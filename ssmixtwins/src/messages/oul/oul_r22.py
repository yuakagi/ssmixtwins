"""
OUL_R22

Example:
MSH|^~\&|HIS123|SEND|GW|RCV|20111220103059.0000||OUL^R22^OUL_R22|20111220131032|P|2.5||||||~ISO IR87||ISO 2022-1994|SS-MIX2_1.20^SS-MIX2^1.2.392.200250.2.1.100.1.2.120^ISO
PID|0001||0001000052^^^^PI||患者^太郎^^^^^L^I~カンジャ^タロウ^^^^^L^P||19700405|M|||^^^^422-8033^JPN^H^ 静岡県静岡市登呂１－３－５
PV1|0001|O|01^^^^^C
SPM|1|000000001219001||023^血清^JC10|||||||||||||201112191500
OBR|1|000000011000354|000000001219001|E001^血液学的検査^99O03|||20111219|20111219||||||||607^医師一郎 ^^^^^^^^L^^^^^I||||||20111220103059
ORC|SC|000000011000354|000000001219001||CM||||20111220103059|||607^医師一郎 ^^^^^^^^L^^^^^I|01^^^^^C||||01^内科^99XY1||||登呂病院||||||||O^外来患者オーダ^HL70482
OBX|1|NM|3A016000002327102^A/G比^JC10||1.7||1.2-2.0||||F|||201112191500
OBX|2|NM|3A010000002327101^総蛋白^JC10||7.2|g/dl^g/dl^99XYZ|6.70-8.3||||F|||201112191500
OBX|3|NM|3A015000002327101^アルブミン^JC10||4.9|g/dl^g/dl^99XYZ|3.7-5.5||||F|||201112191500
"""

import copy
from ...objects import Patient, Physician, Hospital, Admission, LabResultSpecimen
from ...utils import join_segments_dict
from ...segments import (
    generate_msh,
    generate_pid,
    generate_pv1,
    generate_spm,
    generate_obr,
    generate_orc,
    generate_obx,
)

# MSH [PID] [PV1] {SPM {OBR [ORC] [{OBX}]}}
OUL_R22_BASE = {"MSH": None, "PID": None, "PV1": None, "specimens": []}

SPECIMEN_BASE = {
    # SPM {OBR [ORC] [{OBX}]}
    "SPM": [],  # Should be only one
    "OBR": [],  # Can be multiple, but should be one
    "ORC": [],  # Can be multiple, but should be one
    "OBX": [],  # Can be multiple, usually many, as many as test results.
}


def generate_oul_r22_base_message(
    message_time: str,
    message_id: str,
    patient: Patient,
    outpatient_department_code: str,
    admission: Admission | None,
    primary_physician: Physician,
):
    """
    Generates a base OUL^R22 message structure.

    Args:
        message_time (str): The time the message is generated. YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        message_id (str): Unique identifier for the message.
        patient (Patient): The patient object containing patient details.
        outpatient_department_code (str): The code for the outpatient department.
        admission (Admission | None): The admission object if the patient is admitted, otherwise None.
        primary_physician (Physician): The primary physician object.
    Raises:
        AssertionError: If any of the validation checks fail.
    Returns:
        dict: A base OUL^R22 message structure with MSH and PID segments.
    """
    # MSH
    # NOTE: Arguments are validated in the generate_msh function.
    msh = generate_msh(
        message_code="OUL",
        trigger_event="R22",
        message_structure="OUL_R22",
        message_time=message_time,
        message_id=message_id,
    )
    # PID
    # NOTE: Arguments are validated in the generate_pid function.
    pid = generate_pid(
        message_code="OUL",
        trigger_event="R22",
        message_structure="OUL_R22",
        patient=patient,
        last_updated="",  # Optional
    )
    # PV1
    # Validation is done in the generate_pv1 function.
    pv1 = generate_pv1(
        message_code="OUL",
        trigger_event="R22",
        message_structure="OUL_R22",
        outpatient_department_code=outpatient_department_code,
        primary_physician=primary_physician,
        admission=admission,
        admission_or_visit_time="",
        discharge_time="",
        discharge_disposition="",
    )
    base = copy.deepcopy(OUL_R22_BASE)
    base["MSH"] = msh
    base["PID"] = pid
    base["PV1"] = pv1
    return base


