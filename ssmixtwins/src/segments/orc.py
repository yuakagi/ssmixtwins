"""
Scripts to generate generic ORC segment for HL7 messages.

Example:
    ORC|NW|123456789012345||||||||||110^医師^一郎^^^^^^^L^^^^^I~^イシ^イチロウ^^^^^^^L^^^^^P|||||01^内科 ^HL70069||||||||||||O^外来患者オーダ^HL70482
"""

from typing import Literal
from ..objects import Hospital, Physician
from ..tables import udt_0069, h7t_0482
from ..utils import (
    join_fields,
    make_message_type,
)


def generate_orc(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    order_control: str,
    requester_order_number: str,
    filler_order_number: str,
    requester_group_number: str,
    order_status: str,
    transaction_time: str,
    order_effective_time: str,
    order_type: Literal["I", "O"],
    enterer: Physician,
    requester: Physician,
    hospital: Hospital,
) -> str:
    """
    Generates a sample ORC segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        order_control (str): The order control code, e.g., 'NW' for new order.
        requester_order_number (str): The order number assigned by the requester.
        filler_order_number (str): The order number assigned by the filler.
        requester_group_number (str): The group number assigned by the requester.
        order_status (str): The status of the order, e.g., 'SC' for status change.
        transaction_time (str): The time of the transaction in YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        order_effective_time (str): The time when the order becomes effective in YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        order_type (Literal["I", "O"]): The type of order, either 'I' for inpatient or 'O' for outpatient.
        enterer (Physician): The physician who entered the order.
        requester (Physician): The physician who requested the order.
        hospital (Hospital): The hospital information, including name, postal code, address, and phone

    Returns:
        str: ORC segment in HL7 format.

    Notes:
        Validation logics are expected to be handled outside this function.
    """
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Entered by
    enterer_full = f"{enterer.physician_id}^{enterer.physician_last_name}^{enterer.physician_first_name}^^^^^^^L^^^^^I"
    # Requester
    requester_full = f"{requester.physician_id}^{requester.physician_last_name}^{requester.physician_first_name}^^^^^^^L^^^^^I"
    # Department
    # NOTE: SSMIX supports use of local codes, but we do not allow local codes here for simplicity.
    if requester.department_code != "":
        dept_name = udt_0069[requester.department_code]
        dept_full = f"{requester.department_code}^{dept_name}^HL70069"
    else:
        dept_full = ""
    # Hospital
    hp_address_full = (
        f"^^^^{hospital.hospital_postal_code}^JPN^^{hospital.hospital_address}"
    )
    # Order type
    if order_type != "":
        order_type_full = f"{order_type}^{h7t_0482[order_type]}^HL70482"
    else:
        order_type_full = ""

    # ====== TEMPLAETE ======
    template = {
        0: "ORC",
        1: order_control,  # e.g., 'NW' for new order or 'CA' for cancel order.
        2: requester_order_number,
        3: filler_order_number,
        4: requester_group_number,  # e.g., '000000000000001_01_003'.
        5: order_status,  # e.g., 'SC' for status change.
        6: "",
        7: "",
        8: "",
        9: transaction_time,
        10: enterer_full,
        11: "",
        12: requester_full,
        13: "",  # Omitted for simplicity
        14: "",
        15: order_effective_time,
        16: "",  # Omitted for simplicity
        17: dept_full,
        18: "",  # Omitted for simplicity
        19: "",
        20: "",
        21: hospital.hospital_name,
        22: hp_address_full,
        23: hospital.hospital_phone,
        24: "",
        25: "",
        26: "",
        27: "",
        28: "",
        29: order_type_full,
        30: "",
    }
    segment = join_fields(template)
    return segment
