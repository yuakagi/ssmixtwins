"""
Scripts to generate generic PID segment for HL7 messages.

Example:
    PID|0001||9999013||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19480405|M|||^^^^422-8033^JPN^H^静岡県静 岡市登呂１－３－５||^PRN^PH^^^^^^^^^054-000-0000~^EMR^PH^^^^^^^^^03-5999-9999|^WPN^PH^^^^^^^^^03-35999993 |||||||||||||||||||20111219121551
"""

# NOTE: PID segment is constant across various messages. Therefore, validation logics are included in this module.

from ..objects import Patient
from ..utils import (
    join_fields,
    make_message_type,
    format_timestamp,
)


def generate_pid(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    last_updated: str,
    patient: Patient,
) -> str:
    """
    Generates a sample PID segment in HL7 format.
    Args:
        message_code: The code for message type, e.g., 'ADT'.
        trigger_event: The trigger event type, e.g., 'A08'.
        message_structure: The message structure, e.g., 'ADT_A01'.
        last_updated: The last updated time of the patient information in 'YYYYMMDDHHMMSS' format.
        patient (Patient): The patient object containing patient information.
    Returns:
        str: PID segment in HL7 format.
    """
    # ====== Validation ======
    # Format time strings
    last_updated = format_timestamp(
        last_updated, format="YYYYMMDDHHMMSS", allow_null=True
    )
    # References
    must_use_pid33 = ["ADT^A08"]
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    partial_message_type = "^".join([message_code, trigger_event])  # e.g., "ADT^A08"
    # Last updated time
    if partial_message_type in must_use_pid33:
        assert (
            last_updated != ""
        ), f"last_updated must be provided for {partial_message_type}."

    # ====== TEMPLAETE ======
    template = {
        0: "PID",
        1: "0001",
        2: "",
        3: patient.patient_id,
        4: "",
        5: f"{patient.patient_last_name}^{patient.patient_first_name}^^^^L^I~{patient.patient_last_name_kana}^{patient.patient_first_name_kana}^^^^^L^P",
        6: "",
        7: patient.dob,  # Date of birth
        8: patient.sex,
        9: "",
        10: "",
        11: f"^^^^{patient.patient_postal_code}^JPN^H^{patient.patient_address}",
        12: "",
        13: f"^PRN^PH^^^^^^^^^{patient.home_phone}",
        14: f"^WPN^PH^^^^^^^^^{patient.work_phone}",
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
        33: last_updated,
        34: "",
        35: "",
        36: "",
        37: "",
        38: "",
        39: "",
    }
    segment = join_fields(template)
    return segment
