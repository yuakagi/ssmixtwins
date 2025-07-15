from ..objects import Patient, Problem
from ..config import BASE_TIMESTAMP_FORMAT
from ..messages import generate_ppr_zd1_message
from ..utils import to_datetime_anything
from .basics import save_message_to_file


def create_ppr_01(
    ssmix_root: str,
    message_id: str,  # 20 characters long.
    patient: Patient,
    hospital: str,
    problems: list[Problem],
    encoding: str,
):
    """Creates a PPR-01 message (Problem) and saves it to a file.

    Args:
        ssmix_root (str): The root directory for SSMIX files.
        message_id (str): The unique message ID for the PPR message.
        patient (Patient): The patient object containing patient details.
        hospital (str): The name of the hospital.
        problems (list[Problem]): List of Problem objects containing problem data.
        encoding (str): The encoding to use when saving the file.

    Returns:
        None
    """
    # Timestamp
    all_action_times = [to_datetime_anything(p.action_time) for p in problems]
    sorted_action_times = sorted(all_action_times)
    latest_action_time = sorted_action_times[-1]
    message_time = latest_action_time.strftime(BASE_TIMESTAMP_FORMAT)

    # Create a message
    ppr_zd1_message = generate_ppr_zd1_message(
        message_time=message_time,
        message_id=message_id,
        patient=patient,
        hospital=hospital,
        problems=problems,
    )

    # Save the file
    requester_order_number = problems[
        0
    ].requester_order_number  # NOTE: Order number (ORC-2) is expected to be shared.
    for problem in problems:
        assert (
            problem.requester_order_number == requester_order_number
        ), "All problems must have the same requester order number."

    save_message_to_file(
        message=ppr_zd1_message,
        ssmix_root=ssmix_root,
        patient_id=patient.patient_id,
        date="-",  # Set '-' for PPR-01
        data_type="PPR-01",
        requester_order_number=requester_order_number,
        message_time=message_time,
        department_code="-",  # Set '-' for department code in the file name
        condition_flag="1",  # Currently, only 1 is set.
        encoding=encoding,
    )
    return None
