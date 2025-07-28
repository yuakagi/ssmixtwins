import re
from datetime import timedelta
from typing import Literal
import random
from faker import Faker
import numpy as np
from ..random_data import RANDOM_ABO_BLOOD_TYPES, RANDOM_ALLERGIES
from ..utils import (
    format_timestamp,
    normalize_and_validate_postal_code,
    to_datetime_anything,
    generate_random_address,
    generate_random_phone,
)
from ..tables import udt_0001, jhsd_0001, jhsd_0001_ext, jhsd_0002, udt_0063, udt_0127
from ..config import BASE_TIMESTAMP_FORMAT


class Allergy:
    """Allergy object for SSMIX dummy data generation."""

    def __init__(
        self,
        allergy_type_code: str,
        allergen_code: str,
        allergen_name: str,
        allergen_code_system: str,
    ):
        """Initializes the Allergy object with the provided attributes.

        Args:
            allergy_type_code (str): The code for the allergy type, must be one of udt_0127.
            allergen_code (str): The code for the allergen, e.g., '99XYZ' for local codes.
            allergen_name (str): The name of the allergen, e.g., 'ペニシリン'.
            allergen_code_system (str): The code system for the allergen, e.g., 'HOT9' for drugs, 'JLAC10' for food.
        """

        # Validate and clean the inputs
        assert (
            allergy_type_code in udt_0127
        ), "allergy_type_code must be one of udt_0127."
        assert allergen_code != "", "allergen_code must not be empty."
        assert allergen_name != "", "allergen_name must not be empty."
        assert allergen_code_system != "", "allergen_code_system must not be empty."
        # Set attributes
        self.allergy_type_code = allergy_type_code
        self.allergen_code = allergen_code
        self.allergen_name = allergen_name
        self.allergen_code_system = allergen_code_system


class Insurance:
    """Insurance object for SSMIX dummy data generation."""

    def __init__(
        self,
        insurance_plan_code: str,
        insurance_number: str,
        insurance_plan_effective_date: str,
        insurance_plan_expiration_date: str,
        insurance_plan_type: str,
        insurance_relationship: str,
        insurance_company_name: str,
    ):
        """Initializes the Insurance object with the provided attributes.

        Args:
            insurance_plan_code (str): The code for the insurance plan, must be one of jhsd_0001.
            insurance_number (str): The insurance number, 6 digits for 国民健康保険 (C0), 8 digits for other plans.
            insurance_plan_effective_date (str): The effective date of the insurance plan in 'YYYYMMDD' format.
            insurance_plan_expiration_date (str): The expiration date of the insurance plan in 'YYYYMMDD' format.
            insurance_plan_type (str): The type of the insurance plan, must be one of jhsd_0002 for public expense insurance (PE).
            insurance_relationship (str): The relationship of the insured person, must be one of udt_0063.
            insurance_company_name (str): The name of the insurance company, must not be empty for certain insurance plans.
        """

        # Insurance validation below
        # NOTE: Insurance logics are complex, be careful when modifying.
        assert (
            insurance_plan_code in jhsd_0001
        ), f"insurance_plan_code must be one of {list(jhsd_0001.keys())}, got '{insurance_plan_code}'."
        if insurance_plan_code == "C0":
            # 国民健康保険 (National Health Insurance) does not have the first 2 digits of the insurance number
            assert (
                len(insurance_number) == 6
            ), "insurance_number must be 6 digits long for 国民健康保険 (C0)."
        else:
            # Other insurance plans have 8-digit insurance number
            assert (
                len(insurance_number) == 8
            ), "insurance_number must be 8 digits long for other insurance plans than C0 (国民健康保険)."
            first_two = insurance_plan_code[:2]
            assert (
                first_two in jhsd_0001_ext
            ), f"insurance_plan_code must start with one of {list(jhsd_0001_ext.keys())}, got '{insurance_plan_code}'."
        insurance_classification = jhsd_0001[insurance_plan_code]["classification"]
        insurance_class_name = jhsd_0001[insurance_plan_code]["name"]
        if insurance_classification == "PE":
            assert (insurance_plan_type != "") and (
                insurance_plan_type in jhsd_0002
            ), "insurance_plan_type must be provided for public expense insurance (PE) and must be one of jhsd_0002."
        if insurance_classification in ["MI", "PE", "TI", "PS", "PI", "OE", "OT"]:
            assert (
                insurance_company_name != ""
            ), "insurance_company_name must not be empty for insurance plans MI, PE, TI, PS, PI, OE, OT."
        if insurance_relationship != "":
            assert (
                insurance_relationship in udt_0063
            ), f"insurance_relationship must be one of {list(udt_0063.keys())}, got '{insurance_relationship}'."
        # Timestamp validation
        insurance_plan_effective_date = format_timestamp(
            insurance_plan_effective_date, "YYYYMMDD", allow_null=True
        )  # <- Format is not specified, but the max length is 8, which essentially means YYYYMMDD.
        insurance_plan_expiration_date = format_timestamp(
            insurance_plan_expiration_date, "YYYYMMDD", allow_null=True
        )  # <- Format is not specified, but the max length is 8, which essentially means YYYYMMDD.
        # Set attributes
        self.insurance_plan_code = insurance_plan_code
        self.insurance_number = insurance_number
        self.insurance_plan_effective_date = insurance_plan_effective_date
        self.insurance_plan_expiration_date = insurance_plan_expiration_date
        self.insurance_plan_type = insurance_plan_type
        self.insurance_relationship = insurance_relationship
        self.insurance_classification = insurance_classification
        self.insurance_class_name = insurance_class_name
        self.insurance_company_name = insurance_company_name


