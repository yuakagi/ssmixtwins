"""Module for OMP related messages

Example:
    RDE^O11 for prescription orders:
        MSH|^~\&|HIS123|SEND|GW|RCV|20110701224603.984||RDE^O11^RDE_O11|20110701000001|P|2.5||||||~ISO IR87||ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
        PID|0001||9999013^^^^PI||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19480405|M|||^^^^422-8033^JPN^H^静 岡県静岡市登呂１－３－５||^PRN^PH^^^^^^^^^054-000-0000|^WPN^PH^^^^^^^^^054-999-2455 |||||||||||||||||||20110601121551
        PV1|0001|O|01^^^^^C||||110^医師^一郎^^^^^^^L^^^^^I|||01
        ORC|NW|000000011000185||1|||||20110701103045|058^入力者^花子^^^^^^^L^^^^^I||110^医師^一郎 ^^^^^^^L^^^^^I| 10^^^^^C||||01^内科^99XY1|VMDOCX01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡市駿河区登呂3-1-1 |^^^^^^^^^^^054-284-9122||||||O^外来患者オーダ^HL70482
        RXE||108665201^ダーゼン錠（５mg)^HOT9|1||TAB^錠^MR9P|||||15|TAB^錠^MR9P||||2011070112345||||3^TAB&錠 &MR9P||OHP^外来処方^MR9P~OHI^院内処方^MR9P
        TQ1|1||1013044400000000&内服・経口・１日３回朝昼夕食後&JAMISDP01|||5^d|2011070100
        RXR|PO^口^HL70162
        ORC|NW|000000011000185||1|||||20110701103045|058^入力者^花子^^^^^^^L^^^^^I||110^医師^一郎^^^^^^^L^^^^^I |10^^^^^C||||01^内科^99XY1|VMDOCX01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡市駿河区登呂3-11|^^^^^^^^^^^054-284-9122||||||O^外来患者オーダ^HL70482
        RXE||110626901^パンスポリンＴ錠（１００mg)^HOT9|2||TAB^錠^MR9P|||||30|TAB^錠 ^MR9P||||2011070112345||||6^TAB&錠&MR9P||OHP^外来処方^MR9P~OHI^院内処方^MR9P TQ1|1||1013044400000000&内服・経口・１日３回朝昼夕食後&JAMISDP01|||5^d|2011070100
        RXR|PO^口^HL70162
        ORC|NW|000000011000185||2|||||20110701103045|058^入力者^花子^^^^^^^L^^^^^I||110^医師^一郎 ^^^^^^^L^^^^^I|10^^^^^C||||01^内科^99XY1|VMDOCX01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡市駿河 区登呂3-1-1|^^^^^^^^^^^054-284-9122||||||O^外来患者オーダ^HL70482
        RXE||100607002^アレピアチン１０倍散^HOT9|50||MG^ミリグラム^MR9P|PWD^散剤^MR9P||||1400|MG^ミリグラム ^MR9P||||2011070112345||||100^MG&ミリグラム&MR9P||OHP^外来処方^MR9P~OHI^院内処方^MR9P
        TQ1|1||1012040400000000&内服・経口・１日２回朝夕食後&JAMISDP01|||14^d|2011070100
        RXR|PO^口^HL70162

    RDE^O11 for injection orders:
        MSH|^~\&|HIS123|SEND|GW|RCV|20110701224603.984||RDE^O11^RDE_O11|20110701000001|P|2.5||||||~ISO IR87||ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
        PID|0001||9999013^^^^PI||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19480405|M|||^^^^422-8033^JPN^H^静 岡県静岡市登呂１－３－５||^PRN^PH^^^^^^^^^054-000-0000|^WPN^PH^^^^^^^^^054-999-2455
        PV1|0001|I|32^302^^^^N||||110^医師^一郎^^^^^^^L^^^^^I|||01
        ORC|NW|123456789012345||123456789012345_01_001|||||20110701012410|058^入力者^花子^^^^^^^L^^^^^I||110^医 師^一郎^^^^^^^L^^^^^I|32^302^^^^N||||01^内科^99XY1|PC01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡 市駿河区登呂3-1-1|^^^^^^^^^^^054-284-9122||||||I^入院患者オーダ^HL70482
        RXE||00^一般^99I02|510||ML^ミリリットル^MR9P|INJ^注射剤^MR9P|^５時間一定速度で^99IC6||||||||20110701001 ||||||IHP^入院処方^MR9P~FTP^定時処方^99I01|H1|102|ml/hr^ミリリッター／時間^ISO+|||||||||||||||||| 09A^^^^^N
        TQ1|1||||||201107010800|201107011300
        RXR|IV^静脈内^HL70162||IVP^点滴ポンプ^HL70164
        RXC|B|620007329^ソリタ－Ｔ３号輸液５００ｍＬ^HOT9|1|HON^本^MR9P
        RXC|A|620002559^アドナ注（静脈用）50mg^HOT9|1|AMP^アンプル^MR9P
        ORC|NW|123456789012345||123456789012345_01_002|||||20090701012410|058^入力者^花子^^^^^^^L^^^^^I||110^医 師^一郎^^^^^^^L^^^^^I|32^302^^^^N||||01^内科^99XY1|PC01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡 市駿河区登呂3-1-1|^^^^^^^^^^^054-284-9122||||||I^入院患者オーダ^HL70482
        RXE||00^一般^99I02|510||ML^ミリリットル^MR9P|INJ^注射剤^MR9P|^５時間一定速度で^99IC6||||||||20110701001 ||||||IHP^入院処方^MR9P~FTP^定時処方^99I01|H1|102|ml/hr^ミリリッター／時間^ISO+|||||||||||||||||| 09A^^^^^N
        TQ1|1||||||201107011300|201107011800
        RXR|IV^静脈内^HL70162||IVP^点滴ポンプ^HL70164
        RXC|B|620007329^ソリタ－Ｔ３号輸液５００ｍＬ^HOT9|1|HON^本^MR9P
        RXC|A|620002559^アドナ注（静脈用）50mg^HOT9|1|AMP^アンプル^MR9P
        ORC|NW|123456789012345||123456789012345_01_003|||||20090701012410|058^入力者^花子^^^^^^^L^^^^^I||110^医 師^一郎^^^^^^^L^^^^^I|32^302^^^^N||||01^内科^99XY1|PC01^^99XY2|||登呂病院|^^^^422-8033^JPN^^静岡県静岡 市駿河区登呂3-1-1|^^^^^^^^^^^054-284-9122||||||I^入院患者オーダ^HL70482
        RXE||00^一般^99I02|510||ML^ミリリットル^MR9P|INJ^注射剤^MR9P|^５時間一定速度で^99IC6||||||||20090701001 ||||||IHP^入院処方^MR9P~FTP^定時処方^99I01|H1|102|ml/hr^ミリリッター／時間^ISO+|||||||||||||||||| 09A^^^^^N
        TQ1|1||||||201107011800|201107012300
        RXR|IV^静脈内^HL70162||IVP^点滴ポンプ^HL70164
        RXC|B|620007329^ソリタ－Ｔ３号輸液５００ｍＬ^HOT9|1|HON^本^MR9P
        RXC|A|620002559^アドナ注（静脈用）50mg^HOT9|1|AMP^アンプル^MR9P
"""

