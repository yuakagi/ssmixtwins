"""
Scripts to generate generic SPM segment for HL7 messages.

Example:
    SPM|1|000000001219001||023^血清^JC10|||||||||||||201112191500
"""

from ..objects import LabResultSpecimen
from ..utils import join_fields, make_message_type


def generate_spm(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    sequence_no: str,
    specimen: LabResultSpecimen,
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        sequence_no (str): Sequence number for the SPM segment, starting from 1.
        specimen (LabResultSpecimen): An object containing specimen details, including:
    Returns:
        str: SPM segment in HL7 format.
    """
    # ====== Validation ======
    assert (
        (sequence_no != "") and (sequence_no.isdigit()) and (len(sequence_no) <= 4)
    ), "sequence_no must be a non-empty string of digits with a maximum length of 4."
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Specimen code
    specimen_full = f"{specimen.specimen_code}^{specimen.specimen_name}^{specimen.specimen_code_system}"

    # ====== TEMPLAETE ======
    template = {
        0: "SPM",
        1: sequence_no,
        2: specimen.specimen_id,
        3: "",
        4: specimen_full,
        5: "",
        6: "",
        7: "",
        8: "",  # Omitted for simplicity
        9: "",
        10: "",
        11: "",
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: specimen.sampled_time,
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
    }
    segment = join_fields(template)
    return segment