class Patient:
    """Patient object for SSMIX dummy data generation."""

    def __init__(
        self,
        patient_id: str,
        dob: str,
        sex: Literal["F", "M", "O", "U"],
        patient_first_name: str,
        patient_first_name_kana: str,
        patient_last_name: str,
        patient_last_name_kana: str,
        patient_postal_code: str,
        patient_address: str,
        home_phone: str,
        work_place: str,
        work_phone: str,
        abo_blood_type: Literal["A", "B", "AB", "O", ""],
        rh_blood_type: Literal["+", "-", ""],
        height: str,
        weight: str,
        allergies: list[Allergy],
        insurances: list[Insurance],
        patient_last_name_roman: str = "",  # Not implemented
        patient_first_name_roman: str = "",  # Not implemented
    ):
        """Initializes the Patient object with the provided attributes.

        Args:
            patient_id (str): The unique identifier for the patient, must be alphanumeric and 6-250 characters long.
            dob (str): The date of birth in 'YYYYMMDD' format.
            sex (Literal["F", "M", "O", "U"]): The patient sex.
            patient_first_name (str): The first name of the patient.
            patient_first_name_kana (str): The first name in Kana.
            patient_last_name (str): The last name of the patient.
            patient_last_name_kana (str): The last name in Kana.
            patient_postal_code (str): The postal code of the patient, must be a valid postal code.
            patient_address (str): The address of the patient, must be 235 characters or less.
            home_phone (str): The home phone number of the patient, must be 250 characters or less.
            work_place (str): The workplace of the patient, must be 250 characters or less.
            work_phone (str): The work phone number of the patient, must be 250 characters or less.
            abo_blood_type (Literal["A", "B", "AB", "O", ""]): The ABO blood type of the patient, must be one of 'A', 'B', 'AB', 'O', or empty.
            rh_blood_type (Literal["+", "-", ""]): The Rh blood type of the patient, must be one of '+', '-', or empty.
            height (str): The height of the patient in cm, must be a digit between 30 and 300 cm.
            weight (str): The weight of the patient in kg, must be a digit between 1 and 500 kg.
            allergies (list[Allergy]): A list of Allergy objects representing the patient's allergies.
            insurances (list[Insurance]): A list of Insurance objects representing the patient's insurance information.
            patient_last_name_roman (str): The last name in Roman characters, not implemented.
            patient_first_name_roman (str): The first name in Roman characters, not implemented.
        """

        # Validate and clean the inputs
        assert re.match(
            r"^\w{6,250}$", patient_id
        ), "patient_id must be alphanumeric and 6-250 characters long."
        assert sex in udt_0001, "Invalid patient sex."
        assert (
            len(patient_first_name)
            + len(patient_last_name)
            + len(patient_first_name_kana)
            + len(patient_last_name_kana)
            < 230
        ), "Patient name is too long. It must be less than 230 characters in total."
        postal_valid, patient_postal_code = normalize_and_validate_postal_code(
            patient_postal_code
        )
        assert postal_valid, "Invalid patient_postal_code must be a valid postal code."
        assert (
            len(patient_address) <= 235
        ), "patient_address should be 235 characters or less."
        assert len(home_phone) <= 250, "home_phone must be 250 characters or less."
        assert len(work_phone) <= 250, "work_phone must be 250 characters or less."
        assert len(work_place) <= 250, "work_place must be 250 characters or less."
        if abo_blood_type != "":
            assert abo_blood_type in [
                "A",
                "B",
                "AB",
                "O",
            ], "abo_blood_type must be one of 'A', 'B', 'AB', 'O', or empty."
        if rh_blood_type != "":
            assert rh_blood_type in [
                "+",
                "-",
            ], "rh_blood_type must be one of '+', '-', or empty."
        if height != "":
            try:
                height_float = float(height)
                assert (
                    0 <= height_float <= 300
                ), "height must be a digit between 30 and 300 cm."
            except ValueError as e:
                raise ValueError(f"Height must be a number, but got '{height}'.") from e
        if weight != "":
            try:
                weight_float = float(weight)
                assert (
                    0 <= weight_float <= 500
                ), "weight must be a digit between 1 and 500 kg."
            except ValueError as e:
                raise ValueError(f"Weight must be a number, but got '{weight}'.") from e
        if len(allergies) > 0:
            assert isinstance(
                allergies, list
            ), "allergies must be a list of Allergy objects."
            for allergy in allergies:
                assert isinstance(
                    allergy, Allergy
                ), "allergies must contain Allergy objects."

        # Format
        dob = format_timestamp(dob, "YYYYMMDD", allow_null=False)

        # Set attributes
        self.patient_id = patient_id
        self.dob = dob
        self.sex = sex
        self.patient_first_name = patient_first_name
        self.patient_first_name_kana = patient_first_name_kana
        self.patient_first_name_roman = patient_first_name_roman
        self.patient_last_name = patient_last_name
        self.patient_last_name_kana = patient_last_name_kana
        self.patient_last_name_roman = patient_last_name_roman
        self.patient_postal_code = patient_postal_code
        self.patient_address = patient_address
        self.home_phone = home_phone
        self.work_place = work_place
        self.work_phone = work_phone
        self.abo_blood_type = abo_blood_type  # e.g., "A", "B", "AB", "O", ""
        self.rh_blood_type = rh_blood_type  # e.g., "+", "-",
        self.height = height  # Height in cm
        self.weight = weight  # Weight in kg
        self.allergies = allergies  # List of Allergy objects
        self.insurances = insurances  # List of Insurance objects


