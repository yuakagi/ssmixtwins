import os
import re
import random
import json
from datetime import timedelta, datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd
from ..objects import (
    Physician,
    Admission,
    Hospital,
    generate_random_admission,
    generate_random_patient,
    generate_random_problem,
    generate_random_prescription_order,
    generate_random_injection_order,
    generate_random_injection_component,
    generate_random_lab_result_specimen,
    generate_random_lab_result,
)
from ..file_making import (
    create_adt_00,
    create_adt_12,
    create_adt_22,
    create_adt_52,
    create_ppr_01,
    create_omp_01,
    create_omp_02,
    create_oml_11,
)
from ..tables import udt_0112
from ..utils import to_datetime_anything, generate_random_timedelta
from ..config import BASE_TIMESTAMP_FORMAT

# message_id < 20 characters
# order_number < 15 characters (zfill 15 char)

TABLE_DTYPES = {
    "timestamp": str,  # str, nonnullable
    "type": int,  # int, nonnullable, from 0 to 6
    "text": str,  # str, nullable
    "icd10": str,  # str, nullable
    "mdcdx2": str,  # str,
    "provisional": str,  # str, "1" or ""
    "hot": str,  # str
    "jlac10": str,  # str
    "lab_value": str,  # str
    "unit": str,  # str
    "discharge_disposition": str,  # str
}


def random_message_id_generator(patient_id: str):
    """Generates a random message ID for a patient.
    The message ID is a combination of the patient ID and a random integer.
    The message must be equal to or shorter than 20 characters long.

    NOTE: This does not have to be exactly 20 characters long.
    """
    # First 10 charactersare the patient ID
    for i in range(int(1e11)):
        # NOTE: The patient ID is reversed
        message_id = patient_id[::-1] + str(i)
        yield message_id


def random_order_number(patient_id: str):
    """Generates a random order number for a patient.
    The order number is a combination of the patient ID and a random integer.
    The order number must be exactly 15 characters long.
    """
    for i in range(int(1e6)):
        # NOTE: The patient ID is reversed
        order_number = (patient_id[::-1] + str(i)).zfill(15)
        yield order_number


def draw_random_physician(
    primary_physician: Physician,
    random_physicians: list[Physician],
    admission: Admission | None = None,
) -> Physician:
    """Draws a random physician from the list of physicians.
    If there is an admission, the physician can be the primary physician or the physician of the admission.
    If there is no admission, the physician can only be the primary physician or a random physician from the list.

    Args:
        primary_physician (Physician): The primary physician of the patient.
        random_physicians (list[Physician]): A list of random physicians to choose from.
        admission (Admission | None): The admission object if the patient is admitted, otherwise None.

    Returns:
        Physician: A random physician from the list of physicians.
    """
    # Admission case
    if admission is not None:
        if random.random() < 0.5:
            random_dr = admission.physician
        elif random.random() < 0.5:
            random_dr = primary_physician
        else:
            random_dr = random.choice(random_physicians)
    # No admission case
    else:
        if random.random() < 0.5:
            random_dr = primary_physician
        else:
            random_dr = random.choice(random_physicians)

    return random_dr


def load_table(csv_file: str):
    """
    Loads a CSV file containing source data and returns a DataFrame with the appropriate types.
    The CSV file must be named in the format:
        <start_age>_<sex>_<file_number>.csv
    where:
        - start_age: The initial age of the patient in years, e.g., "30". This must be an integer.
        - sex: Must be one of ["M", "F", "O", "U", "N"], but usually "M" or "F".
        - file_number: An optional number to avoid file name collision.
            This number is not used in the SSMIX data, therefore, it can be any string.
            UUID is handy for this purpose, but you can use any string.

    Args:
        csv_file (str): The path to the CSV file to be loaded.

    Returns:
        tuple: A tuple containing:
            - df (pd.DataFrame): The loaded DataFrame with the appropriate types.
            - start_age (str): The first age of the patient as a string, e.g., "30".
            - sex (str): The patient sex, one of ["M", "F", "O", "U", "N"].
    """
    # Type checking
    # Load
    df = pd.read_csv(csv_file, dtype=str).fillna("")
    df = df.astype(TABLE_DTYPES)
    # Strip
    for k, v in TABLE_DTYPES.items():
        if v == str:
            df[k] = df[k].str.strip()
    # Ensure sorting
    df["timestamp_dt"] = pd.to_datetime(
        df["timestamp"], format=BASE_TIMESTAMP_FORMAT, errors="coerce"
    )
    df = df.sort_values(
        by=["timestamp_dt", "type"], ascending=[True, True]
    ).reset_index(drop=True)
    df = df.drop(columns=["timestamp_dt"])  # Drop the temporary column
    # Organize columns
    df = df[list(TABLE_DTYPES.keys())]
    # Fill nan
    for col, dtype in TABLE_DTYPES.items():
        if dtype == str:
            df[col] = (
                df[col].fillna("").astype(str)
            )  # Fill NaN with empty string for str columns

    # Load parameters from the file name
    file_name_parts = os.path.basename(csv_file).replace(".csv", "").split("_")
    start_age = file_name_parts[0]  # e.g., "30"
    sex = file_name_parts[1]  # e.g., "M" or "F"

    return df, int(start_age), sex


