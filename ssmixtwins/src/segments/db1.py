"""
Scripts to generate generic DB1 segment for HL7 messages.

Example:
    DB1|1|PT||Y
"""

from typing import Literal
from ..tables import udt_0334
from ..utils import join_fields, make_message_type


def generate_db1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    disability_person_code: str,
    disability_present: Literal["Y", "N"],
) -> str:
    """
    Generates a sample DB1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the disability record, starting from 1.
        disability_person_code (str): Disability person code, must be one of udt_0334.
        disability_present (Literal["Y", "N"]): Indicates if the disability is present.
    Returns:
        str: DB1 segment in HL7 format.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Disability person code
    if disability_person_code not in udt_0334:
        raise ValueError(
            f"disability_person_code must be one of {list(udt_0334.keys())}, got '{disability_person_code}'."
        )

    # ====== TEMPLAETE ======
    template = {
        0: "DB1",
        1: sequence_no,  # From 1
        2: disability_person_code,
        3: "",
        4: disability_present,
        5: "",
        6: "",
        7: "",
        8: "",
    }
    segment = join_fields(template)
    return segment