import copy
from ...objects import (
    Allergy,
    Patient,
    Physician,
    Hospital,
    Admission,
    PrescriptionOrder,
    InjectionOrder,
)
from ...utils import (
    join_segments_dict,
)
from ...tables import (
    merit_9_4,
)
from ...segments import (
    generate_msh,
    generate_pid,
    generate_pv1,
    generate_al1,
    generate_orc,
    generate_rxe,
    generate_tq1,
    generate_rxc,
    generate_rxr,
)

# MSH [ PID [PV1] [{AL1}]] { orders}
RDE_O11_BASE = {
    "MSH": None,
    "PID": None,
    "PV1": None,
    "AL1": [],
    "orders": [],
}
# one prescription order: {ORC RXE {TQ1} {RXR}}
PRESCRIPTION_ORDER_BASE = {
    "ORC": None,  # One per order
    "RXE": None,  # One per order
    "TQ1": [],  # Can be multiple, usually one
    "RXR": [],  # Can be multiple, usually one
}

# one injection order: {ORC RXE {TQ1} {RXR} [{RXC}] [{OBX}] [{CTI}]}
INJECTION_ORDER_BASE = {
    "ORC": None,  # One per order
    "RXE": None,  # One per order
    "TQ1": [],  # Can be multiple, but expected to be one
    "RXR": [],  # Can be multiple, but expected to be one
    "RXC": [],  # Can be multiple, usually many
    "OBX": [],  # Can be multiple, usually absent. Can contain height, weight, eGFR, etc.
    "CTI": [],  # Can be multiple, usually absent.
}


