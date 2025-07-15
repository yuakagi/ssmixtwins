"""
Scripts to generate generic PV1 segment for HL7 messages.

Example:
    PV1|0001|I|32^302^1^^^N||||220^医師^一郎^^^^^^^L^^^^^I
"""

from ..objects import Physician, Admission
from ..tables import udt_0112, udt_0069
from ..utils import (
    join_fields,
    make_message_type,
    format_timestamp,
)


def generate_pv1(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    outpatient_department_code: str,
    discharge_time: str,
    discharge_disposition: str,
    admission_or_visit_time: str,
    primary_physician: Physician | None = None,
    admission: Admission | None = None,
    set_id: str = "0001",  # Not used for RDE_o11, etc
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code: The code for message type, e.g., 'ADT'.
        trigger_event: The trigger event type, e.g., 'A01'.
        message_structure: The message structure, e.g., 'ADT_A01'.
        outpatient_department_code: The code for the outpatient department.
        discharge_time: The time of discharge in 'YYYYMMDD[HH[MM[SS
        discharge_disposition: The code for the discharge disposition.
        admission_or_visit_time: The time of admission or visit in 'YYYYMMDD[HH[MM[SS]]]' format.
        primary_physician: The primary physician object (optional).
        admission: The admission object (optional, required for inpatient).
        set_id: The set ID for the segment (default is '0001', not used for RDE_o11, etc).
    Returns:
        str: PV1 segment in HL7 format.
    """
    # ====== Validation ======
    if outpatient_department_code != "":
        assert (
            outpatient_department_code in udt_0069
        ), "Invalid outpatient_department_code."
    if discharge_disposition != "":
        assert discharge_disposition in udt_0112, "Invalid discharge_disposition."
    if set_id != "":
        assert set_id == "0001", "set_id must be '0001'."
    # Validate timestamps
    admission_or_visit_time = format_timestamp(
        admission_or_visit_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )
    discharge_time = format_timestamp(
        discharge_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
    )

    # References
    can_use_pv1_10 = ["A01", "A02", "A14", "A15"]
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Patient class (must be in udt_0004)
    patient_class = "I" if admission is not None else "O"
    # Join fields
    if patient_class == "I":
        # Inpatient
        patient_location = f"{admission.admission_ward_code}^{admission.admission_room_code}^{admission.admission_bed_code}^^^N"
        adm_physician_full = f"{admission.physician.physician_id}^{admission.physician.physician_last_name}^{admission.physician.physician_first_name}^^^^^^^L^^^^^I"
    else:
        # Outpatient
        if outpatient_department_code != "":
            patient_location = f"{outpatient_department_code}^^^^^C"
        else:
            patient_location = ""
        adm_physician_full = ""
    # Primary physican
    if primary_physician is None:
        primary_physician_full = ""
    else:
        primary_physician_full = f"{primary_physician.physician_id}^{primary_physician.physician_last_name}^{primary_physician.physician_first_name}^^^^^^^L^^^^^I"

    # ====== TEMPLAETE ======
    template = {
        0: "PV1",
        1: set_id,  # Set ID, not used for RDE_o11, etc
        2: patient_class,
        3: patient_location,
        4: "",
        5: "",
        6: "",  # <--- Patient's previous location. This is optional. But omitted for simplicity.
        7: primary_physician_full,
        8: "",
        9: "",
        10: (
            outpatient_department_code if trigger_event in can_use_pv1_10 else ""
        ),  # Max length is 3
        11: "",
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: adm_physician_full,
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
        36: discharge_disposition,  # Discharge only
        37: "",
        38: "",
        39: "",
        40: "",
        41: "",
        42: "",
        43: "",
        44: admission_or_visit_time,  # Visit time for ADT^A04, planned admission time for ADT^A05
        45: discharge_time,  # Discharge only
        46: "",
        47: "",
        48: "",
        49: "",
        50: "",
        51: "",
        52: "",
    }
    segment = join_fields(template)
    return segment
