from ..utils import to_datetime_anything
from ..objects import Patient, Admission, LabResultSpecimen, Physician
from ..config import BASE_TIMESTAMP_FORMAT
from ..messages import generate_oul_r22_message
from .basics import save_message_to_file


def create_oml_11(
    ssmix_root: str,
    message_id: str,  # 20 characters long.
    patient: Patient,
    hospital: str,
    admission: Admission | None,
    primary_physician: Physician,
    outpatient_department_code: str,
    specimens: list[LabResultSpecimen],
    encoding: str,
):
    """Creates a OMP-02 message (injection order) and saves it to a file.

    Args:
        ssmix_root (str): The root directory for SSMIX files.
        message_id (str): The unique message ID for the PPR message.
        patient (Patient): The patient object containing patient details.
        hospital (str): The name of the hospital.
        admission (Admission | None): The admission object containing admission details.
        outpatient_department_code (str): The code for the outpatient department.
        primary_physician (Physician): The primary physician object.
        specimens (list[LabResultSpecimen]): List of LabResultSpecimen objects containing specimen data.
        encoding (str): The encoding to use when saving the file.

    Returns:
        None
    """
    # Validation

    # Timestamp
    # NOTE: The sampled time is expected to be the same for all orders in the same file.
    sampled_time = specimens[0].sampled_time
    for specimen in specimens:
        assert (
            specimen.sampled_time == sampled_time
        ), "All specimens must have the same sampled time."
    all_reported_times = [
        to_datetime_anything(specimen.reported_time) for specimen in specimens
    ]
    sorted_reported_times = sorted(all_reported_times)
    latest_reported_time = sorted_reported_times[-1]
    message_time = latest_reported_time.strftime(BASE_TIMESTAMP_FORMAT)

    # Create a message
    oul_r22_message = generate_oul_r22_message(
        message_time=message_time,
        message_id=message_id,
        outpatient_department_code=outpatient_department_code,
        patient=patient,
        admission=admission,
        hospital=hospital,
        primary_physician=primary_physician,
        specimens=specimens,
    )

    # Save the file
    requester_order_number = specimens[
        0
    ].requester_order_number  # NOTE: Order number (ORC-2) is expected to be shared.
    for specimen in specimens:
        assert (
            specimen.requester_order_number == requester_order_number
        ), "All specimens must have the same requester order number."

    save_message_to_file(
        message=oul_r22_message,
        ssmix_root=ssmix_root,
        patient_id=patient.patient_id,
        date=sampled_time[:8],  # SPM-17
        data_type="OML-11",
        requester_order_number=requester_order_number,
        message_time=message_time,
        department_code=(
            outpatient_department_code
            if admission is None
            else admission.department_code
        ),
        condition_flag="1",  # Currently, only 1 is set.
        encoding=encoding,
    )
    return None