def generate_rde_o11_base(
    message_time: str,
    message_id: str,
    patient: Patient,
    outpatient_department_code: str,  # Outpatient only, this is not used if admission is given
    admission: Admission | None,
    primary_physician: Physician,
) -> dict:
    """
    Generates a base structure for RDE^O11 message in HL7 format.

    Args:
        message_time (str): The time of the message in 'YYYYMMDDHHMMSS[.S[S[S[S]]]]' format.
        message_id (str): The unique identifier for the message.
        patient (Patient): A Patient object containing patient information.
        outpatient_department_code (str): The code for the outpatient department, e.g., "09A".
        admission (Admission | None): An Admission object if the patient is admitted, or None if the patient is an outpatient.
        primary_physician (Physician): A Physician object representing the
    """
    # === Input validation ===
    # NOTE: Args for PID segment are validated and cleaned in generate_pid function.
    # NOTE: Args for MSH segment are validated and cleaned in validate_msh_args function.
    # NOTE: Args for PV1 segment are validated and cleaned in generate_pv1 function.
    # MSH [ PID [PV1] [{AL1}] ]
    base = copy.deepcopy(RDE_O11_BASE)
    # MSH
    msh = generate_msh(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        message_time=message_time,
        message_id=message_id,
    )
    # PID
    pid = generate_pid(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        patient=patient,
        last_updated="",
    )
    # PV1
    pv1 = generate_pv1(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        outpatient_department_code=outpatient_department_code,
        discharge_time="",  # Not used
        discharge_disposition="",  # Not used
        admission_or_visit_time="",  # Not used
        primary_physician=primary_physician,
        admission=admission,
    )
    # Update the base with MSH, PID, and PV1 segments
    base["MSH"] = msh
    base["PID"] = pid
    base["PV1"] = pv1
    return base


def updata_rde_o11_base_allergy(
    base: dict,
    sequence_no: str,
    allergy: Allergy,
):
    """
    Updates the RDE^O11 base with allergy information.

    Args:
        base (dict): The base structure for RDE^O11 message.
        sequence_no (str): The sequence number for the allergy, e.g., "1".
        allergy (Allergy): An Allergy object containing allergy information.
    """
    # Validate inputs
    # NOTE: Args for AL1 segment are validated and cleaned in generate_al1 function.
    # AL1
    # Example: AL1|1|DA^薬剤アレルギー^HL70127|1^ペニシリン^99XYZ
    al1 = generate_al1(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        sequence_no=sequence_no,
        allergy=allergy,
    )
    # Update the base with the allergy information
    base["AL1"].append(al1)
    return base


def update_rde_o11_prescription_orders(
    base: dict,
    hospital: Hospital,
    admission: Admission | None,
    prescription_order: PrescriptionOrder,
):
    """
    Updates the RDE^O11 base with prescription orders.

    Args:
        base (dict): The base structure for RDE^O11 message.

    """
    # === Input validation & cleaning ===

    # Variables for the order
    dose_unit_name = merit_9_4[prescription_order.dose_unit_code]
    dose_unit_code_system = "MR9P"
    dispense_unit_name = merit_9_4[prescription_order.dispense_unit_code]
    dispense_unit_code_system = "MR9P"
    # one prescription order: {ORC RXE {TQ1} {RXR}}
    orc = generate_orc(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        order_control=prescription_order.order_control,
        requester_order_number=prescription_order.requester_order_number,
        filler_order_number=prescription_order.filler_order_number,
        requester_group_number=prescription_order.requester_group_number,  # e.g., "000000011000185_01_001"
        transaction_time=prescription_order.transaction_time,
        order_effective_time=prescription_order.order_effective_time,
        order_type=prescription_order.order_type,
        order_status="",  # Not implemented.
        hospital=hospital,
        requester=prescription_order.requester,
        enterer=prescription_order.enterer,
    )
    rxe = generate_rxe(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        drug_code=prescription_order.drug_code,
        drug_name=prescription_order.drug_name,
        drug_code_system=prescription_order.drug_code_system,
        minimum_dose=prescription_order.minimum_dose,
        dose_unit_code=prescription_order.dose_unit_code,
        dose_unit_name=dose_unit_name,
        dose_unit_code_system=dose_unit_code_system,
        dosage_form_code=prescription_order.dosage_form_code,
        dispense_amount=prescription_order.dispense_amount,
        dispense_unit_code=prescription_order.dispense_unit_code,
        dispense_unit_name=dispense_unit_name,
        dispense_unit_code_system=dispense_unit_code_system,
        prescription_number=prescription_order.prescription_number,
        outpatient_department_code=prescription_order.requester.department_code,
        admission=admission,
    )
    # TQ1
    tq1 = generate_tq1(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        sequence_no="1",  # Always "1", because currently only one TQ1 is supported for each order
        amount="",  # Not implemented
        repeat_pattern_code=prescription_order.repeat_pattern_code,
        repeat_pattern_name=prescription_order.repeat_pattern_name,
        repeat_pattern_code_system=prescription_order.repeat_pattern_code_system,
        duration=prescription_order.duration_in_days,
        duration_unit="d" if prescription_order.duration_in_days.isdigit() else "",
        start_time=prescription_order.start_time,
        end_time=prescription_order.end_time,
        total_occurrences=prescription_order.total_occurrences,
    )
    # RXR
    rxr = generate_rxr(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        route_code=prescription_order.route_code,
        route_device_code="",
    )
    # Add the order to the base
    order = copy.deepcopy(PRESCRIPTION_ORDER_BASE)
    order["ORC"] = orc
    order["RXE"] = rxe
    order["TQ1"].append(tq1)
    order["RXR"].append(rxr)
    base["orders"].append(order)

    return base