def parse_table(
    csv_file: str,
    patient_id: str,
    ssmix_root: str,
    random_physicians: list[Physician],
    hospital: Hospital,
    encoding: str,
) -> bool:
    """Parses a CSV file containing source data and generates SSMIX messages based on the data.
    The CSV file must be named in the format:
        <start_age>_<sex>_<file_number>.csv

    Args:
        csv_file (str): The path to the CSV file to be parsed.
        patient_id (str): The patient ID, which is a 10-character string.
        ssmix_root (str): The root directory for SSMIX files.
        random_physicians (list[Physician]): A list of random physicians to choose from.
        hospital (Hospital): The hospital object containing hospital details.
        encoding (str): The encoding to use when saving the file.

    Returns:
        bool: True if the file was processed successfully, False if the file is empty.
    """

    # Load and clean source data
    df, start_age, sex = load_table(csv_file)
    # Generators
    message_id_gen = random_message_id_generator(patient_id)
    order_number_gen = random_order_number(patient_id)
    # Handling date of birth and timestamps
    all_dates = pd.to_datetime(df["timestamp"], format=BASE_TIMESTAMP_FORMAT).dt.floor(
        "D"
    )
    oldest_date = all_dates.min()
    latest_date = all_dates.max()
    start_age_td = timedelta(days=int(start_age * 365.25))
    dob_dt = (oldest_date - start_age_td).date()
    dob = dob_dt.strftime("%Y%m%d")  # Convert to YYYYMMDD format
    dob_roudned_dt = datetime.strptime(dob, "%Y%m%d")
    latest_age = int((latest_date - dob_roudned_dt).days / 365.25)

    # Init objects
    patient = generate_random_patient(
        patient_id=patient_id,
        latest_date=latest_date.strftime("%Y%m%d"),  # Latest date in YYYYMMDD format
        age=latest_age,
        dob=dob,
        sex=sex,
        n_insurance=1,
    )
    primary_physician = random.choice(random_physicians)
    admission = None

    # Check if the DataFrame is empty
    if len(df) == 0:
        print(f"Warning: No data found in {csv_file}. Skipping file.")
        return False

    # Proceed with the DataFrame otherwise.
    else:
        # Iterate through types and timestamps, pasing from old to new
        grouped = df.groupby(["timestamp", "type"])
        current_date = ""
        for (timestamp, record_type), t in grouped:
            # Check for ADT-12 indications
            # (Place ADT-12 messages when the date changes, and the patient is not admitted)
            if current_date != timestamp[:8]:
                # Update current date
                current_date = timestamp[:8]
                # If the patient is not admitted, create an ADT-12 message on a date change
                if admission is None:
                    # Update primary physician (10% chance)
                    if random.random() < 0.1:
                        primary_physician = random.choice(random_physicians)
                    # Generate a visit time (30 to 180 minutes before the timestamp)
                    timestamp_dt = to_datetime_anything(timestamp)
                    visit_time_dt = timestamp_dt - generate_random_timedelta(
                        min_minutes=30, max_minutes=180
                    )
                    visit_time = visit_time_dt.strftime(BASE_TIMESTAMP_FORMAT)
                    # Create ADT-12 message
                    create_adt_12(
                        ssmix_root=ssmix_root,
                        visit_time=visit_time,
                        message_id=next(message_id_gen),
                        patient=patient,
                        primary_physician=primary_physician,
                        departmet_code=primary_physician.department_code,
                        requester_order_number=next(order_number_gen),
                        encoding=encoding,
                    )

            # Admission
            if record_type == 0:
                # Update admission
                admission = generate_random_admission(
                    physician=random.choice(random_physicians),
                )
                # Update primary physician (50% chance)
                if random.random() < 0.5:
                    primary_physician = random.choice(random_physicians)
                # Create ADT-00 message
                create_adt_22(
                    ssmix_root=ssmix_root,
                    admission_time=timestamp,
                    message_id=next(message_id_gen),
                    patient=patient,
                    primary_physician=primary_physician,
                    admission=admission,
                    requester_order_number=next(order_number_gen),
                    encoding=encoding,
                )
            # Discharge
            elif record_type == 1:
                # Create ADT-52 message
                create_adt_52(
                    ssmix_root=ssmix_root,
                    discharge_time=timestamp,
                    discharge_disposition=t["discharge_disposition"].iloc[0],
                    message_id=next(message_id_gen),
                    patient=patient,
                    primary_physician=primary_physician,
                    admission=admission,
                    requester_order_number=next(order_number_gen),
                    encoding=encoding,
                )
                # Delete admission
                # NOTE: Ensure this comes after the ADT-52 message creation
                admission = None

            # 📝 ===== Diagnosis =====
            elif record_type == 2:
                # Determine enterer and requester
                if random.random() < 0.7:
                    # 70% chance to use primary physician as both enterer and requester
                    requester_enterer = primary_physician
                else:
                    # 30% chance to use a random physician as enterer and requester
                    requester_enterer = draw_random_physician(
                        primary_physician, random_physicians, admission
                    )
                # Problems
                problems = []
                # Order number
                # NOTE: You should use the same order number for all problems saved in the same file.
                requester_order_number = next(order_number_gen)
                filler_order_number = next(order_number_gen)
                for _, row in t.iterrows():
                    # Handling irregular or missing codes & names
                    dx_code = row["mdcdx2"]
                    if dx_code == "":
                        dx_code = "99999999"  # Set default
                        dx_code_system = "99XYZ"
                    else:
                        dx_code_system = "MDCDX2" if len(dx_code) == 8 else "99XYZ"
                    dx_name = row["text"]
                    if dx_name == "":
                        dx_name = "名称未設定"  # Set default

                    # Generate a problem instance
                    problem = generate_random_problem(
                        dx_code=dx_code,
                        dx_name=dx_name,
                        # MDCDX2 codes are 8 characters long.
                        dx_code_system=dx_code_system,
                        prb_instance_id=next(order_number_gen),
                        icd10_code=row["icd10"],
                        icd10_name="",  # ICD-10 name is not used currently
                        provisional=row["provisional"],  # True or False
                        is_admitted=admission is not None,
                        action_time=row["timestamp"],
                        requester_order_number=requester_order_number,
                        filler_order_number=filler_order_number,
                        enterer=requester_enterer,
                        requester=requester_enterer,
                    )
                    problems.append(problem)
                # Create ADT-00 message
                create_ppr_01(
                    ssmix_root=ssmix_root,
                    message_id=next(message_id_gen),
                    patient=patient,
                    hospital=hospital,
                    problems=problems,  # <- Must use the same ORC-2 for consistent naming
                    encoding=encoding,
                )

            # 💊 ===== Prescription =====
            elif record_type == 3:
                # Determine enterer and requester
                if random.random() < 0.7:
                    # 70% chance to use primary physician as both enterer and requester
                    requester_enterer = primary_physician
                else:
                    # 30% chance to use a random physician as enterer and requester
                    requester_enterer = draw_random_physician(
                        primary_physician, random_physicians, admission
                    )
                # Orders
                orders = []
                requester_order_number = next(order_number_gen)
                filler_order_number = next(order_number_gen)
                start_time = timestamp
                # NOTE: Transaction time should be the same for all orders in the same file.
                #       currently, we set start_time as the transaction time. But this is not realistic.
                transaction_time = start_time
                for rp_no, (_, row) in enumerate(t.iterrows(), start=1):
                    # Handling missing drug codes or names
                    drug_code = row["hot"]
                    if drug_code == "":
                        drug_code = "999999"  # Set default
                        drug_code_system = "99XYZ"
                    else:
                        drug_code_system = "HOT" + str(len(drug_code))
                    drug_name = row["text"]
                    if drug_name == "":
                        drug_name = "名称未設定"  # Set default

                    # Generate a random prescription order
                    generated_order = generate_random_prescription_order(
                        drug_code=drug_code,
                        drug_name=drug_name,
                        drug_code_system=drug_code_system,
                        prescription_number=requester_order_number,  # Use the same order number for all prescriptions in the same files
                        start_time=start_time,
                        transaction_time=transaction_time,
                        recipe_number=str(rp_no).zfill(2),  # Zero-padded to 2 digits
                        order_admin_number="001",  # Always "001" for now
                        requester_order_number=requester_order_number,
                        filler_order_number=filler_order_number,
                        is_admitted=admission is not None,
                        enterer=requester_enterer,
                        requester=requester_enterer,
                    )
                    orders.append(generated_order)
                # Create OMP-01 message
                create_omp_01(
                    ssmix_root=ssmix_root,
                    message_id=next(message_id_gen),
                    patient=patient,
                    hospital=hospital,
                    admission=admission,
                    primary_physician=primary_physician,
                    outpatient_department_code=primary_physician.department_code,
                    orders=orders,  # <- Must use the same ORC-2 for consistent naming
                    encoding=encoding,
                )

            # 💉===== Injection =======
            elif record_type == 4:
                # Determine enterer and requester
                if random.random() < 0.7:
                    # 70% chance to use primary physician as both enterer and requester
                    requester_enterer = primary_physician
                else:
                    # 30% chance to use a random physician as enterer and requester
                    requester_enterer = draw_random_physician(
                        primary_physician, random_physicians, admission
                    )
                # Separate orders artificially
                # NOTE: In SSMIX2, there are multiple components under one ROC, like saline+antibiotics
                #       It is difficult to completely simulate this, therefore, we separate one order into
                #       artificial fragments.
                # Shuffle the table first
                t_shuffled = t.sample(frac=1, replace=False).reset_index(drop=True)
                n_components = len(t_shuffled)
                # Separate the table into random number of components
                t_chunks = []
                idx = 0
                if n_components >= 3:
                    max_max_pick = n_components // 3
                    while idx < n_components:
                        # Conunt reamaining components
                        remaining = n_components - idx
                        # Determine how many components to pick
                        max_pick = min(remaining, max_max_pick)
                        n_pick = random.randint(1, max_pick)
                        end_idx = min(idx + n_pick, n_components)
                        # Create a chunk
                        chunk = t_shuffled.iloc[idx:end_idx].reset_index(drop=True)
                        # Add the chunk to the list
                        t_chunks.append(chunk)
                        # Update the index
                        idx = end_idx
                else:
                    # If there are less than 3 components, just use the whole table
                    t_chunks = [t_shuffled]

                # Create all orders
                orders = []
                requester_order_number = next(order_number_gen)
                filler_order_number = next(order_number_gen)
                start_time = timestamp
                # NOTE: Transaction time should be the same for all orders in the same file.
                #       currently, we set start_time as the transaction time. But this is not realistic.
                transaction_time = start_time
                for rp_no, comp_table in enumerate(t_chunks, start=1):
                    # Gnerate components
                    components = []
                    for _, row in comp_table.iterrows():
                        # Handling missing component codes or names
                        component_code = row["hot"]
                        if component_code == "":
                            component_code = "999999"  # Set default
                            component_code_system = "99XYZ"
                        else:
                            component_code_system = "HOT" + str(len(component_code))
                        component_name = row["text"]
                        if component_name == "":
                            component_name = "名称未設定"  # Set default
                        # Generate a random injection order
                        component = generate_random_injection_component(
                            component_code=component_code,
                            component_name=component_name,
                            component_code_system=component_code_system,
                        )
                        components.append(component)

                    # Generate an injection order
                    order = generate_random_injection_order(
                        prescription_number=requester_order_number,  # Use the same order number for all injections in the same files
                        start_time=start_time,
                        transaction_time=transaction_time,
                        recipe_number="01",  # Always "01" for now
                        order_admin_number=str(rp_no).zfill(3),
                        requester_order_number=requester_order_number,
                        filler_order_number=filler_order_number,
                        is_admitted=admission is not None,
                        enterer=requester_enterer,
                        requester=requester_enterer,
                        components=components,
                    )
                    orders.append(order)
                # Create OMP-02 message
                create_omp_02(
                    ssmix_root=ssmix_root,
                    message_id=next(message_id_gen),
                    patient=patient,
                    hospital=hospital,
                    admission=admission,
                    primary_physician=primary_physician,
                    outpatient_department_code=primary_physician.department_code,
                    orders=orders,  # <- Must use the same ORC-2 for consistent naming
                    encoding=encoding,
                )

            # 🧪 ===== Lab Results ====
            elif record_type == 5:
                # Determine enterer and requester
                if random.random() < 0.7:
                    # 70% chance to use primary physician as both enterer and requester
                    requester_enterer = primary_physician
                else:
                    # 30% chance to use a random physician as enterer and requester
                    requester_enterer = draw_random_physician(
                        primary_physician, random_physicians, admission
                    )
                # Specimens
                valid_jlac10 = t["jlac10"].str.len() == 17
                t["specimen"] = "990"  # Defaults to 'その他の検体' in JLAC10
                t.loc[valid_jlac10, "specimen"] = t.loc[
                    valid_jlac10, "jlac10"
                ].str.slice(9, 12)
                # Orders
                requester_order_number = next(order_number_gen)
                filler_order_number = next(order_number_gen)
                specimens = []
                for specimen_code, specimen_table in t.groupby("specimen"):
                    # Iterate through each result with the same specimen code
                    lab_results = []
                    for _, row in specimen_table.iterrows():
                        # Generate a random lab result
                        lab_result = generate_random_lab_result(
                            observation_sub_id="",  # Currently not used
                            observation_code=row["jlac10"],
                            observation_name=row["text"],
                            observation_code_system=(
                                "JC10" if len(row["jlac10"]) == 17 else "99XYZ"
                            ),
                            observation_value=row["lab_value"],
                            unit=row["unit"],
                        )
                        lab_results.append(lab_result)
                    # Specimen
                    specimen = generate_random_lab_result_specimen(
                        specimen_id=next(order_number_gen),
                        specimen_code=specimen_code,
                        sampled_time=timestamp,
                        requester_order_number=requester_order_number,
                        filler_order_number=filler_order_number,
                        is_admitted=admission is not None,
                        enterer=requester_enterer,
                        requester=requester_enterer,
                        results=lab_results,
                    )
                    specimens.append(specimen)

                # Create OML-11 message
                create_oml_11(
                    ssmix_root=ssmix_root,
                    message_id=next(message_id_gen),
                    patient=patient,
                    hospital=hospital,
                    admission=admission,
                    primary_physician=primary_physician,
                    outpatient_department_code=primary_physician.department_code,
                    specimens=specimens,  # <- Must use the same ORC-2 for consistent naming
                    encoding=encoding,
                )

        # ===== Demographics =====
        # NOTE: This should come after all other messages, because the latest admission status is used.
        create_adt_00(
            ssmix_root=ssmix_root,
            # NOTE: Uset the final timestamp from the loop, this is intended.
            # pylint: disable=undefined-loop-variable
            last_updated=timestamp,
            message_id=next(message_id_gen),
            patinet=patient,
            primary_physician=primary_physician,
            admission=admission,  # This can be None if the patient is not admitted
            encoding=encoding,
        )
    return True


