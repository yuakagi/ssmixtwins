"""
Scripts to generate generic NK1 segment for HL7 messages.

Example:
    NK1|1|患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P|SEL^本人^HL70063|^^^^422-8033^JPN^H^静岡県静岡市登呂１ －３－５~^^^^1050003^^B^東京都港区鹿ノ門６丁目３番３号|^PRN^PH^^^^^^^^^054-000-0000| ^WPN^PH^^^^^^^^^03-3599-9993|||||||鹿ノ門商事株式会社^D
"""

from ..tables import udt_0063
from ..utils import join_fields, normalize_and_validate_postal_code, make_message_type


def generate_nk1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    first_name: str,
    last_name: str,
    first_name_kana: str,
    last_name_kana: str,
    relationship: str,
    patient_postal_code: str,
    patient_address: str,
    home_phone: str,
    work_phone: str,
    work_place: str,
) -> str:
    """
    Generates a sample NK1 segment in HL7 format.
    Args:
        message_code: The code for message type, e.g., 'ADT'.
        trigger_event: The trigger event type, e.g., 'A08'.
        message_structure: The message structure, e.g., 'ADT_A01'.
        sequence_no: The sequence number for the NK1 segment starting from 1.
        first_name: The first name of the contact.
        last_name: The last name of the contact.
        first_name_kana: The first name in Kana.
        last_name_kana: The last name in Kana.
        relationship: The relationship to the patient, must be one of udt_0063.
        patient_postal_code: The postal code in the format 'XXX-XXXX'.
        patient_address: The address of the contact.
        home_phone: The home phone number.
        work_phone: The work phone number.
        work_place: The workplace of the contact.
    Returns:
        str: NK1 segment in HL7 format.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Relationship
    if relationship != "":
        if relationship not in udt_0063:
            raise ValueError(f"relationship must be one of {list(udt_0063.keys())}.")
    # Clean and validate postal code
    if patient_postal_code != "":
        postal_valid, patient_postal_code = normalize_and_validate_postal_code(
            patient_postal_code
        )
        if not postal_valid:
            raise ValueError(
                f"patient_postal_code must be in the format 'XXX-XXXX', got '{patient_postal_code}'."
            )

    # ====== TEMPLAETE ======
    template = {
        0: "NK1",
        1: sequence_no,
        2: f"{last_name}^{first_name}^^^^L^I~{last_name_kana}^{first_name_kana}^^^^^L^P",
        3: relationship,
        4: f"^^^^{patient_postal_code}^JPN^H^{patient_address}",
        5: home_phone,
        6: work_phone,
        7: "",
        8: "",
        9: "",
        10: "",
        11: "",
        12: "",
        13: work_place,
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
    }
    segment = join_fields(template)
    return segment