def update_rde_o11_injection_orders(
    base: dict,
    injection_order: InjectionOrder,
    hospital: Hospital,
    outpatient_department_code: str,  # Outpatient only, this is not used if admission is given
    admission: Admission | None,
):
    """
    Updates the RDE^O11 base with injection orders.

    Args:
        base (dict): The base structure for RDE^O11 message.
    """

    # one injection order: {ORC RXE {TQ1} {RXR} [{RXC}] [{OBX}] [{CTI}]}
    orc = generate_orc(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        order_control=injection_order.order_control,
        requester_order_number=injection_order.requester_order_number,
        filler_order_number=injection_order.filler_order_number,
        requester_group_number=injection_order.requester_group_number,
        transaction_time=injection_order.transaction_time,
        order_effective_time=injection_order.order_effective_time,
        requester=injection_order.requester,
        enterer=injection_order.enterer,
        hospital=hospital,
        order_type=injection_order.order_type,
        order_status="",  # Not implemented.
    )
    rxe = generate_rxe(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        drug_code=injection_order.injection_type_code,  # <- for injection orders, this is not drug code, but injection type code (such as "IV", etc)
        drug_name=injection_order.injection_type_name,
        drug_code_system=injection_order.injection_type_code_system,
        minimum_dose=injection_order.minimum_dose,
        dose_unit_code=injection_order.dose_unit_code,
        dose_unit_name=injection_order.dose_unit_name,
        dose_unit_code_system=injection_order.dose_unit_code_system,
        dosage_form_code="INJ",  # Set INJ always, compatible with MERIT9-3
        dispense_amount=injection_order.dispense_amount,
        dispense_unit_code=injection_order.dispense_unit_code,
        dispense_unit_name=injection_order.dispense_unit_name,
        dispense_unit_code_system=injection_order.dispense_unit_code_system,
        prescription_number=injection_order.prescription_number,
        outpatient_department_code=outpatient_department_code,
        admission=admission,
    )
    # TQ1
    tq1 = generate_tq1(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        sequence_no="1",  # Always "1", because currently only one TQ1 is supported for each order
        amount="",  # Not implemented
        repeat_pattern_code=injection_order.repeat_pattern_code,
        repeat_pattern_name=injection_order.repeat_pattern_name,
        repeat_pattern_code_system=injection_order.repeat_pattern_code_system,
        duration="",  # Not used for injection orders
        duration_unit="",  # Not used for injection orders
        start_time=injection_order.start_time,
        end_time=injection_order.end_time,
        total_occurrences=injection_order.total_occurrences,
    )
    # RXR
    rxr = generate_rxr(
        message_code="RDE",
        trigger_event="O11",
        message_structure="RDE_O11",
        route_code=injection_order.route_code,
        route_device_code=injection_order.route_device_code,  # Use udt_0164
    )
    # RXC
    rxcs = []  # Initialize RXC list
    for component in injection_order.components:
        # Generate RXC
        rxc = generate_rxc(
            message_code="RDE",
            trigger_event="O11",
            message_structure="RDE_O11",
            component_type=component.component_type,  # from h7t_0166, 'A' or 'B' only.
            component_code=component.component_code,
            component_name=component.component_name,
            component_code_system=component.component_code_system,
            component_quantity=component.component_quantity,
            component_unit_code=component.component_unit_code,
            component_unit_name=component.component_unit_name,
            component_unit_code_system=component.component_unit_code_system,
        )
        rxcs.append(rxc)  # Append to RXC list
    # Add the order to the base
    order = copy.deepcopy(INJECTION_ORDER_BASE)
    order["ORC"] = orc
    order["RXE"] = rxe
    order["TQ1"].append(tq1)
    order["RXR"].append(rxr)
    order["RXC"].extend(rxcs)  # Add all RXC components
    base["orders"].append(order)

    return base