def update_oul_r22_base_message(
    base: dict, hospital: Hospital, specimens: list[LabResultSpecimen]
):
    """
    Updates the base OUL^R22 message with a new problem.
    Args:
        base (dict): The base OUL^R22 message structure.
        hospital (Hospital): The hospital object containing hospital details.
        specimens (list[LabResultSpecimen]): List of LabResultSpecimen objects containing specimen data.

    Returns:
        dict: Updated OUL^R22 message.
    """

    # SPM {ORC [OBR] [{OBX}]}
    for spm_no, specimen in enumerate(specimens, start=1):
        # Initialize SPM base
        spm_base = copy.deepcopy(SPECIMEN_BASE)
        # Update sequence number
        # NOTE: Validation is done in the generate_spm function.
        spm = generate_spm(
            message_code="OUL",
            trigger_event="R22",
            message_structure="OUL_R22",
            sequence_no=str(spm_no),
            specimen=specimen,
        )
        spm_base["SPM"].append(spm)
        # ORC
        orc = generate_orc(
            message_code="OUL",
            trigger_event="R22",
            message_structure="OUL_R22",
            order_control="SC",  # Always 'SC' for lab test result reports.
            order_type=specimen.order_type,
            order_status=specimen.order_status,
            transaction_time=specimen.transaction_time,
            order_effective_time=specimen.order_effective_time,
            requester_order_number=specimen.requester_order_number,
            filler_order_number=specimen.filler_order_number,
            requester_group_number="",  # Not implemented yet
            enterer=specimen.enterer,
            requester=specimen.requester,
            hospital=hospital,
        )
        spm_base["ORC"].append(orc)

        # OBR
        # NOTE: Many arguments are shared with ORC, therefore, ORC is generated first.
        #       Then, we use some of thethe validated arguments.
        obr = generate_obr(
            message_code="OUL",
            trigger_event="R22",
            message_structure="OUL_R22",
            # NOTE: This sequence number can be incremental under SPM, but currently we set 1 only for simplicity.
            #       (This means, one OBR per SPM.)
            #       If you need more than one OBR per SPM, you can change this to sequence_no.
            sequence_no="1",
            requester_order_number=specimen.requester_order_number,
            filler_order_number=specimen.filler_order_number,
            test_type_code=specimen.test_type_code,
            test_type_name=specimen.test_type_name,
            test_type_code_system=specimen.test_type_code_system,
            sampled_time=specimen.sampled_time,
            sampling_finished_time=specimen.sampling_finished_time,
            requester=specimen.requester,
            reported_time=specimen.reported_time,
            parent_result=specimen.parent_result,
        )
        spm_base["OBR"].append(obr)

        # OBX
        for res_no, result in enumerate(specimen.results, start=1):
            obx = generate_obx(
                message_code="OUL",
                trigger_event="R22",
                message_structure="OUL_R22",
                sequence_no=str(res_no),
                value_type=result.value_type,
                observation_code=result.observation_code,
                observation_name=result.observation_name,
                observation_code_system=result.observation_code_system,
                observation_sub_id=result.observation_sub_id,
                observation_value=result.observation_value,
                observation_value_code=result.observation_value_code,
                observation_value_system=result.observation_value_system,
                unit=result.unit,
                unit_code=result.unit_code,
                unit_code_system=result.unit_code_system,
                status=result.status,
            )
            # Add to the base message
            spm_base["OBX"].append(obx)

        # Add to the base message
        base["specimens"].append(spm_base)

    return base


# ⭐️ This is the main function ⭐️
def generate_oul_r22_message(
    message_time: str,
    message_id: str,
    outpatient_department_code: str,
    patient: Patient,
    admission: Admission | None,
    primary_physician: Physician,
    hospital: Hospital,
    specimens: list[LabResultSpecimen],
):
    """
    Generates a sample OUL^R22 message in HL7 format.
    This is the main message for OML-11.

    Args:
        message_time (str): The time the message is generated. YYYYMMDDHHMMSS[.S[S[S[S]]]] format.
        message_id (str): Unique identifier for the message.
        outpatient_department_code (str): The code for the outpatient department.
        patient (Patient): The patient object containing patient details.
        admission (Admission | None): The admission object if the patient is admitted, otherwise None.
        primary_physician (Physician): The primary physician object.
        hospital (Hospital): The hospital object containing hospital details.
        specimens (list[LabResultSpecimen]): List of LabResultSpecimen objects containing specimen data.
    Returns:
        str: A sample OUL^R22 message in HL7 format.
    """
    # Base
    base_message = generate_oul_r22_base_message(
        message_time=message_time,
        message_id=message_id,
        patient=patient,
        outpatient_department_code=outpatient_department_code,
        admission=admission,
        primary_physician=primary_physician,
    )
    # Update with specimens and observations
    base_message = update_oul_r22_base_message(
        base=base_message,
        hospital=hospital,
        specimens=specimens,
    )
    # Finalize the message
    message = join_segments_dict(base_message)
    return message