def _validate_table(
    csv_file: str,
):
    """Validates a CSV file containing source data."""
    status = {"csv_file": csv_file}

    # Validate file naming
    # NOTE: File name must be <age>_<sex>_<file_number>.csv, age is 0-120.
    pattern = r"^(?:[0-9]|[1-9][0-9]|1[01][0-9]|120)_[MFOUN]_[a-zA-Z0-9\-]+\.csv$"
    file_name = os.path.basename(csv_file)
    if not re.match(pattern, file_name):
        status["file_name_format_error"] = True

    # Try loading the CSV file
    try:
        # Load
        df = pd.read_csv(csv_file, dtype=str).fillna("")
    except Exception:
        status["csv_not_readable"] = True
        # Do not proceed
        return status
    # Check columns
    for col in TABLE_DTYPES.keys():
        if col not in df.columns:
            status["table_does_not_have_required_columns"] = True
            # Do not proceed if there is a missing column
            return status
    # Convert types
    conversion_errors = False
    for col, dtype in TABLE_DTYPES.items():
        try:
            df[col] = df[col].astype(dtype)
            if dtype == str:
                df[col] = df[col].str.strip()
                df[col] = df[col].fillna(
                    ""
                )  # Fill NaN with empty string for str columns
        except ValueError:
            status[f"all_values_in_{col}_column_must_be_{dtype}_data_type"] = True
            conversion_errors = True
    if conversion_errors:
        # Do not proceed if there is an error
        return status
    # Timestamp
    if (df["timestamp"] == "").any():
        status["table_must_not_contain_missing_timestamp(s)"] = True
    try:
        _ = pd.to_datetime(
            df["timestamp"], format=BASE_TIMESTAMP_FORMAT, errors="raise"
        )
    except ValueError:
        status["table_contains_irregular_timestamp(s)"] = True
    # Types
    all_types = set(df["type"].unique().tolist())
    valid_types = (0, 1, 2, 3, 4, 5)
    if df["type"].isnull().any():
        status["table_must_not_contain_missing_type(s)"] = True
    if not all_types.issubset(valid_types):
        status["table_contains_invalid_type(s)"] = True
    # Discharge
    discharge_table = df[df["type"] == 1]  # Discharge type
    if len(discharge_table) > 0:
        if (discharge_table["discharge_disposition"] == "").any():
            status["table_must_not_contain_missing_discharge_disposition(s)"] = True
        if not set(discharge_table["discharge_disposition"].unique().tolist()).issubset(
            set(udt_0112.keys())
        ):
            status["discharge_disposition_column_contains_irregular_value(s)"] = True
    # Diagnosis
    diagnosis_table = df[df["type"] == 2]  # Diagnosis type
    if len(diagnosis_table) > 0:
        if (~diagnosis_table["provisional"].isin(["1", ""])).any():
            status["provisional_column_must_be_1_or_empty"] = True
    # Prescription
    prescription_table = df[df["type"] == 3]  # Prescription type
    if len(prescription_table) > 0:
        # NOTE: Add validation logics if needed
        pass
    # Injection
    injection_table = df[df["type"] == 4]  # Injection type
    if len(injection_table) > 0:
        # NOTE: Add validation logics if needed
        pass
    # Lab results
    lab_results_table = df[df["type"] == 5]  # Lab results type
    if len(lab_results_table) > 0:
        if (lab_results_table["jlac10"] == "").any():
            status["lab_results_data_must_not_contain_missing_jlac10_code(s)"] = True
        if (lab_results_table["lab_value"] == "").any():
            status["lab_results_data_must_not_contain_missing_lab_value(s)"] = True
        if (lab_results_table["jlac10"].str.len() != 17).any():
            status["jlac10_code_must_be_17_characters_long_without_hyphens"] = True

    # Admissin-discharge consistency
    if (df["type"] == 0).any() and (df["type"] == 1).any():
        # Check if all admissions and discharges alternate (Ending without discharge is allowed)
        admission_discharge = df[df["type"].isin([0, 1])]
        expected_next = 0  # Expecting admission first
        for _, row in admission_discharge.iterrows():
            if row["type"] != expected_next:
                if expected_next == 0:
                    status["admission_discharge_sequence_error"] = True
                    break
            # Update expected next type
            expected_next = 1 if expected_next == 0 else 0

    return status


