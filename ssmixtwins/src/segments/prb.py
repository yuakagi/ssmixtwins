"""
Scripts to generate generic PRB segment for HL7 messages.

Example:
    PRB|AD|20110915|20054174^胃炎^MDCDX2|123456789012345|||20110831||20110915|K297^^I10^O^外来時 ^JHSD0004||||N^回復せず^HL70241|20110915|20110831|胃炎|1^主診断^JHSD0007|||||||V^非常に限定^HL70177
"""

from ..objects import Problem
from ..tables import jhsd_0004
from ..utils import join_fields, make_message_type


def generate_prb(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    problem: Problem,
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        problem (Problem): An instance of the Problem object containing problem details.
    Returns:
        str: PRB segment in HL7 format.
    """

    # References
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Problem ID (Like, 20054174^胃炎^MDCDX2)
    # NOTE: dx_code_system is expected to be MDCDX2
    prob_id_full = f"{problem.dx_code}^{problem.dx_name}^{problem.dx_code_system}"
    # Problem classification (ICD-10 + diagnosis type, like <ICD-10 の値>^^I10^<診断種別>^<テキスト>^JHSD0004)
    if problem.diagnosis_type != "":
        dx_type_name = jhsd_0004[problem.diagnosis_type]
        dx_type_system = "JHSD0004"
    else:
        dx_type_name = ""
        dx_type_system = ""
    # ICD-10
    dx_class_full = f"{problem.icd10_code}^{problem.icd10_name}^I10^{problem.diagnosis_type}^{dx_type_name}^{dx_type_system}"

    # ====== TEMPLAETE ======
    template = {
        0: "PRB",
        1: problem.action_code,
        2: problem.action_time,
        3: prob_id_full,
        4: problem.prb_instance_id,
        5: "",  # Omitted for simplicity
        6: "",  # Priority, omitted for simplicity
        7: problem.date_of_diagnosis,
        8: problem.expected_time_solved,
        9: problem.time_solved,
        10: dx_class_full,
        11: "",  # Omitted for simplicity
        12: "",  # Omitted for simplicity
        13: problem.provisional,  # '1' or ''
        14: "",  # Omitted for simplicity
        15: "",  # Omitted for simplicity
        16: problem.time_of_onset,
        17: "",  # Omitted for simplicity
        18: "",  # Omitted for simplicity
        19: "",  # Omitted for simplicity
        20: "",  # Omitted for simplicity
        21: "",  # Omitted for simplicity
        22: "",  # Omitted for simplicity
        23: "",  # Omitted for simplicity
        24: "",  # Omitted for simplicity
        25: "",  # Omitted for simplicity
    }
    segment = join_fields(template)
    return segment
