"""
Scripts to generate generic IN1 segment for HL7 messages.

Example:
    IN1|1|67^国民健康保険退職者^JHSD0001|67999991|||||||||20091201|||||SEL^本人^HL70063
"""

import re
from ..objects import Insurance
from ..tables import udt_0063
from ..utils import join_fields, make_message_type


def generate_in1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    insurance: Insurance,
) -> str:
    """
    Generates a sample IN1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number, starting from 1.
        insurance (Insurance): An Insurance object containing the insurance details.
    Returns:
        str: IN1 segment in HL7 format.
    """
    # ====== Validation ======
    # Sequence number is from 1 ~
    assert (
        sequence_no != "0"
    ), "sequence_no must be a positive integer string, starting from 1."
    assert re.match(
        r"^\d+$", sequence_no
    ), "sequence_no must be a positive integer string."
    # Validate insurance relationship
    # References
    company_names = {
        "MI": "国民健康保険の保険者名",
        "PE": "公費名称(都道府県名含む)",
        "LI": "労働基準局などの名称",
        "TI": "自賠責保険会社名",
        "PS": "公務員災害補償基金名",
        "PI": "市または都道府県名",
        "OE": "自費",
        "OT": "保険名称",
    }
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)

    ins_plan_full = (
        f"{insurance.insurance_plan_code}^{insurance.insurance_class_name}^JHSD0001"
    )
    # Insurance group employer ID
    if insurance.insurance_classification in ["MI", "PI"]:
        # NOTE: Currently, we use a fixed value for this value, for simplicity.
        ins_group_emp_id = "123~1234567~01"
    else:
        ins_group_emp_id = ""
    # Relationship
    if insurance.insurance_relationship != "":
        ins_relationship_full = f"{insurance.insurance_relationship}^{udt_0063[insurance.insurance_relationship]}^HL70063"
    else:
        ins_relationship_full = ""

    # ====== TEMPLAETE ======
    template = {
        0: "IN1",
        1: sequence_no,
        2: ins_plan_full,
        3: insurance.insurance_number,
        4: insurance.insurance_company_name,
        5: "",
        6: "",
        7: "",
        8: "",
        9: "",
        10: ins_group_emp_id,
        11: "被保険者グループ雇用者名",  # Currently, this is a placeholder, for simplicity.
        12: insurance.insurance_plan_effective_date,
        13: insurance.insurance_plan_expiration_date,
        14: "",
        15: insurance.insurance_plan_type,
        16: "",
        17: ins_relationship_full,
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
        40: "",
        41: "",
        42: "",
        43: "",
        44: "",
        45: "",
        46: "",
        47: "",
        48: "",
        49: "",
        50: "",
        51: "",
        52: "",
        53: "",
    }
    segment = join_fields(template)
    return segment