def validate_csv_files(
    csv_files: list[str],
    output_dir: str,
    max_workers: int = 1,
    early_exit_threshold: int = 10,
) -> bool:
    """Validates a list of CSV files containing source data"""

    # Validate files
    print(f"Found {len(csv_files)} CSV files in the source directory.")
    print("Validating CSV files...")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_validate_table, csv_file) for csv_file in csv_files]
        all_errors = {}
        n_errors = 0
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Validating CSV files"
        ):
            status = future.result()
            if status:
                # Get the file name from the status
                file_name = status.pop("csv_file")
                # Detect errors
                for key, value in status.items():
                    if value:
                        if key not in all_errors:
                            all_errors[key] = []
                        all_errors[key].append(file_name)
                        n_errors += 1
            # Early exit if the number of errors exceeds the threshold
            if n_errors >= early_exit_threshold:
                print(f"Early exit: {n_errors} errors found. Stopping validation.")
                break

        # Save errors a JSON file
        if len(all_errors) > 0:
            print(f"Found {n_errors} errors in the CSV files.")
            json_path = os.path.join(output_dir, "validation_errors.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    all_errors,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )
            print("Type of errors found:")
            for error_type in all_errors:
                print(" ".join(error_type.split("_")).capitalize())
            print(f"Validation errors are saved to {os.path.abspath(json_path)}")
            print(
                "Please see the file and fix the errors in the CSV files before proceeding with the SSMIX file creation."
            )
            return False
        else:
            print("No errors found in the CSV files.")
            print("Proceed with the SSMIX creation process.")
            return True
