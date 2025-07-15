"""Module for ADT-12 related messages (Outpatient visit)"""

from ...utils import join_segments
from ...objects import Patient, Physician
from ...segments import generate_msh, generate_evn, generate_pid, generate_pv1


def generate_adt_a04_message(
    message_time: str,
    message_id: str,
    transaction_time: str,
    department_code: str,
    visit_time: str,
    patient: Patient,
    primary_physician: Physician,
):
    """
    Generates a sample ADT^A04 message in HL7 format.
    This is the main message for ADT-12.

    Returns:
        str: A sample ADT_A04 message.
    """

    # MSH
    # NOTE: Arguments are validated and cleaned in the generate_msh function.
    msh = generate_msh(
        message_code="ADT",
        trigger_event="A01",
        message_structure="ADT_A01",
        message_time=message_time,
        message_id=message_id,
    )
    # ENV
    # NOTE: Arguments are validated and cleaned in the generate_evn function.
    evn = generate_evn(
        message_code="ADT",
        trigger_event="A01",
        message_structure="ADT_A01",
        transaction_time=transaction_time,
        planned_event_time="",
        evn_reason_code="",
        controller_id="",
        evn_time="",
    )
    # PID
    # NOTE: Arguments are validated and cleaned in the generate_pid function.
    pid = generate_pid(
        message_code="ADT",
        trigger_event="A01",
        message_structure="ADT_A01",
        last_updated="",  # Optional
        patient=patient,
    )
    # PV1
    # NOTE: Arguments are validated and cleaned in the generate_pv1 function.
    pv1 = generate_pv1(
        message_code="ADT",
        trigger_event="A01",
        message_structure="ADT_A01",
        outpatient_department_code=department_code,
        discharge_time="",  # Not applicable for outpatient
        discharge_disposition="",  # Not applicable for outpatient
        admission_or_visit_time=visit_time,
        primary_physician=primary_physician,
        admission=None,  # No admission for outpatient
    )

    # Join segments
    message = join_segments([msh, evn, pid, pv1])
    return message
