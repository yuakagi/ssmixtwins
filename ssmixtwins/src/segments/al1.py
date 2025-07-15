"""
Scripts to generate generic AL1 segment for HL7 messages.

Example:
    AL1|1|DA^薬剤アレルギー^HL70127|1^ペニシリン^99XYZ
"""

import re
from ..objects import Allergy
from ..tables import udt_0127
from ..utils import join_fields, make_message_type


def generate_al1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    allergy: Allergy,
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the allergy record, starting from 1.
        allergy (Allergy): An Allergy object containing the allergy details.
    Returns:
        str: AL1 segment in HL7 format.
    """
    # ====== Validation ======
    # Sequence number is from 1 ~
    assert (
        sequence_no != "0"
    ), "sequence_no must be a positive integer string, starting from 1."
    assert re.match(
        r"^\d+$", sequence_no
    ), "sequence_no must be a positive integer string."
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)

    # Allergy type
    al_type_name = udt_0127[allergy.allergy_type_code]
    allergy_type_full = f"{allergy.allergy_type_code}^{al_type_name}^HL70127"
    # Allergen code
    # Use HOT9 for drugs, JLAC10 for food etc.
    # Something like '99XYZ' for local code system
    allergen_full = f"{allergy.allergen_code}^{allergy.allergen_name}^{allergy.allergen_code_system}"

    # ====== TEMPLAETE ======
    template = {
        0: "AL1",
        1: sequence_no,
        2: allergy_type_full,
        3: allergen_full,
        4: "",
        5: "",
        6: "",
    }
    segment = join_fields(template)
    return segment
