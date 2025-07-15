from ..utils import to_datetime_anything
from ..objects import Patient, PrescriptionOrder, Admission, Physician
from ..config import BASE_TIMESTAMP_FORMAT
from ..messages import generate_rde_o11_prescription_message
from .basics import save_message_to_file


def create_omp_01(
    ssmix_root: str,
    message_id: str,  # 20 characters long.
    patient: Patient,
    hospital: str,
    admission: Admission | None,
    outpatient_department_code: str,
    primary_physician: Physician,
    orders: list[PrescriptionOrder],
    encoding: str,
):
    """Creates a OMP-01 message (prescription order) and saves it to a file.

    Args:
        ssmix_root (str): The root directory for SSMIX files.
        message_id (str): The unique message ID for the PPR message.
        patient (Patient): The patient object containing patient details.
        hospital (str): The name of the hospital.
        admission (Admission): The admission object containing admission details.
        outpatient_department_code (str): The code for the outpatient department.
        primary_physician (Physician): The primary physician object.
        orders (list[PrescriptionOrder]): List of PrescriptionOrder objects containing prescription data.
        encoding (str): The encoding to use when saving the file.

    Returns:
        None
    """
    # Timestamp
    # NOTE: The transaction time is expected to be the same for all orders in the same file.
    transaction_time = orders[0].transaction_time
    for order in orders:
        assert (
            order.transaction_time == transaction_time
        ), "All orders must have the same transaction time."
    transaction_time_dt = to_datetime_anything(transaction_time)
    message_time = transaction_time_dt.strftime(BASE_TIMESTAMP_FORMAT)

    # Create a message
    rde_o11_message = generate_rde_o11_prescription_message(
        message_time=message_time,
        message_id=message_id,
        outpatient_department_code=outpatient_department_code,
        patient=patient,
        admission=admission,
        primary_physician=primary_physician,
        hospital=hospital,
        orders=orders,
    )

    # Save the file
    requester_order_number = orders[
        0
    ].requester_order_number  # NOTE: Order number (ORC-2) is expected to be shared.
    for order in orders:
        assert (
            order.requester_order_number == requester_order_number
        ), "All orders must have the same requester order number."

    save_message_to_file(
        message=rde_o11_message,
        ssmix_root=ssmix_root,
        patient_id=patient.patient_id,
        date=transaction_time[:8],  # ORC-9
        data_type="OMP-01",
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
