"""
Scripts to generate generic TQ1 segment for HL7 messages.

Example:
    TQ1|1||1012040400000000&内服・経口・１日２回朝夕食後&JAMISDP01|||14^d|2011070100
"""

from ..utils import join_fields, make_message_type, format_timestamp


def generate_tq1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    amount: str,
    repeat_pattern_code: str,
    repeat_pattern_name: str,
    repeat_pattern_code_system: str,
    duration: str,
    duration_unit: str,
    start_time: str,
    end_time: str,
    total_occurrences: str,
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the TQ1 segment, starting from 1.
        amount (str): The amount of the item, e.g., '1'.
        repeat_pattern_code (str): The code for the repeat pattern, e.g., '1012040400000000'.
        repeat_pattern_name (str): The name of the repeat pattern, e.g., '内服・経口・１日２回朝夕食後'.
        repeat_pattern_code_system (str): The code system for the repeat pattern, e.g., 'JAMISDP01'.
        duration (str): The duration of the item, e.g., '14'.
        duration_unit (str): The unit of the duration, e.g., 'd' for days.
        start_time (str): The start time in the format 'YYYYMMDD[HH[MM]]'.
        end_time (str): The end time in the format 'YYYYMMDD[HH[MM]]'.
        total_occurrences (str): The total number of occurrences, if applicable.
            For example, '10' for 10 PRN doses.

    Returns:
        str: PV1 segment in HL7 format.
    """
    # ====== Validation ======
    # Validate timestamps
    start_time = format_timestamp(
        start_time, format="YYYYMMDD[HH[MM]]", allow_null=True
    )
    end_time = format_timestamp(end_time, format="YYYYMMDD[HH[MM]]", allow_null=True)
    # Total occurrences
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Repeat pattern
    # NOTE: Joined using '&'
    repeat_full = (
        f"{repeat_pattern_code}&{repeat_pattern_name}&{repeat_pattern_code_system}"
    )
    # Duration
    if duration != "":
        if not duration.isdigit():
            raise ValueError("duration must be a digit.")
        if duration_unit == "":
            raise ValueError("duration_unit must not be empty if duration is provided.")
        duration_full = f"{duration}^{duration_unit}"
    elif duration_unit != "":
        raise ValueError("duration must not be empty if duration_unit is provided.")
    else:
        duration_full = ""

    # ====== TEMPLAETE ======
    template = {
        0: "TQ1",
        1: sequence_no,
        2: amount,
        3: repeat_full,
        4: "",
        5: "",
        6: duration_full,
        7: start_time,
        8: end_time,
        9: "",
        10: "",
        11: "",  # Omitted for simplicity
        12: "",
        13: "",
        14: total_occurrences,
    }
    segment = join_fields(template)
    return segment
