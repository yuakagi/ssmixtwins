"""Module for ADT-52 related messages

Example:
    MSH|^~\&|HIS123|SEND|GW|RCV|20111220224447.3399||ADT^A03^ADT_A03|20111220000001|P|2.5||||||~ISO IR87||ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
    EVN||201112202100|||||SEND001
    PID|0001||9999013||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19700405|M
    PV1|0001|I|41^460^2^^^N||||607^医師^一郎^^^^^^^L^^^^^I|||08|||||||607^医師^一郎^^^^^^^L^^^^^I |||||||||||||||||||01|||||||||201112201200
"""

from ...objects import Patient, Physician, Admission
from ...utils import join_segments
from ...segments import generate_msh, generate_evn, generate_pid, generate_pv1


def generate_adt_a03_message(
    message_time: str,
    message_id: str,
    transaction_time: str,
    discharge_time: str,
    discharge_disposition,
    patient: Patient,
    admission: Admission,
    primary_physician: Physician,
):
    """
    Generates a sample ADT^A03 message in HL7 format.
    This is the main message for ADT-52.

    Returns:
        str: A sample ADT^A03 message.
    """
    # MSH
    # NOTE: Arguments are validated and cleaned in the generate_msh function.
    msh = generate_msh(
        message_code="ADT",
        trigger_event="A03",
        message_structure="ADT_A03",
        message_time=message_time,
        message_id=message_id,
    )
    # ENV
    # NOTE: Arguments are validated and cleaned in the generate_evn function.
    evn = generate_evn(
        message_code="ADT",
        trigger_event="A03",
        message_structure="ADT_A03",
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
        trigger_event="A03",
        message_structure="ADT_A03",
        last_updated="",  # Optional
        patient=patient,
    )
    # PV1
    # NOTE: Arguments are validated and cleaned in the generate_pv1 function.
    pv1 = generate_pv1(
        message_code="ADT",
        trigger_event="A03",
        message_structure="ADT_A03",
        outpatient_department_code="",  # Not applicable for discharge
        discharge_time=discharge_time,
        discharge_disposition=discharge_disposition,
        admission_or_visit_time="",  # Not applicable for discharge
        primary_physician=primary_physician,
        admission=admission,
    )

    # Join segments
    message = join_segments([msh, evn, pid, pv1])
    return message
