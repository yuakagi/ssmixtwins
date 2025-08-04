"""
Scripts to generate generic RXE segment for HL7 messages.

Example:
    RXE||100607002^アレピアチン１０倍散^HOT9|50||MG^ミリグラム^MR9P|PWD^散剤^MR9P||||1400|MG^ミリグラム ^MR9P||||2011070112345||||100^MG&ミリグラム&MR9P||OHP^外来処方^MR9P~OHI^院内処方^MR9P
    RXE||00^一般^99I02|510||ML^ミリリットル^MR9P|INJ^注射剤^MR9P|^５時間一定速度で^99IC6||||||||20090701001 ||||||IHP^入院処方^MR9P~FTP^定時処方^99I01|H1|102|ml/hr^ミリリッター／時間^ISO+|||||||||||||||||| 09A^^^^^N
"""

from ..objects import Admission
from ..utils import join_fields, make_message_type
from ..tables import merit_9_3


def generate_rxe(
    message_code: str,
    trigger_event: str,
    message_structure: str,
    drug_code: str,
    drug_name: str,
    drug_code_system: str,
    minimum_dose: str,
    dose_unit_code: str,
    dose_unit_name: str,
    dose_unit_code_system: str,
    dosage_form_code: str,  # Use merit_9_3 if you use this field.
    total_daily_dose: str,
    dispense_amount: str,
    dispense_unit_code: str,
    dispense_unit_name: str,
    dispense_unit_code_system: str,
    prescription_number: str,
    outpatient_department_code: str,
    admission: Admission | None,
) -> str:
    """
    Generates a sample PV1 segment in HL7 format.

    Args:
        message_code (str): The code for message type, e.g., 'ADT'.
        trigger_event (str): The trigger event type, e.g., 'A08'.
        message_structure (str): The message structure, e.g., 'ADT_A01'.
        drug_code (str): The code for the drug, e.g., "100607002".
        drug_name (str): The name of the drug, e.g., "アレピアチン１０倍散".
        drug_code_system (str): The code system for the drug, e.g., "HOT9".
        minimum_dose (str): The minimum dose of the drug, e.g., "50".
            For injections, this is water volume, not the drug itself.
            If this valu is not applicable, use '""'. This is not an empty string, but a visible "". Be careful.
        dose_unit_code (str): The code for the dose unit, e.g., "MG".
            If minimum_dose is '""', then this value should also be '""'.
        dose_unit_name (str): The name of the dose unit, e.g., "ミリグラム".
        dose_unit_code_system (str): The code system for the dose unit, e.g., "MR9P".
        dosage_form_code (str): The dosage form of the drug, e.g., "PWD^散剤^MR9P". Use merit_9_3.
        dispense_amount (str): The amount to be dispensed, e.g., "1400".
        dispense_unit_code (str): The code for the dispense unit, e.g., "MG".
        dispense_unit_name (str): The name of the dispense unit, e.g., "ミリグラム".
        dispense_unit_code_system (str): The code system for the dispense unit, e.g., "MR9P".
        prescription_number (str): The prescription number, e.g., "2011070112345". Must be < 20 characters, can contain characters and numbers.
        outpatient_department_code (str): The code for the outpatient department, e.g., "09A".
        admission (Admission | None): The admission object if the prescription is for an inpatient, or
    Returns:
        str: PV1 segment in HL7 format.

    Notes:
        Validation logics are expected to be handled outside this function.
    """
    # ====== Validation ======
    # NOTE: message_type is created for consistency with other segments, even if it is not used.
    message_type = make_message_type(message_code, trigger_event, message_structure)
    # Drug codes etc
    # NOTE: For injection orders (OMP-02), this is injection type code, not drug itself.
    drug_full = f"{drug_code}^{drug_name}^{drug_code_system}"
    # Dose unit
    # NOTE: MR9P is recommended, but it may be difficult to implement. So validation is skipped here.
    #       For injections, you can use ISO+, like ml^ml^ISO+.
    if dose_unit_code == '""':
        # NOTE: This value '""' is for drugs whose dose units are hard to define, like ointments.
        dose_unit_full = '""'  # <- Not empty string, but visible "".
    else:
        if (
            (dose_unit_code != "")
            or (dose_unit_name != "")
            or (dose_unit_code_system != "")
        ):
            dose_unit_full = (
                f"{dose_unit_code}^{dose_unit_name}^{dose_unit_code_system}"
            )
        else:
            dose_unit_full = ""
    # Dispense unit
    if dispense_unit_code == '""':
        dispence_unit_full = '""'  # <- Not empty string, but visible "".
    else:
        if (
            (dispense_unit_code != "")
            or (dispense_unit_name != "")
            or (dispense_unit_code_system != "")
        ):
            dispence_unit_full = (
                f"{dispense_unit_code}^{dispense_unit_name}^{dispense_unit_code_system}"
            )
        else:
            dispence_unit_full = ""
    # Dosage form
    if dosage_form_code != "":
        dosage_form_full = f"{dosage_form_code}^{merit_9_3[dosage_form_code]}^MR9P"
    else:
        dosage_form_full = ""
    # Total daily dose
    if total_daily_dose != "":
        # NOTE: Here, we use unit codes from dispence unit.
        total_daily_dose_full = f"{total_daily_dose}^{dispense_unit_code}&{dispense_unit_name}&{dispense_unit_code_system}"
    else:
        total_daily_dose_full = ""
    # Delivery place
    if admission is not None:
        # Inpatient
        delivery_place = f"{admission.admission_ward_code}^{admission.admission_room_code}^{admission.admission_bed_code}^^^N"
    else:
        # Outpatient
        delivery_place = f"{outpatient_department_code}^^^^^C"

    # ====== TEMPLAETE ======
    template = {
        0: "RXE",
        1: "",
        2: drug_full,
        # NOTE: Minimum doses should not be defined for drugs whose minimum doses are hard to define, like ointments.
        # But, because this RXE-3 is requried, you must set '""' for these drugs.
        # '""' is NOT empty string, it must be visble "". So, in python, you must use '""' not "".
        3: minimum_dose,
        4: "",  # Omitted for simplicity
        # NOTE: If minimum_dose is '""', then this field should also be '""'.
        5: dose_unit_full,
        6: dosage_form_full,
        7: "",  # Omitted for simplicity
        8: "",
        9: "",
        10: dispense_amount,  # R
        11: dispence_unit_full,  # R
        12: "",  # Omitted for simplicity
        13: "",  # Omitted for simplicity
        14: "",  # Omitted for simplicity
        15: prescription_number,  # R
        16: "",  # Omitted for simplicity
        17: "",  # Omitted for simplicity
        18: "",  # Omitted for simplicity
        19: total_daily_dose_full,
        20: "",
        21: "",  # Omitted for simplicity
        22: "",  # Omitted for simplicity
        23: "",
        24: "",
        25: "",  # Omitted for simplicity
        26: "",  # Omitted for simplicity
        27: "",  # Omitted for simplicity
        28: "",  # Omitted for simplicity
        29: "",  # Omitted for simplicity
        30: "",  # Omitted for simplicity
        31: "",  # Omitted for simplicity
        32: "",  # Omitted for simplicity
        33: "",  # Omitted for simplicity
        34: "",  # Omitted for simplicity
        35: "",  # Omitted for simplicity
        36: "",  # Omitted for simplicity
        37: "",  # Omitted for simplicity
        38: "",  # Omitted for simplicity
        39: "",  # Omitted for simplicity
        40: "",  # Omitted for simplicity
        41: "",  # Omitted for simplicity
        42: delivery_place,
        43: "",  # Omitted for simplicity
        44: "",  # Omitted for simplicity
    }
    segment = join_fields(template)
    return segment
