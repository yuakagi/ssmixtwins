"""
Scripts to generate generic RXR segment for HL7 messages.

Example:
    RXR|PO^口^HL70162
"""

from ..utils import join_fields, make_message_type
from ..tables import udt_0162, udt_0164


def generate_rxr(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    route_code: str,  # R
    route_device_code: str,  # O
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        route_code (str): The code for the route of administration. Use 'udt_0162' table.
        route_device_code (str): The code for the device used in administration, if applicable. Use 'udt_0164' table.
    Returns:
        str: PV1 segment in HL7 format.

    Notes:
        Validation logics are expected to be handled outside this function.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Route
    if route_code != "":
        route_full = f"{route_code}^{udt_0162[route_code]}^HL70162"
    else:
        route_full = ""
    # Device
    if route_device_code != "":
        route_device_full = f"{route_device_code}^{udt_0164[route_device_code]}^HL70164"
    else:
        route_device_full = ""  # Allow empty

    # ====== TEMPLAETE ======
    template = {
        0: "RXR",
        1: route_full,
        2: "",  # Omitted for simplicity
        3: route_device_full,
        4: "",  # Omitted for simplicity
        5: "",
        6: "",  # Omitted for simplicity
    }
    segment = join_fields(template)
    return segment
