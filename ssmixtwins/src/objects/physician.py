import random
from faker import Faker
from ..tables import udt_0069
from ..random_data import RANDOM_DEPARTMENT_CODES


class Physician:
    """Physician object to hold physician information."""

    def __init__(
        self,
        physician_id: str,
        physician_first_name: str,
        physician_first_name_kana: str,
        physician_last_name: str,
        physician_last_name_kana: str,
        department_code: str,
        physician_last_name_roman: str = "",  # Not implemented
        physician_first_name_roman: str = "",  # Not implemented
    ):
        """Initializes the Physician object with the provided attributes.

        Args:
            physician_id (str): The unique identifier for the physician.
            physician_first_name (str): The first name of the physician.
            physician_first_name_kana (str): The first name of the physician in Kana.
            physician_first_name_roman (str): The first name of the physician in Roman characters.
            physician_last_name (str): The last name of the physician.
            physician_last_name_kana (str): The last name of the physician in Kana.
            physician_last_name_roman (str): The last name of the physician in Roman characters.
            department_code (str): The code for the department, must be one of udt_0069.
        """

        # Validate and clean the inputs
        if department_code != "":
            assert (
                department_code in udt_0069
            ), f"department_code must be one of {list(udt_0069.keys())}, got '{department_code}'."
        assert physician_id != "", "physician_id must not be empty."
        assert physician_first_name != "", "physician_first_name must not be empty."
        assert physician_last_name != "", "physician_last_name must not be empty."
        assert (
            len(physician_id)
            + len(physician_first_name)
            + len(physician_last_name)
            + len(physician_first_name_kana)
            + len(physician_last_name_kana)
            < 230
        ), f"physician_id, physician_first_name, physician_last_name, physician_first_name_kana, and physician_last_name_kana combined must be less than 230 characters, got {len(physician_id) + len(physician_first_name) + len(physician_last_name) + len(physician_first_name_kana) + len(physician_last_name_kana)}."

        # Set attributes
        self.physician_id = physician_id
        self.physician_first_name = physician_first_name
        self.physician_first_name_kana = physician_first_name_kana
        self.physician_first_name_roman = physician_first_name_roman
        self.physician_last_name = physician_last_name
        self.physician_last_name_kana = physician_last_name_kana
        self.physician_last_name_roman = physician_last_name_roman
        self.department_code = department_code


def generate_random_physician() -> Physician:
    """Generates a random physician profile with various attributes.

    Returns:
        Physician: A Physician object.
    """
    # Create a Faker instance
    fake = Faker("ja_JP")  # Set the locale to Japanese (ja_JP)
    # Generate random physician information
    first_name_pair = fake.first_name_pair()
    last_name_pair = fake.last_name_pair()
    physician_first_name = first_name_pair[0]
    physician_first_name_kana = first_name_pair[1]
    physician_first_name_roman = first_name_pair[2]
    physician_last_name = last_name_pair[0]
    physician_last_name_kana = last_name_pair[1]
    physician_last_name_roman = last_name_pair[2]
    physician_last_name = f"仮{physician_first_name}"  # Prefix with "仮"
    physician_last_name_kana = f"カリ{physician_first_name_kana}"  # Prefix with "カリ"

    # NOTE: The physician ID is a random 10-digit number.
    #   Collision is not checked, although it is unlikely to happen in practice.
    physician_id = str(
        random.randint(1000000000, 9999999999)
    )  # Random 10-digit physician ID
    departmetn_code = random.choice(
        list(RANDOM_DEPARTMENT_CODES.keys())
    )  # Random department code from udt_0069

    # Return the physician attributes
    physician = Physician(
        physician_id=physician_id,
        physician_first_name=physician_first_name,
        physician_first_name_kana=physician_first_name_kana,
        physician_first_name_roman=physician_first_name_roman,
        physician_last_name=physician_last_name,
        physician_last_name_kana=physician_last_name_kana,
        physician_last_name_roman=physician_last_name_roman,
        department_code=departmetn_code,
    )
    return physician
