from datetime import datetime
from ..objects import Patient, Physician, Admission
from ..config import BASE_TIMESTAMP_FORMAT
from ..messages import generate_adt_a01_message
from ..utils import generate_random_timedelta
from .basics import save_message_to_file


def create_adt_22(
    ssmix_root: str,
    admission_time: str,  # BASE_TIMESTAMP_FORMAT
    message_id: str,  # 20 characters long.
    patient: Patient,
    primary_physician: Physician,
    admission: Admission,
    requester_order_number: str,
    encoding: str,
):
    """Creates an ADT-22 message (admission) and saves it to a file.

    Args:
        ssmix_root (str): The root directory for SSMIX files.
        admission_time (str): The base time for the admission.
        message_id (str): The unique message ID for the ADT message.
        patient (Patient): The patient object containing patient details.
        primary_physician (Physician): The primary physician object.
        admission (Admission): The admission object containing admission details.
        requester_order_number (str): The order number for the visit. This is only for file naming
        encoding (str): The encoding to use when saving the file.

    Returns:
        None
    """
    # Timestamps
    admission_time_dt = datetime.strptime(admission_time, BASE_TIMESTAMP_FORMAT)
    transaction_time = (admission_time_dt + generate_random_timedelta(1, 5)).strftime(
        BASE_TIMESTAMP_FORMAT
    )  # Transaction time is 1-5 minutes after the base time
    message_time = (admission_time_dt + generate_random_timedelta(5, 10)).strftime(
        BASE_TIMESTAMP_FORMAT
    )  # Message time is 25-10 minutes after the base time

    adt_a01_message = generate_adt_a01_message(
        message_time=message_time,
        message_id=message_id,
        transaction_time=transaction_time,
        admission_time=admission_time,
        admission=admission,
        primary_physician=primary_physician,
        patient=patient,
    )

    # Save the file
    save_message_to_file(
        message=adt_a01_message,
        ssmix_root=ssmix_root,
        patient_id=patient.patient_id,
        date=admission_time[
            :8
        ],  # YYYYMMDD component, for ADT-22, you must use PV1-44 'admission_time' as the date
        data_type="ADT-22",
        requester_order_number=requester_order_number,
        message_time=message_time,
        department_code=admission.department_code,
        condition_flag="1",  # Default condition flag
        encoding=encoding,
    )
    return None
