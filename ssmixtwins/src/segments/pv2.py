"""
Scripts to generate generic PV2 segment for HL7 messages.
"""

from ..utils import join_fields, make_message_type, format_timestamp


def generate_pv2(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    admission_ward_code: str,
    admission_room_code: str,
    admission_bed_code: str,
    expected_admit_time: str,
    expected_discharge_time: str,
    expected_loa_return_time: str,
) -> str:
    """
    Generates a sample PV2 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        admission_ward_code (str): Admission ward code.
        admission_room_code (str): Admission room code.
        admission_bed_code (str): Admission bed code.
        expected_admit_time (str): Expected admit time in the format 'YYYYMMDD[HH[MM[SS]]]'.
        expected_discharge_time (str): Expected discharge time in the format 'YYYYMMDD[HH[MM[SS]]].
        expected_loa_return_time (str): Expected return time from leave of absence in the format 'YYYYMMDD[HH[MM[SS]]].
    Returns:
        str: PV1 segment in HL7 format.
    """
    # ====== Validation ======
    # Validate timestamps
    expected_admit_time = format_timestamp(
        expected_admit_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    expected_discharge_time = format_timestamp(
        expected_discharge_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    expected_loa_return_time = format_timestamp(
        expected_loa_return_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    # References
    can_use_pv2_1 = ["ADT^A27", "ADT^A26"]
    can_use_pv2_8 = ["ADT^A14", "ADT^A27"]
    can_use_pv2_9 = ["ADT^A16", "ADT^A25"]
    can_use_pv2_47 = ["ADT^A21", "ADT^A22", "ADT^A52", "ADT^A53"]
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    partial_message_type = "^".join([message_code, trigger_event])  # e.g., "ADT^A01"
    # Pending loc
    if partial_message_type in can_use_pv2_1:
        prior_pending_location = (
            f"{admission_ward_code}^{admission_room_code}^{admission_bed_code}^^^N"
        )
    else:
        prior_pending_location = ""
    # Expected admit time
    if partial_message_type in can_use_pv2_8:
        if expected_admit_time != "":
            raise ValueError(
                f"expected_admit_time must not be provided for {partial_message_type}."
            )
    # Discharge time
    if partial_message_type in can_use_pv2_9:
        if expected_discharge_time != "":
            raise ValueError(
                f"expected_discharge_time must not be provided for {partial_message_type}."
            )
    # LAO return time
    if partial_message_type not in can_use_pv2_47:
        if expected_loa_return_time != "":
            raise ValueError(
                f"expected_loa_return_time must not be provided for {partial_message_type}."
            )

    # ====== TEMPLAETE ======
    template = {
        0: "PV2",
        1: prior_pending_location,
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: expected_admit_time,
        9: expected_discharge_time,
        10: "",
        11: "",
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: "",
        18: "",
        19: "",
        20: "",
        21: "",
        22: "",
        23: "",
        24: "",
        25: "",
        26: "",
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
        47: expected_loa_return_time,
        48: "",
        49: "",
    }
    segment = join_fields(template)
    return segment
