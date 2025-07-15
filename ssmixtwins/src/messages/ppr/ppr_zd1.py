"""Module for PPR-01 related messages

Example:
    MSH|^~\&|HIS123|SEND|GW|RCV|20111209163030||PPR^ZD1^PPR_ZD1|201112091630305|P|2.5||||||~ISO IR87||ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
    PID|0001||1234567890^^^^PI||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19650415|M
    PRB|AD|20110915|20054174^胃炎^MDCDX2|123456789012345|||20110831||20110915|K297^^I10^O^外来時 ^JHSD0004||||N^回復せず^HL70241|20110915|20110831|胃炎|1^主診断^JHSD0007|||||||V^非常に限定^HL70177
    ZPR||20054174^胃炎^MDCDX2|||TSQF^胃炎^MDCDX2
    ZI1|1|01^全国健康保険協会管掌健康保険^JHSD0001|1130012|全国健康保険協会東京支部||||||123456|11010203 |20110901|20120831||13||SEL^本人^HL70063
    ORC|NW|123456789012345||||||||||110^医師^一郎^^^^^^^L^^^^^I~^イシ^イチロウ^^^^^^^L^^^^^P|||||01^内科 ^HL70069||||||||||||O^外来患者オーダ^HL70482
"""

import copy
from ...utils import join_segments_dict
from ...objects import Problem, Patient, Hospital
from ...segments import (
    generate_msh,
    generate_pid,
    generate_prb,
    generate_orc,
)


PPR_ZD1_BASE = {
    "MSH": None,
    "PID": None,
    "problems": [],  # <- Append probems here
}
PROBLEM_BASE = {
    "PRB": None,
    "ZPR": None,
    "ZPD": [],
    "ZI1": [],
    "ORC": [],
}


def generate_ppr_zd1_base_message(
    message_time: str,
    message_id: str,
    patient: Patient,
):
    """
    Generates a base PPR^ZD1 message structure.

    Args:
        message_time (str): The time the message is generated. YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        message_id (str): Unique identifier for the message.
        patient_id (str): Unique identifier for the patient.
        patient_first_name (str): First name of the patient.
        patient_last_name (str): Last name of the patient.
        patient_first_name_kana (str): First name in Kana.
        patient_last_name_kana (str): Last name in Kana.
        dob (str): Date of birth of the patient (YYYYMMDD).
        sex (Literal["F", "M", "O", "U"]): Patient sex.
        patient_postal_code (str): Postal code of the patient.
        patient_address (str): address of the patient.
        home_phone (str): Home phone number of the patient.
        work_phone (str): Work phone number of the patient.
    Returns:
        dict: A base PPR^ZD1 message structure with MSH and PID segments.
    """
    # MSH
    # NOTE: Arguments are validated in the generate_msh function.
    msh = generate_msh(
        message_code="PPR",
        trigger_event="ZD1",
        message_structure="PPR_ZD1",
        message_time=message_time,
        message_id=message_id,
    )
    # PID
    # NOTE: Arguments are validated in the generate_pid function.
    pid = generate_pid(
        message_code="PPR",
        trigger_event="ZD1",
        message_structure="PPR_ZD1",
        last_updated="",  # Optional
        patient=patient,
    )
    base = copy.deepcopy(PPR_ZD1_BASE)
    base["MSH"] = msh
    base["PID"] = pid
    return base


def update_ppr_zd1_base_message(
    base_message: dict,
    problem: Problem,
    hospital: Hospital,
):
    """
    Updates the base PPR^ZD1 message with a new problem.
    Args:
        base_message (dict): The base PPR^ZD1 message structure.

    Returns:
        dict: Updated PPR^ZD1 message structure with the new problem added.
    """
    # === Validation ===
    # Generate the PRB segment
    # { PRB
    prb = generate_prb(
        message_code="PPR",
        trigger_event="ZD1",
        message_structure="PPR_ZD1",
        problem=problem,
    )
    # [ZPR]
    # NOTE: Currently ZPR is not supported.
    # [{ZPD}]
    # NOTE: Currently ZPD is not supported.
    # [{ZI1}]
    # NOTE: Currently ZI1 is not supported.
    # [{ ORC }]
    orc = generate_orc(
        message_code="PPR",
        trigger_event="ZD1",
        message_structure="PPR_ZD1",
        order_control=problem.order_control,
        requester_order_number=problem.prb_instance_id,  # This is equivalent to PRB-4 (prb_instance_id)
        filler_order_number=problem.filler_order_number,
        requester_group_number="",  # Currently not supported in PPR^ZD1
        transaction_time=problem.transaction_time,  # Optional, can be left empty
        order_effective_time=problem.order_effective_time,
        order_type=problem.order_type,
        order_status="",  # Not implemented.
        hospital=hospital,
        requester=problem.requester,
        enterer=problem.enterer,
    )
    # }

    # Update the base message with the new problem
    prb_set = copy.deepcopy(PROBLEM_BASE)
    prb_set["PRB"] = prb
    prb_set["ZPR"] = None  # Currently ZPR is not supported
    prb_set["ZPD"] = []  # Currently ZPD is not supported
    prb_set["ZI1"] = []  # Currently ZI1 is not supported
    prb_set["ORC"] = [orc]  # ORC is a list (only one ORC per PRB)
    # Add the problem set to the base message
    base_message["problems"].append(prb_set)

    # Returne the updated base message
    return base_message


# ⭐️ This is the main function ⭐️
def generate_ppr_zd1_message(
    message_time: str,
    message_id: str,
    patient: Patient,
    hospital: Hospital,
    problems: list[Problem],
):
    """
    Generates a sample PPR^ZD1 message in HL7 format.
    This is the main message for PPR-01.

    Args:
        message_time (str): The time the message is generated. YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        message_id (str): Unique identifier for the message.
        patient (Patient): The patient object containing patient information.
        hospital (Hospital): The hospital object containing hospital information.
        problems (list[Problem]): A list of Problem objects containing problem information.
    Returns:
        str: A sample PPR^ZD1 message in HL7 format.
    """
    # Base
    base_message = generate_ppr_zd1_base_message(
        message_time=message_time,
        message_id=message_id,
        patient=patient,
    )
    # Process each problem in the DataFrame
    for prb in problems:
        base_message = update_ppr_zd1_base_message(
            base_message=base_message,
            problem=prb,
            hospital=hospital,
        )
    # Finalize the message
    message = join_segments_dict(base_message)
    return message