def generate_rde_o11_prescription_message(
    message_time: str,
    message_id: str,
    outpatient_department_code: str,  #  Ignored if inpatient
    patient: Patient,
    admission: Admission | None,
    primary_physician: Physician,
    hospital: Hospital,
    orders: list[PrescriptionOrder],
):
    """
    Generates a sample RDE^O11 message in HL7 format.
    This is the main message for OMP-01

    Args:
        message_time (str): The time of the message in 'YYYYMMDDHHMMSS[.S[S[S[S]]]].
        message_id (str): The unique identifier for the message.
        outpatient_department_code (str): The code for the outpatient department, e.g., "09A".
        patient (Patient): A Patient object containing patient information.
        admission (Admission | None): An Admission object if the patient is admitted, or None if the patient is an outpatient.
        primary_physician (Physician): A Physician object representing the primary physician.
        hospital (Hospital): A Hospital object containing hospital information.
        orders (list[PrescriptionOrder]): A list of PrescriptionOrder objects containing prescription orders.

    Returns:
        str: A sample RDE^O11 message.
    """
    # Create base
    base = generate_rde_o11_base(
        message_time=message_time,
        message_id=message_id,
        patient=patient,
        outpatient_department_code=outpatient_department_code,
        admission=admission,
        primary_physician=primary_physician,
    )

    # Add allergy information
    for al_no, al in enumerate(patient.allergies, start=1):
        base = updata_rde_o11_base_allergy(
            base=base, sequence_no=str(al_no), allergy=al
        )

    # Add prescription orders
    for prescription_order in orders:
        base = update_rde_o11_prescription_orders(
            base=base,
            hospital=hospital,
            admission=admission,
            prescription_order=prescription_order,
        )

    # Return the base as a string (HL7 format)
    message = join_segments_dict(base)

    return message


def generate_rde_o11_injection_message(
    message_time: str,
    message_id: str,
    patient: Patient,
    admission: Admission | None,
    primary_physician: Physician,
    hospital: Hospital,
    outpatient_department_code: str,  # Ignored if inpatient
    orders: list[InjectionOrder],
):
    """
    Generates a sample RDE^O11 message in HL7 format for injection orders.
    This is the main message for OMP-02.

    Args:
        message_time (str): The time of the message in 'YYYYMMDDHHMMSS[.S[S[S[S]]]]'.
        message_id (str): The unique identifier for the message.
        patient (Patient): A Patient object containing patient information.
        admission (Admission | None): An Admission object if the patient is admitted, or None if the patient is an outpatient.
        primary_physician (Physician): A Physician object representing the primary physician.
        hospital (Hospital): A Hospital object containing hospital information.
        outpatient_department_code (str): The code for the outpatient department, e.g., "09A".
        orders (list[InjectionOrder]): A list of InjectionOrder objects containing injection orders.
    Returns:
        str: A sample RDE^O11 message.
    """
    # Create base
    base = generate_rde_o11_base(
        message_time=message_time,
        message_id=message_id,
        patient=patient,
        outpatient_department_code=outpatient_department_code,
        admission=admission,
        primary_physician=primary_physician,
    )
    # Add allergy information
    for al_no, al in enumerate(patient.allergies, start=1):
        base = updata_rde_o11_base_allergy(
            base=base, sequence_no=str(al_no), allergy=al
        )
    # Add injection orders
    for injection_order in orders:
        # Update
        base = update_rde_o11_injection_orders(
            base=base,
            injection_order=injection_order,
            hospital=hospital,
            outpatient_department_code=outpatient_department_code,
            admission=admission,
        )
    # Return the base as a string (HL7 format)
    message = join_segments_dict(base)

    return message
