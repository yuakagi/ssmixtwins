"""
Scripts to generate generic OBX segment for HL7 messages.

Example:
    OBX|1|NM|9N001000000000001^身長^JC10||167.8|cm^cm^ISO+|||||F
    OBX|2|NM|9N006000000000001^体重^JC10||63.5|kg^kg^ISO+|||||F
    OBX|3|CWE|5H010000001999911^血液型-ABO式^JC10||A^A^JSHR002||||||F
    OBX|4|CWE|5H020000001999911^血液型-Rh式^JC10||+^Rh+^JSHR002||||||F
"""

from ..tables import h7t_0125, h7t_0085
from ..utils import join_fields, make_message_type


def generate_obx(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    value_type: str,
    observation_code: str,
    observation_name: str,
    observation_code_system: str,
    observation_sub_id: str,
    observation_value: str,
    observation_value_code: str,
    observation_value_system: str,
    unit: str,
    unit_code: str,
    unit_code_system: str,
    status: str,
) -> str:
    """
    Generates a sample OBX segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the OBX segment, starting from 1.
        value_type (str): The type of value, must be one of h7t_0125.
        observation_code (str): Observation code, e.g., "9N001000000000001" for height.
        observation_name (str): Observation name, e.g., "身長" for height.
        observation_code_system (str): Code system for the observation, e.g., "JC10".
        observation_sub_id (str): Sub-ID for the observation, if applicable.
        observation_value_code (str): Code for the observation value, if applicable.
        observation_value (str): Name of the observation value, e.g., "167.8" for height.
            This is the main value and can be a numeric value or a coded value.
        observation_value_system (str): Code system for the observation value, if applicable.
        unit (str): Unit of measurement for the observation value, e.g., "cm".
        unit_code (str): Code for the unit of measurement, if applicable.
        unit_code_system (str): Code system for the unit of measurement, if applicable.
        status (str): Status of the observation, must be one of h7t_0085.
    Returns:
        str: OBX segment in HL7 format.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Value type
    # NOTE: "CWE" for blood type, "NM" for numeric values like body weights and heigt, etc.
    if value_type not in h7t_0125:
        if value_type != "":
            raise ValueError(
                f"value_type must be one of {list(h7t_0125.keys())}, got '{value_type}'."
            )
    # Observation code
    obs_identifier = f"{observation_code}^{observation_name}^{observation_code_system}"
    # Value
    # NOTE: Value can be given in two ways:
    # 1. observation value with codes, code system: e.g., "A^A^JSHR002" for blood type A
    # 2. observation value alone: e.g., "167.8" for height
    if (observation_value_code != "") or (observation_value_system != ""):
        obs_value_full = (
            f"{observation_value_code}^{observation_value}^{observation_value_system}"
        )
    else:
        obs_value_full = observation_value
    # Unit
    if unit != "":
        if (unit_code != "") or (unit_code_system != ""):
            unit_full = f"{unit_code}^{unit}^{unit_code_system}"
        else:
            unit_full = unit
    else:
        unit_full = ""
    # Status
    if status != "":
        if status not in h7t_0085:
            raise ValueError(
                f"status must be one of {list(h7t_0085.keys())}, got '{status}'."
            )

    # ====== TEMPLAETE ======
    template = {
        0: "OBX",
        1: sequence_no,
        2: value_type,
        3: obs_identifier,
        4: observation_sub_id,
        5: obs_value_full,
        6: unit_full,
        7: "",
        8: "",
        9: "",
        10: "",
        11: status,
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: "",
        18: "",
        19: "",
    }
    segment = join_fields(template)
    return segment
