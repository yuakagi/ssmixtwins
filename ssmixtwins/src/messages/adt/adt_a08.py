"""Module for ADT-00 related messages

Example:
    MSH|^~\&|HIS123|SEND|GW|RCV|20111220224447.3399||ADT^A08^ADT_A01|20111220000001|P|2.5||||||~ISO IR87|| ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO EVN||201112202100|||||SEND001
    PID|0001||9999013||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19480405|M|||^^^^422-8033^JPN^H^静岡県静 岡市登呂１－３－５||^PRN^PH^^^^^^^^^054-000-0000~^EMR^PH^^^^^^^^^03-5999-9999|^WPN^PH^^^^^^^^^03-35999993 |||||||||||||||||||20111219121551
    NK1|1|患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P|SEL^本人^HL70063|^^^^422-8033^JPN^H^静岡県静岡市登呂１ －３－５~^^^^1050003^^B^東京都港区鹿ノ門６丁目３番３号|^PRN^PH^^^^^^^^^054-000-0000| ^WPN^PH^^^^^^^^^03-3599-9993|||||||鹿ノ門商事株式会社^D
    PV1|0001|I|32^302^1^^^N||||220^医師^一郎^^^^^^^L^^^^^I
    DB1|1|PT||Y
    OBX|1|NM|9N001000000000001^身長^JC10||167.8|cm^cm^ISO+|||||F
    OBX|2|NM|9N006000000000001^体重^JC10||63.5|kg^kg^ISO+|||||F
    OBX|3|CWE|5H010000001999911^血液型-ABO式^JC10||A^A^JSHR002||||||F
    OBX|4|CWE|5H020000001999911^血液型-Rh式^JC10||+^Rh+^JSHR002||||||F
    AL1|1|DA^薬剤アレルギー^HL70127|1^ペニシリン^99XYZ
    IN1|1|67^国民健康保険退職者^JHSD0001|67999991|||||||||20091201|||||SEL^本人^HL70063
"""

import copy
from ...utils import join_segments_dict
from ...objects import Patient, Physician, Admission
from ...segments import (
    generate_msh,
    generate_evn,
    generate_pid,
    generate_pv1,
    generate_nk1,
    generate_db1,
    generate_obx,
    generate_al1,
    generate_in1,
)

ADT_AO8_BASE = {
    "MSH": None,
    "EVN": None,
    "PID": None,
    "NK1": None,
    "PV1": None,
    "DB1": [],
    "OBX": [],
    "AL1": [],
    "IN1": [],
}


def generate_adt_a08_message(
    message_time: str,
    message_id: str,
    transaction_time: str,
    last_updated: str,
    patient: Patient,
    primary_physician: Physician,
    admission: Admission | None = None,
):
    """
    Generates a sample ADT^A08 message in HL7 format.
    This is the main message for ADT-00.

    Returns:
        str: A sample ADT^A08 message.
    """
    base = copy.deepcopy(ADT_AO8_BASE)
    # MSH
    # NOTE: Arguments are validated and cleaned in the generate_msh function.
    msh = generate_msh(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        message_time=message_time,
        message_id=message_id,
    )
    base["MSH"] = msh
    # EVN
    # NOTE: Arguments are validated and cleaned in the generate_evn function.
    evn = generate_evn(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        transaction_time=transaction_time,
        planned_event_time="",
        evn_reason_code="",
        controller_id="",
        evn_time="",
    )
    base["EVN"] = evn
    # PID
    # NOTE: Arguments are validated and cleaned in the generate_pid function.
    pid = generate_pid(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        last_updated=last_updated,
        patient=patient,
    )
    base["PID"] = pid
    # NK1
    # NOTE: Currently, only patients themselves are set
    # NOTE: Validation is done in the generate_nk1 function.
    nk1 = generate_nk1(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        sequence_no="1",
        first_name=patient.patient_first_name,
        last_name=patient.patient_last_name,
        first_name_kana=patient.patient_first_name_kana,
        last_name_kana=patient.patient_last_name_kana,
        relationship="SEL",
        patient_postal_code=patient.patient_postal_code,
        patient_address=patient.patient_address,
        home_phone=patient.home_phone,
        work_phone=patient.work_phone,
        work_place=patient.work_place,
    )
    base["NK1"] = nk1
    # PV1
    # NOTE: Arguments are validated and cleaned in the generate_pv1 function.
    pv1 = generate_pv1(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        outpatient_department_code=primary_physician.department_code,
        discharge_time="",  # Not applicable
        discharge_disposition="",  # Not applicable
        admission_or_visit_time="",  # Not applicable
        primary_physician=primary_physician,
        admission=admission,
    )
    base["PV1"] = pv1
    # DB1
    # NOTE: Currently, placeholders are set
    db1 = generate_db1(
        message_code="ADT",
        trigger_event="A08",
        message_structure="ADT_A01",
        sequence_no="1",
        disability_person_code="PT",
        disability_present="Y",
    )
    base["DB1"].append(db1)
    # OBX
    measurements = {}
    if patient.height != "":
        measurements["height"] = [
            "NM",
            "9N001000000000001",
            "身長",
            patient.height,
            "",
            "",
            "cm",
            "cm",
            "ISO+",
        ]
    if patient.weight != "":
        measurements["weight"] = [
            "NM",
            "9N006000000000001",
            "体重",
            patient.weight,
            "",
            "",
            "kg",
            "kg",
            "ISO+",
        ]
    if patient.abo_blood_type != "":
        measurements["abo"] = [
            "CWE",
            "5H010000001999911",
            "血液型-ABO式",
            patient.abo_blood_type,
            patient.abo_blood_type,
            "JSHR002",
            "",
            "",
            "",
        ]
    if patient.rh_blood_type != "":
        rh_name = "Rh+" if patient.rh_blood_type == "+" else "Rh-"
        measurements["rh"] = [
            "CWE",
            "5H020000001999911",
            "血液型-Rh式",
            patient.rh_blood_type,
            rh_name,
            "JSHR002",
            "",
            "",
            "",
        ]
    for idx, (key, v) in enumerate(measurements.items(), start=1):
        obx = generate_obx(
            message_code="ADT",
            trigger_event="A08",
            message_structure="ADT_A01",
            sequence_no=str(idx),
            value_type=v[0],
            observation_code=v[1],
            observation_name=v[2],
            observation_code_system="JC10",
            observation_sub_id="",
            observation_value=v[3],
            observation_value_code=v[4],
            observation_value_system=v[5],
            unit=v[6],
            unit_code=v[7],
            unit_code_system=v[8],
            status="F",
        )
        base["OBX"].append(obx)

    # [{AL1}]
    for al_no, al in enumerate(patient.allergies, start=1):
        al1 = generate_al1(
            message_code="ADT",
            trigger_event="A08",
            message_structure="ADT_A01",
            sequence_no=str(al_no),  # e.g., "1"
            allergy=al,  # Allergy object
        )
        base["AL1"].append(al1)

    # [{IN1}]
    for ins_no, insurance in enumerate(patient.insurances, start=1):
        # Generate IN1 segment for each insurance
        in1 = generate_in1(
            message_code="ADT",
            trigger_event="A08",
            message_structure="ADT_A01",
            sequence_no=str(ins_no),
            insurance=insurance,
        )
        base["IN1"].append(in1)

    # Join segments
    message = join_segments_dict(base)

    # Retrun
    return message
