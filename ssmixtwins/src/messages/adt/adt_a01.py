"""Module for ADT-22 related messages

Example:
    MSH|^~\&|HIS123|SEND|GW|RCV|20111220224447.3399||ADT^A01^ADT_A01|20111220000001|P|2.5||||||~ISO IR87|| ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
    EVN||201112202100|||||SEND001
    PID|0001||9999013||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19480405|M
    PV1|0001|I|32^302^1^^^N||||ishi01^医師一郎^^^^^^^^L^^^^^I|||01|||||||ishi01^医師一郎^^^^^^^^L^^^^^I |||||||||||||||||||||||||||201111201600
"""

from ...utils import join_segments
from ...objects import Patient, Physician, Admission
from ...segments import generate_msh, generate_evn, generate_pid, generate_pv1


def generate_adt_a01_message(
    message_time: str,
    message_id: str,
    transaction_time: str,
    admission_time: str,
    patient: Patient,
    admission: Admission,
    primary_physician: Physician,
) -> str:
    """
    Generates a sample ADT^A01 message in HL7 format.
    This is the main message for ADT-22.

    Returns:
        str: A sample ADT^A01 message.
    """
    # MSH
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
        patient=patient,
        last_updated="",  # Optional
    )
    # PV1
    # NOTE: Arguments are validated and cleaned in the generate_pv1 function.
    pv1 = generate_pv1(
        message_code="ADT",
        trigger_event="A01",
        message_structure="ADT_A01",
        outpatient_department_code="",  # Not applicable for admission
        discharge_time="",  # Not applicable for admission
        discharge_disposition="",  # Not applicable for admission
        admission_or_visit_time=admission_time,
        primary_physician=primary_physician,
        admission=admission,
    )

    # Join segments
    message = join_segments([msh, evn, pid, pv1])
    return message
