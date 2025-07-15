"""
Scripts to generate generic EVN segment for HL7 messages.

Example:
    EVN||201112202100|||||SEND001
"""

from ..tables import udt_0062
from ..utils import (
    join_fields,
    make_message_type,
    format_timestamp,
)


def generate_evn(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    transaction_time: str,
    planned_event_time: str,
    evn_reason_code: str,
    controller_id: str,
    evn_time: str,
) -> str:
    """
    Generates a sample EVN segment in HL7 format.
    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        planned_event_time (str): Planned event time in the format 'YYYYMMDD[HH[MM[SS]]]'.
        evn_reason_code (str): Reason code for the event, must be one of udt_0062.
        controller_id (str): Controller ID, if applicable.
        evn_time (str): Time of the event in the format 'YYYYMMDD[HH[MM[SS]]]'.
        transaction_time (str): Transaction time in the format 'YYYYMMDD[HH[MM[SS]]]'.
    Returns:
        str: EVN segment in HL7 format.
    """
    # ====== Validation ======
    # References
    can_use_evn_3 = [
        "ADT^A14",  # 入院予定
        "ADT^A27",  # 入院予定の取消
        "ADT^A16",  # 退院予定
        "ADT^A25",  # 退院予定の取消
        "ADT^A21",  # 外出泊実施
        "ADT^A22",  # 外出泊帰院実施
        "ADT^A52",  # 外出泊実施の取消
        "ADT^A53",  # 外出泊帰院実施の取消
    ]
    can_use_evn_6 = [
        "ADT^A15",  # 転送保留
        "ADT^A26",  # 転送保留の取消
        "ADT^A02",  # 患者転送
        "ADT^A12",  # 転送の取消
        "ADT^A21",  # 外出泊実施
        "ADT^A22",  # 外出泊帰院実施
        "ADT^A52",  # 外出泊実施の取消
        "ADT^A53",  # 外出泊帰院実施の取消
    ]
    # Validate timestamps
    transaction_time = format_timestamp(
        transaction_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=False
    )
    planned_event_time = format_timestamp(
        planned_event_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    evn_time = format_timestamp(
        evn_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    # Make message type
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    partial_message_type = "^".join([message_code, trigger_event])  # e.g., "ADT^A14"
    # Validate EVN-3
    if partial_message_type not in can_use_evn_3:
        if planned_event_time != "":
            raise ValueError(
                f"planned_event_time must not be provided for {partial_message_type}."
            )
    # Validate EVN-4
    if evn_reason_code != "":
        if evn_reason_code not in udt_0062:
            raise ValueError(f"evn_reason_code must be one of {list(udt_0062.keys())}")

    # Validate EVN-6
    if partial_message_type not in can_use_evn_6:
        if evn_time != "":
            raise ValueError("evn_time must not be provided for this message type.")

    # ====== TEMPLAETE ======
    template = {
        0: "EVN",
        1: "",
        2: transaction_time,
        3: planned_event_time,
        4: evn_reason_code,
        5: controller_id,
        6: evn_time,  # This is the time of the event, not the transaction time
        7: "SEND001",  # This is used as a dummy site
    }
    segment = join_fields(template)
    return segment
