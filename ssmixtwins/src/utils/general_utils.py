"""Utility functions for HL7 message generation."""

import re
from ..tables import h7t_0354, udt_0003, udt_0076

# Define pattern to match hyphen-like characters
HYPHEN_VARIANTS = r"[‐‑‒–—―ー－]"

# Strict postal code pattern
POSTAL_PATTERN = r"^\d{3}-\d{4}$"


def make_message_type(
    message_code: str, trigger_event: str, message_structure: str
) -> str:
    """
    Constructs a message type string in HL7 format.

    This fuction vailidates the input parameters.

    Args:
        message_code (str): The code for the message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.

    Returns:
        str: The constructed message type string.
    """
    # Validate inputs
    if message_code not in udt_0076:
        raise ValueError(
            f"message_code must be one of {list(udt_0076.keys())}, but got '{message_code}'."
        )
    if trigger_event not in udt_0003:
        raise ValueError(
            f"trigger_event must be one of {list(udt_0003.keys())}, but got '{trigger_event}'."
        )
    if message_structure not in h7t_0354:
        raise ValueError(
            f"message_structure must be one of {list(h7t_0354.keys())}, but got '{message_structure}'."
        )
    # Construct message type
    message_type = f"{message_code}^{trigger_event}^{message_structure}"

    return message_type


def join_fields(template: dict) -> str:
    """
    Joins fields with a pipe character ('|').

    Args:
        fields (list): List of fields to join.

    Returns:
        str: Joined string with fields separated by '|'.
    """
    joined = "|".join(
        str(field) if field is not None else "" for field in template.values()
    )
    # Remove trailing pipe character if it exists
    trimmed = joined.rstrip("|")
    return trimmed


def normalize_and_validate_postal_code(input_str: str) -> tuple[bool, str]:
    """
    Normalize and validate a postal code string.
    This function replaces various hyphen-like characters with a standard hyphen
    and checks if the resulting string matches the postal code format.
    Args:
        input_str (str): The postal code string to normalize and validate.
    Returns:
        tuple: A tuple containing a boolean indicating validity and the normalized string.
    """
    # Check if input_str is None or empty
    # Step 1: Normalize hyphens
    normalized = re.sub(HYPHEN_VARIANTS, "-", input_str)
    # Step 2: Validate
    if re.match(POSTAL_PATTERN, normalized):
        return True, normalized
    else:
        return False, normalized
