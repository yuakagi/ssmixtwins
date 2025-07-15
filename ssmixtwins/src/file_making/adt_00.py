from datetime import datetime
from ..config import BASE_TIMESTAMP_FORMAT
from ..messages import generate_adt_a08_message
from ..objects import Patient, Physician, Admission
from ..utils import generate_random_timedelta
from .basics import save_message_to_file


def create_adt_00(
    ssmix_root: str,
    last_updated: str,  # BASE_TIMESTAMP_FORMAT
    message_id: str,  # 20 characters long.
    patinet: Patient,
    primary_physician: Physician,
    admission: Admission | None,
    encoding: str,
):
    """Creates an ADT-00 message (Demographics) and saves it to a file.

    Args:
        ssmix_root (str): The root directory for SSMIX files.
        last_updated (str): The base time for the last updated.
        message_id (str): The unique message ID for the ADT message.
        patinet (Patient): The patient object containing patient details.
        primary_physician (Physician): The primary physician object.
        admission (Admission | None): The admission object if the patient is admitted, otherwise None.
        encoding (str): The encoding to use when saving the file.
    Returns:
        None
    """
    # Timestamps
    last_updated_dt = datetime.strptime(last_updated, BASE_TIMESTAMP_FORMAT)
    transaction_time = (last_updated_dt + generate_random_timedelta(1, 5)).strftime(
        BASE_TIMESTAMP_FORMAT
    )  # Transaction time is 1-5 minutes after the base time
    message_time = (last_updated_dt + generate_random_timedelta(5, 10)).strftime(
        BASE_TIMESTAMP_FORMAT
    )  # Message time is 25-10 minutes after the base time

    adt_a08_message = generate_adt_a08_message(
        message_time=message_time,
        message_id=message_id,
        transaction_time=transaction_time,
        last_updated=last_updated,
        patient=patinet,
        primary_physician=primary_physician,
        admission=admission,
    )

    # Save the file
    save_message_to_file(
        message=adt_a08_message,
        ssmix_root=ssmix_root,
        patient_id=patinet.patient_id,
        date="-",  # Always '-' for demographics
        data_type="ADT-00",
        requester_order_number="9" * 15,  # Set all nines for demographics
        message_time=message_time,
        department_code="-",  # Set '-' for department code in the file name
        condition_flag="1",  # Currently, only 1 is set.
        encoding=encoding,
    )
    return None
