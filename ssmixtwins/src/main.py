"""Main module to create SSMIX dataset from CSV files."""

import os
import glob
import math
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import numpy as np
from .preprocessing import validate_csv_files, parse_table
from .objects import generate_random_hospital, generate_random_physician


def create_ssmix(
    source_dir: str,
    output_dir: str,
    max_workers: int = 1,
    already_validated: bool = False,
    encoding: str = "iso2022_jp",
    n_physicians: int = 30,
) -> None:
    """Create SSMIX dataset from CSV files.

    This function reads CSV files from the source directory, validates them, and generates SSMIX dataset files.
    The SSMIX root directory will be created as "<output_dir>/ssmixtwins".
    First, this function validates all the CSV files in the source directory, which may take some time.
    If the CSV files are valid, it proceeds to parse the files and generate SSMIX dataset files.

    Args:
        source_dir (str): Directory containing CSV files.
            Each CSV file must be named as "<start_age:integer from 0 to 120>_<patient sex: either M,F,U,O,or N>_<file_number>.csv".
            'file_number' is an optional number to avoid file name collision. This number is not used in the SSMIX data, therefore, it can be any thing.
            For example, "64_M_1a5d9f7892cd437fb6f9b22bba876dfa.csv".
            Each file must contain a single patient data.
            Each table has columns as follows:

                - "timestamp" (str): Timestamp of the event in "YYYYMMDDHHMMSSFFFFFF" format.
                - "type" (int): The record type. 0 for admissions, 1 for discharges, 2 for outpatient visits, 3 for diagnoses, 4 for prescricription orders, 5 for injection orders, and 6 for laboratory tests.
                - "text" (str): Textual description of the event (e.g., diagnosis name for diagnoses, medication name for prescription orders).
                - "icd10" (str): ICD-10 code for the diagnosis (only for rows type==3, empty otherwise).
                - "mdcdx2" (str): MDCDX2 code for the diagnosis (only for rows type==3, empty otherwise).
                - "provisional" (str): "1" if the diagnosis is provisional. (only for rows type==3, empty otherwise).
                - "hot" (str): HOT drug codes for prescription and injection orders (only for rows type==4 or 5, empty otherwise).
                - "jlac10" (str): JLAC10 code for laboratory tests (only for rows type==6, empty otherwise).
                - "lab_value" (str): Laboratory test value (only for rows type==6, empty otherwise).
                - "unit" (str): Unit of the laboratory test value (only for rows type==6, empty otherwise).
                - "discharge_disposition" (str): Discharge disposition code (only for rows type==1, empty otherwise).

        output_dir (str): Directory to save the SSMIX dataset.
            The SSMIX root directory will be created as "<output_dir>/ssmixtwins".
            Error files may be saved in this directory too.
        max_workers (int): Maximum number of workers for parallel processing.
            Default is 1, which means no parallel processing.
            Because this process takes a long time, it is recommended to set this to a higher value if you are processing many files.
            The appropriate value depends on your CPU and memory resources. Please set an appropriate value so that this does not overwhelm your system.
            For example, processing 1000 CSV files with 10 workers finishes in a short time.
            Setting this to one is ok, but it may take a long time to process many files.
        already_validated (bool): If True, skip validation of CSV files.
            This function first loads all CSV files in the source directory and validates them.
            The function proceeds only if the CSV files are valid.
            You can set this to True if you have already validated the CSV files and want to skip the validation step.
        encoding (str): Encoding to use when saving the files. Default is "iso2022_jp".
        n_physicians (int): Number of random physicians to generate.
            Default is 30, and physicians are randomly selected from the randomly generated physicians throughout the generated data.
            The default value is usually sufficient, but you can increase or decrease this number if you want to.

    Returns:
        None
    """
    # Collect all CSV files in the current directory

    # Files
    csv_files = glob.glob(os.path.join(source_dir, "**", "*.csv"), recursive=True)
    if len(csv_files) == 0:
        print("No CSV files found in the source directory.")
        return

    # Validate CSV files if not already validated
    if not already_validated:
        # Validate CSV files
        all_files_valid = validate_csv_files(
            csv_files=csv_files,
            output_dir=output_dir,  # Errors are saved in this directory, if any
            max_workers=max_workers,
            early_exit_threshold=10,
        )
        if not all_files_valid:
            print(
                "Validation failed. Please fix the errors in the CSV files before proceeding."
            )
            return
    else:
        print("Skipping validation, assuming the CSV files are already validated.")

    # Generate random objects
    random_physicians = [generate_random_physician() for _ in range(n_physicians)]
    random_hospital = generate_random_hospital()

    # Task generator
    def _task_generator(csv_files: str):
        # Patient ID pool
        n_per_level = math.ceil(len(csv_files) ** (1 / 3))
        lv1_ids = [
            f"{x:03}" for x in np.random.choice(999, size=n_per_level, replace=False)
        ]
        lv2_ids = [
            f"{x:03}" for x in np.random.choice(999, size=n_per_level, replace=False)
        ]
        lv3_ids = [
            f"{x:04}" for x in np.random.choice(9999, size=n_per_level, replace=False)
        ]
        patient_id_pool = [
            f"{lv1}{lv2}{lv3}"
            for lv1, lv2, lv3 in itertools.product(lv1_ids, lv2_ids, lv3_ids)
        ]
        patient_id_pool = patient_id_pool[: len(csv_files)]

        # Yield pairs of (csv_file, patient_id)
        for csv_file, patient_id in zip(csv_files, patient_id_pool):
            yield csv_file, patient_id

    task_generator = _task_generator(csv_files)

    # Parse the validated CSV files
    ssmix_root = os.path.join(output_dir, "ssmixtwins")
    os.makedirs(ssmix_root, exist_ok=True)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                parse_table,
                csv_file=csv_file,
                patient_id=patient_id,
                ssmix_root=ssmix_root,
                random_physicians=random_physicians,
                hospital=random_hospital,
                encoding=encoding,
            )
            for csv_file, patient_id in task_generator
        ]

        # Execute the futures
        n_generated = 0
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Parsing CSV files"
        ):
            success = future.result()
            if success:
                n_generated += 1

    print("SSMIX dataset creation completed!")
    print(f"The SSMIX root directory is: {ssmix_root}")
    print(f"There are {n_generated} patients in the root directory.")
