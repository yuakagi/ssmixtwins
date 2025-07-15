"""
Scripts to generate generic MSH segment for HL7 messages.

Example:
    MSH|^~\&|HIS123|SEND|GW|RCV|20111220224447.3399||ADT^A08^ADT_A01|20111220000001|P|2.5||||||~ISO IR87|| ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
"""

from ..config import SSMIX_GUIDELINE_VERSION
from ..utils import (
    join_fields,
    make_message_type,
    format_timestamp,
)


def validate_msh_args(message_id: str, message_time: str) -> str:
    """Validates the arguments for generating an MSH segment in HL7 format.
    Args:
        message_id (str): The unique identifier for the message, must be 20 characters or less.
        message_time (str): The time of the message in 'YYYYMMDDHHMMSS[.S[S[S[S]]]]' format.
    Returns:
        str: The formatted message time.
    Raises:
        AssertionError: If the message_id is longer than 20 characters or if the message_time
            does not match the expected format.
    """
    message_time = format_timestamp(
        message_time, format="YYYYMMDDHHMMSS[.S[S[S[S]]]]", allow_null=False
    )
    assert len(message_id) <= 20, "message_id must be 20 characters or less."
    return message_time


def generate_msh(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    message_time: str,
    message_id: str,
) -> str:
    """
    Generates a sample MSH segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        message_time (str): The message time in the format 'YYYYMMDDHHMMSS[.S[S[S[S]]]]'.
        message_id (str): The message ID, e.g., '20111220000001'.
            Must be shorter than 20 characters.
    Returns:
        segment (str): MSH segment.
    """

    # ====== Validation ======
    message_time = validate_msh_args(message_id, message_time)
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    # Create message type
    message_type = make_message_type(message_code, trigger_event, message_structure)

    # ====== TEMPLAETE ======
    template = {
        0: "MSH",
        # NOTE: msh1 is the field separator, so msh1 is omitted.
        2: "^~\&",
        3: "HIS123",  # dummy sending application
        4: "SEND",  # dummy sending facility
        5: "GW",  # dummy receiving application
        6: "RCV",  # dummy receiving facility
        7: message_time,
        8: "",
        9: message_type,  # Example: ADT^A08^ADT_A01
        10: message_id,
        11: "P",  # Processing ID
        12: "2.5",
        13: "",
        14: "",
        15: "",
        16: "",
        17: "",
        18: "~ISO IR87",
        19: "",
        20: "ISO 2022-1994",
        21: f"SS-MIX2_1.20_{SSMIX_GUIDELINE_VERSION}^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO",
    }
    segment = join_fields(template)
    return segment