def generate_random_allergies(
    n_allergy_list: list[int],
    weitghs: list[float],
) -> list[Allergy]:
    """Generates an allergy table from the provided DataFrame.

    Args:
        n_allergy_list (list[int]): A list of integers representing the number of allergies to generate.
        weitghs (list[float]): A list of weights corresponding to the number of allergies.
    Returns:
        pd.DataFrame: A DataFrame containing the generated allergy data with the following columns:
            - 'allergy_type_code': The code for the allergy type.
            - 'allergen_code': The code for the allergen.
            - 'allergen_name': The name of the allergen.
            - 'allergen_code_system': The code system for the allergen.
    """
    # Determine the number of allergies to generate
    n_allergy = np.random.choice(n_allergy_list, p=weitghs)
    # Draw random allergies from the RANDOM_ALLERGIES
    allergies = []
    for _ in range(n_allergy):
        allergy = random.choice(RANDOM_ALLERGIES)
        allergies.append(
            Allergy(
                allergy_type_code=allergy["allergy_type_code"],
                allergen_code=allergy["allergen_code"],
                allergen_name=allergy["allergen_name"],
                allergen_code_system=allergy["allergen_code_system"],
            )
        )

    return allergies


def generate_random_insurances(
    current_date: str,  # Current date for insurance dates
):
    """Generates a random insurance profile for a patient.
    Args:
        current_date (str): The current date to use for generating insurance dates.
    Returns:
        Insurance: An Insurance object with randomly generated attributes.
    """
    # === Insurance details ===
    # Convert current_date to datetime object
    current_date = to_datetime_anything(current_date)

    # Insurance plan code
    insurance_relationship = "SEL"  # Patient themselves is set always
    if random.random() < 0.50:
        insurance_plan_code = "C0"  # 50% C0, 国民健康保険 (National Health Insurance)
    else:
        # Otherwise, we choose from 法別番号 (stored in jhsd_0001_ext)
        insurance_plan_code = random.choice(list(jhsd_0001_ext.keys()))

    # 国民健康保険
    if insurance_plan_code == "C0":
        # 国民健康保険 does not have the first 2 digits of the insurance number
        insurance_number = str(
            random.randint(100000, 999999)
        )  # Random 6-digit insurance number
    # Other insurance plans
    else:
        # For other insurance plans, 8-digit insurance number is used
        first_two = insurance_plan_code  # First two is the insurance plan code, if you use 法別番号
        last_six = str(random.randint(100000, 999999))
        insurance_number = f"{first_two}{last_six}"  # 8-digit insurance
    # Insurance classification, name are obtained from jhsd_0001
    insurance_classification = jhsd_0001[insurance_plan_code]["classification"]
    # Insurance plan type
    if insurance_classification == "PE":
        # NOTE: insurance_plan_type is currently random, therefore it may be inconsistent with patient address.
        insurance_plan_type = random.choice(list(jhsd_0002.keys()))
    else:
        insurance_plan_type = ""  # Not applicable for other insurance plans
    # Insurance company name
    if insurance_classification in ["MI", "PE", "TI", "PS", "PI", "OE", "OT"]:
        # NOTE: Currently, we use a fixed value for this value, for simplicity.
        insurance_company_name = "保険者の名称(仮)"
    else:
        insurance_company_name = ""

    # Insurance plan effective and expiration dates
    insurance_plan_effective_date = current_date.strftime(
        BASE_TIMESTAMP_FORMAT
    )  # Current date
    insurance_plan_expiration_date = (current_date + timedelta(days=365 * 1)).strftime(
        BASE_TIMESTAMP_FORMAT
    )  # 1 years later

    # Create an Insurance object
    insurance = Insurance(
        insurance_plan_code=insurance_plan_code,
        insurance_number=insurance_number,
        insurance_plan_effective_date=insurance_plan_effective_date,
        insurance_plan_expiration_date=insurance_plan_expiration_date,
        insurance_plan_type=insurance_plan_type,
        insurance_relationship=insurance_relationship,
        insurance_company_name=insurance_company_name,
    )
    return insurance


