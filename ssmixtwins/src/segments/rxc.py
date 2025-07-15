"""
Scripts to generate generic RXC segment for HL7 messages.

Example:
    RXC|B|620007329^ソリタ－Ｔ３号輸液５００ｍＬ^HOT9|1|HON^本^MR9P
    RXC|A|620002559^アドナ注（静脈用）50mg^HOT9|1|AMP^アンプル^MR9P
"""

from typing import Literal
from ..tables import h7t_0166
from ..utils import join_fields, make_message_type


def generate_rxc(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    component_type: Literal["B", "A"],
    component_code: str,
    component_name: str,
    component_code_system: str,
    component_quantity: str,
    component_unit_code: str,
    component_unit_name: str,
    component_unit_code_system: str,
) -> str:
    """
    Generates a sample RXC segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        component_type (Literal["B", "A"]): The type of component, 'B' for base or 'A' for additive.
        component_code (str): The code for the component, e.g., '620007329'.
        component_name (str): The name of the component, e.g., 'ソリタ－Ｔ３号輸液５００ｍＬ'.
        component_code_system (str): The code system for the component, e.g., 'HOT9'.
        component_quantity (str): The quantity of the component, must be a digit with a maximum length of 20 characters.
        component_unit_code (str): The code for the unit of the component, e.g., 'HON'.
        component_unit_name (str): The name of the unit of the component, e.g., '本'.
        component_unit_code_system (str): The code system for the unit of the component, e.g., 'MR9P'.


    Returns:
        str: RXC segment in HL7 format.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Component
    component_full = f"{component_code}^{component_name}^{component_code_system}"
    # Unit
    cmp_unit_full = (
        f"{component_unit_code}^{component_unit_name}^{component_unit_code_system}"
    )

    # ====== TEMPLAETE ======
    template = {
        0: "RXC",
        1: component_type,
        2: component_full,
        3: component_quantity,
        4: cmp_unit_full,
        5: "",  # Omitted for simplicity
        6: "",  # Omitted for simplicity
        7: "",  # Omitted for simplicity
        8: "",
        9: "",
    }
    segment = join_fields(template)
    return segment
