"""
Scripts to generate generic OBR segment for HL7 messages.

Example:
    OBR|1|000000011000354|000000001219001|E001^血液学的検査^99O03|||20111219|20111219||||||||607^医師一郎 ^^^^^^^^L^^^^^I||||||20111220103059
"""

from ..objects import Physician
from ..utils import join_fields, make_message_type


def generate_obr(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    requester_order_number: str,  # 15-digit number, e.g., '000000011000354'
    filler_order_number: str,  # 15-digit number, e.g., '000000001219001'
    test_type_code: str,
    test_type_name: str,
    test_type_code_system: str,
    sampled_time: str,  # 'YYYYMMDD[HHMM]', but for clarity, we use YYYYMMDD[HH[MM]]
    sampling_finished_time: str,  # 'YYYYMMDD[HHMM]', but for clarity, we use YYYYMMDD[HH[MM]]
    requester: (
        Physician | None
    ),  # An object containing requester details, or None if not applicable
    reported_time: str,  # YYYYMMDDHHMMSS
    parent_result: str,
) -> str:
    """
    Generates a sample OBR segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the OBX segment, starting from 1.
        requester_order_number (str): The order request number, e.g., '000000011000354'.
        filler_order_number (str): The filler order number, e.g., '000000001219001'.
        test_type_code (str): Test type code.
        test_type_name (str): Test type name, e.g., "血液学的検査".
        test_type_code_system (str): Code system for the test type.
        sampled_time (str): Time when the sample was taken, in the format 'YYYYMMDD[HH[MM]]'.
        sampling_finished_time (str): Time when the sampling was finished, in the format 'YYYYMMDD[HH[MM]]'.
        requester (Physician): An object containing requester details.
        reported_time (str): Time when the results were reported, in the format 'YYYYMMDDHHMMSS'.
        parent_result (str): Parent result identifier, if applicable.

    Returns:
        str: OBR segment in HL7 format.
    """
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # ====== Validation ======
    if test_type_code != "" or test_type_name != "" or test_type_code_system != "":
        test_type_full = f"{test_type_code}^{test_type_name}^{test_type_code_system}"
    else:
        test_type_full = ""
    if requester is not None:
        requester_full = f"{requester.physician_id}^{requester.physician_last_name}^{requester.physician_first_name}"
    else:
        requester_full = ""

    # ====== TEMPLAETE ======
    template = {
        0: "OBR",
        1: sequence_no,
        2: requester_order_number,
        3: filler_order_number,
        4: test_type_full,
        5: "",
        6: "",
        7: sampled_time,
        8: sampling_finished_time,
        9: "",
        10: "",
        11: "",
        12: "",  # Omitted for simplicity (危険物コード)
        13: "",
        14: "",
        15: "",
        16: requester_full,
        17: "",
        18: "",
        19: "",
        20: "",
        21: "",
        22: reported_time,
        23: "",
        24: "",
        25: "",
        26: parent_result,
        27: "",
        28: "",
        29: "",
        30: "",
        31: "",
        32: "",
        33: "",
        34: "",
        35: "",
        36: "",
        37: "",
        38: "",
        39: "",
        40: "",
        41: "",
        42: "",
        43: "",
        44: "",
        45: "",
        46: "",
        47: "",
        48: "",
        49: "",
    }
    segment = join_fields(template)
    return segment