def generate_random_patient(
    patient_id: str,
    dob: str,
    age: str,
    latest_date: str,
    sex: Literal["F", "M", "O", "U"],
    n_insurance: int = 1,
) -> Patient:
    """Generates a random patient profile with various attributes.

    Args:
        patient_id (str): The unique identifier for the patient.
        age (str): The age of the patient in years.
        latest_date (str): The latest date to use for generating timestamps, YYYYMMDD.
        sex (Literal["F", "M", "O", "U"]): The patient sex.
        dob (str): The date of birth in 'YYYYMMDD' format.
        n_insurance (int): The number of insurance plans to generate for the patient. Default

    Returns:
        Patient: A Patient object with randomly generated attributes.
    """
    # Timestamp and dob
    age = int(age)  # Convert age to integer

    # Create a Faker instance
    fake = Faker("ja_JP")  # Set the locale to Japanese (ja_JP)
    # Name
    last_name_pair = fake.last_name_pair()
    if sex == "F":
        first_name_pair = fake.first_name_female_pair()
    else:
        first_name_pair = fake.first_name_male_pair()
    patient_first_name = first_name_pair[0]
    patient_first_name_kana = first_name_pair[1]
    patient_first_name_roman = first_name_pair[2]
    patient_last_name = last_name_pair[0]
    patient_last_name_kana = last_name_pair[1]
    patient_last_name_roman = last_name_pair[2]
    patient_last_name = f"仮{patient_first_name}" # Add a prefix
    patient_last_name_kana = f"カリ{patient_first_name_kana}" # Add a prefix

    # Address
    if random.random() < 0.5:
        # 50% Tokyo, because the hospital is located near Tokyo (See random hospital)
        prefecture = "東京都"  # Fixed
    elif random.random() < 0.5:
        # 25% chance prefecture is from the list
        prefecture = random.choice(
            ["埼玉県", "神奈川県", "千葉県", "茨城県", "栃木県", "群馬県", "山梨県"]
        )
    else:
        # Otherwise random
        prefecture = None 
    patient_address, patient_postal_code = generate_random_address(
        fake, 
        # Use a selected one or random
        prefecture=prefecture, 
        # 50% chance of adding building name
        add_building_name=random.random() < 0.5
    )
    # Phone numbers
    home_phone = generate_random_phone(prefix="099")
    # Work place
    if age < 16:
        is_working = False
    elif age >= 16 and age < 24:
        is_working = random.random() < 0.5  # 50% chance
    elif age >= 24 and age < 65:
        is_working = random.random() < 0.8  # 90% chance
    else:  # age >= 65
        is_working = random.random() < 0.4  # 40% chance
    if is_working:
        work_place = fake.company()
        work_phone = generate_random_phone(prefix="099")
    else:
        work_place = ""
        work_phone = ""

    # === Observations ===
    rh_blood_type = "+" if random.random() < 0.995 else "-"  # 99.5% chance of Rh+
    abo_blood_type = random.choices(
        RANDOM_ABO_BLOOD_TYPES["choices"],
        weights=RANDOM_ABO_BLOOD_TYPES["weights"],
        k=1,
    )[
        0
    ]  # Randomly select ABO blood type based on weights
    # TODO: Add height and weight generation logic
    height = np.random.normal(
        loc=172,  # Average height in cm
        scale=6,  # Standard deviation in cm
    )
    weight = np.random.normal(
        loc=60,  # Average weight in kg
        scale=10,  # Standard deviation in kg
    )
    height = f"{height:.1f}"
    weight = f"{weight:.1f}"

    # === Allergies ===
    allergies = generate_random_allergies(
        n_allergy_list=[0, 1, 2, 3, 4],
        weitghs=[0.5, 0.2, 0.2, 0.05, 0.05],
    )
    # === Insurances ===
    insurances = []
    for _ in range(n_insurance):
        insurance = generate_random_insurances(latest_date)
        insurances.append(insurance)

    # Object creation
    patient = Patient(
        patient_id=patient_id,
        dob=dob,
        sex=sex,
        patient_first_name=patient_first_name,
        patient_first_name_kana=patient_first_name_kana,
        patient_first_name_roman=patient_first_name_roman,
        patient_last_name=patient_last_name,
        patient_last_name_kana=patient_last_name_kana,
        patient_last_name_roman=patient_last_name_roman,
        patient_postal_code=patient_postal_code,
        patient_address=patient_address,
        home_phone=home_phone,
        work_place=work_place,
        work_phone=work_phone,
        abo_blood_type=abo_blood_type,
        rh_blood_type=rh_blood_type,
        height=height,
        weight=weight,
        allergies=allergies,
        insurances=insurances,
    )  # Unpack the dictionary into the Patient object

    return patient
