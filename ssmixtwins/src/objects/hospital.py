import random
from faker import Faker
from ..utils import normalize_and_validate_postal_code


class Hospital:
    """Hospital object to hold hospital information."""

    def __init__(
        self,
        hospital_name: str,
        hospital_postal_code: str,
        hospital_address: str,
        hospital_phone: str,
    ):
        """Initializes the Hospital object with the provided attributes.

        Args:
            hospital_name (str): The name of the hospital.
            hospital_postal_code (str): The postal code of the hospital.
            hospital_address (str): The address of the hospital.
            hospital_phone (str): The phone number of the hospital.
        """
        # Validate and clean the inputs
        assert (
            len(hospital_name) < 250
        ), f"hospital_name must be less than 250 characters, got {len(hospital_name)}."
        if hospital_postal_code != "":
            postal_valid, hospital_postal_code = normalize_and_validate_postal_code(
                hospital_postal_code
            )
            assert (
                postal_valid
            ), "Invalid hospital_postal_code must be a valid postal code."
        assert (
            len(hospital_address) + len(hospital_postal_code) < 230
        ), f"hospital_address and hospital_postal_code combined must be less than 230 characters, got {len(hospital_address)+len(hospital_postal_code)}."
        assert (
            len(hospital_phone) < 230
        ), f"hospital_phone must be less than 230 characters, got {len(hospital_phone)}."

        self.hospital_name = hospital_name
        self.hospital_postal_code = hospital_postal_code
        self.hospital_address = hospital_address
        self.hospital_phone = hospital_phone


def generate_random_hospital() -> Hospital:
    """Generates a random hospital profile with various attributes.

    Returns:
        Hospital: A Hospital object containing the hospital's attributes, including:
            - hospital_name
            - hospital_postal_code
            - hospital_address
            - hospital_phone
    """
    # Create a Faker instance
    fake = Faker("ja_JP")  # Set the locale to Japanese (ja_JP)
    # Generate random hospital information
    # NOTE: We do not use fake.adress() to avoid including building names like 'パーク上野公園565'.
    hospital_name = "日本医療情報推進病院"  # Fixed hospital name for consistency
    prefecture = random.choice(["東京都", "埼玉県"])
    if prefecture == "埼玉県":
        random.choice(["川口市", "さいたま市"])
    city = fake.city()  # Random city kile '横浜市港北区'
    town = fake.town()  #  Random town like '芝公園'
    chome = fake.chome()  # Random chome like '25丁目'
    ban = fake.ban()  # Random ban like '13番'
    gou = fake.gou()  # Random gou like '1号'
    # Construct the hospital address
    hospital_address = f"{prefecture}{city}{town}{chome}{ban}{gou}"
    # Normalize and validate the postal code
    hospital_postal_code = fake.postcode()
    hospital_phone = fake.phone_number()

    # Return the hospital attributes
    hospital = Hospital(
        hospital_name=hospital_name,
        hospital_postal_code=hospital_postal_code,
        hospital_address=hospital_address,
        hospital_phone=hospital_phone,
    )
    return hospital
