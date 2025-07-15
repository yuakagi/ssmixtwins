import random
from .physician import Physician, generate_random_physician
from ..random_data import (
    RANDOM_WARDS,
    RANDOM_BEDS,
    RANDOM_ROOMS,
)


class Admission:
    """Represents an admission event for a patient."""

    def __init__(
        self,
        admission_ward_code: str,
        admission_room_code: str,
        admission_bed_code: str,
        physician: Physician | None = None,
    ):
        # Validate and clean the inputs
        assert isinstance(
            physician, Physician
        ), "physician must be an instance of Physician or None."
        assert admission_bed_code != "", "admission_bed_code must not be empty."
        assert admission_room_code != "", "admission_room_code must not be empty."
        assert admission_ward_code != "", "admission_ward_code must not be empty."
        assert (
            len(admission_ward_code)
            + len(admission_room_code)
            + len(admission_bed_code)
            < 70
        ), f"admission_ward_code, admission_room_code, and admission_bed_code combined must be less than 70 characters, got {len(admission_ward_code) + len(admission_room_code) + len(admission_bed_code)}."

        # Set the attributes
        self.admission_ward_code = admission_ward_code
        self.admission_room_code = admission_room_code
        self.admission_bed_code = admission_bed_code
        self.physician = physician
        self.department_code = self.physician.department_code


def generate_random_admission(physician: Physician | None = None) -> Admission:
    """Generates a random admission profile with various attributes.
    Args:
        physician (Physician | None): An optional Physician object. If None, a random physician will be generated.
    Returns:
        Admission: An Admission object containing the admission's attributes.
    """
    admission_ward_code = random.choice(RANDOM_WARDS)
    admission_room_code = random.choice(RANDOM_ROOMS)
    admission_bed_code = random.choice(RANDOM_BEDS)
    if physician is None:
        # If no physician is provided, generate a random one
        physician = generate_random_physician()

    admission = Admission(
        admission_ward_code=admission_ward_code,
        admission_room_code=admission_room_code,
        admission_bed_code=admission_bed_code,
        physician=physician,
    )
    return admission
