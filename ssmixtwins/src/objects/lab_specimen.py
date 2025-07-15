"""
Objects for lab test resukts.
"""

from typing import Literal
from .physician import Physician
from ..tables import h7t_0038, h7t_0085, h7t_0125, jlac10_test_types, jlac10_specimens
from ..utils import format_timestamp, generate_random_timedelta, to_datetime_anything
from ..config import BASE_TIMESTAMP_FORMAT


class LabResult:
    """
    This class represents a laboratory test result.
    """

    def __init__(
        self,
        value_type: str,  # h7t_0125
        observation_code: str,
        observation_name: str,
        observation_code_system: str,
        observation_sub_id: str,
        observation_value: str,
        observation_value_code: str,  # Usually not used
        observation_value_system: str,  # Usually not used
        unit: str,
        unit_code: str,
        unit_code_system: str,
        status: str,  # h7t_0085
    ):
        """
        Initializes an object with the provided parameters.

        Args:
        """
        # Validate
        assert (
            value_type in h7t_0125
        ), f"value_type must be one of {list(h7t_0125.keys())}, got '{value_type}'."
        assert observation_code != "", "observation_code must not be empty."
        assert (
            observation_code_system != ""
        ), "observation_code_system must not be empty."
        assert (
            len(observation_code) + len(observation_name) + len(observation_code_system)
            < 240
        ), "observation_code, observation_name, and observation_code_system combined must be less than 240 characters."
        assert (
            len(observation_sub_id) <= 20
        ), "observation_sub_id must be less than or equal to 20 characters."
        assert observation_value != "", "observation_value must not be empty."
        assert (
            len(observation_value)
            + len(observation_value_code)
            + len(observation_value_system)
            < 65536
        ), "observation_value, observation_value_code, and observation_value_system combined must be less than 65536 characters."
        assert (
            len(unit) + len(unit_code) + len(unit_code_system) < 240
        ), "unit, unit_code, and unit_code_system combined must be less than 240 characters."
        assert (
            status in h7t_0085
        ), f"status must be one of {list(h7t_0085.keys())}, got '{status}'."

        # Set attributes
        self.value_type = value_type
        self.observation_code = observation_code
        self.observation_name = observation_name
        self.observation_code_system = observation_code_system
        self.observation_sub_id = observation_sub_id
        self.observation_value = observation_value
        self.observation_value_code = observation_value_code
        self.observation_value_system = observation_value_system
        self.unit = unit
        self.unit_code = unit_code
        self.unit_code_system = unit_code_system
        self.status = status  # h7t_0085


class LabResultSpecimen:
    """
    This class represents a specimen for laboratory test results.
    """

    def __init__(
        self,
        specimen_id: str,
        specimen_code: str,
        specimen_name: str,
        specimen_code_system: str,
        sampled_time: str,
        test_type_code: str,
        test_type_name: str,
        test_type_code_system: str,
        sampling_finished_time: str,
        reported_time: str,
        parent_result: str,  # OBR-26
        results: list[LabResult],
        # ORC fields below
        # Because ORC implementation varies by the message type, some ORC fields are included here.
        order_status: str,  # h7t_0038,
        transaction_time: str,
        order_effective_time: str,
        requester_order_number: str,
        filler_order_number: str,
        order_type: Literal["I", "O"],
        enterer: Physician,
        requester: Physician,
    ):
        """
        Initializes an object with the provided parameters.

        Args:
            specimen_id (str): The ID of the specimen, must be a non-empty string of 80 characters or less.
            specimen_code (str): The code of the specimen, must be a non-empty string.
            specimen_name (str): The name of the specimen, must be a non-empty string.
            specimen_code_system (str): The code system of the specimen, must be a non-empty string.
            sampled_time (str): The time when the specimen was sampled, formatted as YYYYMMDD[HH[MM[SS]]].
            test_type_code (str): The code for the test type, must not be empty.
            test_type_name (str): The name of the test type, must not be empty.
            test_type_code_system (str): The code system for the test type, must not be empty.
            sampling_finished_time (str): The time when the sampling was finished, formatted as YYYYMMDD[HH[MM]].
            reported_time (str): The time when the result was reported, formatted as YYYYMMDDHHMMSS.
            parent_result (str): The parent result for the OBR-26 field, must be less than 400 characters long.
            results (list[LabResults]): A list of LabResults objects representing the results of the specimen.

            NOTE: Arguments below are ORC fields. These arguments are expected to be shared with other orders in the same file.
            order_status (str): The status of the order, must be one of the values defined in h7t_0038.
            transaction_time (str): The time of the transaction, formatted as YYYYMMDDHHMMSS, can be null.
            order_effective_time (str): The effective time of the order, formatted as YYYYMMDD[HH[MM[SS]]], can be null.
            requester_order_number (str): The order number from the requester, must be a number shorter than 16 characters long.
                NOTE: This is ORC-2, used for file naming. This value is usually shared with other orders saved in the same file.
            filler_order_number (str): The order number from the filler, must be a number shorter than 16 characters long, can be empty.
            order_type (Literal["I", "O"]): The type of the order, must be 'I' for inpatient or 'O' for outpatient.
            enterer (Physician): The physician who entered the order, must be a Physician object.
            requester (Physician): The physician who requested the order, must be a Physician object.

        Raises:
            AssertionError: If any of the input parameters do not meet the specified requirements.

        """
        # Validate and clean args
        # SPM things
        assert (specimen_id != "") and (
            len(specimen_id) <= 80
        ), "specimen_id must be a non-empty string of 80 characters or less."
        assert (
            (specimen_code != "")
            and (specimen_name != "")
            and (specimen_code_system != "")
        ), "specimen_code, specimen_name, and specimen_code_system must be non-empty strings."
        assert (
            len(specimen_code) + len(specimen_name) + len(specimen_code_system) < 240
        ), "Combined length of specimen_code, specimen_name, and specimen_code_system must be less than 240 characters."
        sampled_time = format_timestamp(sampled_time, format="YYYYMMDD[HH[MM[SS]]]")
        # OBR things
        assert test_type_code != "", "test_type_code must not be empty."
        assert test_type_name != "", "test_type_name must not be empty."
        assert test_type_code_system != "", "test_type_code_system must not be empty."
        assert (
            len(test_type_code) + len(test_type_name) + len(test_type_code_system) < 240
        ), "test_type_code, test_type_name, and test_type_code_system combined must be less than 240 characters."
        assert (
            len(parent_result) < 400
        ), "parent_result must be less than 400 characters long."
        # ORC things
        # NOTE: ORC-5 (order status) is usually optional, but required for lab test results.
        assert (
            order_status in h7t_0038
        ), f"order_status must be one of {list(h7t_0038.keys())}, got '{order_status}'."
        assert order_type in [
            "O",
            "I",
        ], f"order_type must be 'O' for outpatient or 'I' for inpatient, got '{order_type}'."
        assert (requester_order_number.isdigit()) and len(
            requester_order_number
        ) <= 15, f"requester_order_number must be a number shorter than 16 characters long, got '{requester_order_number}'."
        if filler_order_number != "":
            # NOTE: This part in PPR^ZD1 is ambiguous in the guideline. Assume it is 15-digit number.
            assert (filler_order_number.isdigit()) and len(
                filler_order_number
            ) <= 16, f"filler_order_number must be a number shorter than 16 characters long, got '{filler_order_number}'."

        # Objects
        assert isinstance(enterer, Physician), "enterer must be a Physician object."
        assert isinstance(requester, Physician), "requester must be a Physician object."
        assert isinstance(
            results, list
        ), "results must be a list of LabResults objects."
        for result in results:
            assert isinstance(
                result, LabResult
            ), "Each result must be a LabResult object."
        # Clean args
        requester_order_number = requester_order_number.zfill(15)
        if filler_order_number != "":
            filler_order_number = filler_order_number.zfill(15)
        # Timestamps
        transaction_time = format_timestamp(
            transaction_time, format="YYYYMMDDHHMMSS", allow_null=True
        )  # Allow null (ORC-9)
        order_effective_time = format_timestamp(
            order_effective_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # Allow null (ORC-15)
        sampled_time = format_timestamp(
            sampled_time, format="YYYYMMDD[HH[MM]]", allow_null=True
        )
        # NOTE: If sampling is very quick, you can set the same time for sampled_time and sampling_finished_time.
        sampling_finished_time = format_timestamp(
            sampling_finished_time,
            format="YYYYMMDD[HH[MM]]",
            allow_null=True,
        )
        reported_time = format_timestamp(
            reported_time, format="YYYYMMDDHHMMSS", allow_null=True
        )

        # Action time is required in prescription orders.
        # Set attributes
        self.specimen_id = specimen_id
        self.specimen_code = specimen_code
        self.specimen_name = specimen_name
        self.specimen_code_system = specimen_code_system
        self.sampled_time = sampled_time
        self.test_type_code = test_type_code
        self.test_type_name = test_type_name
        self.test_type_code_system = test_type_code_system
        self.sampling_finished_time = sampling_finished_time
        self.reported_time = reported_time
        self.parent_result = parent_result  # OBR-26
        self.results = results

        # ORC fields below
        self.order_type = order_type
        self.order_control = "SC"  # h7t_0119, always 'SC' for lab test results.
        self.order_status = order_status
        self.requester_order_number = requester_order_number
        self.filler_order_number = filler_order_number
        self.transaction_time = transaction_time
        self.order_effective_time = order_effective_time
        self.enterer = enterer
        self.requester = requester


def generate_random_lab_result(
    observation_sub_id: str,
    observation_code: str,
    observation_name: str,
    observation_code_system: str,
    observation_value: str,
    unit: str,
) -> LabResult:
    """
    Generates a random LabResult object for testing purposes.
    """
    # Value type check
    try:
        _ = float(observation_value)
        value_type = "NM"  # Numeric value

    except ValueError:
        value_type = "ST"  # String value

    return LabResult(
        value_type=value_type,
        observation_code=observation_code,
        observation_name=observation_name,
        observation_code_system=observation_code_system,
        observation_sub_id=observation_sub_id,
        observation_value=observation_value,
        observation_value_code="",  # For simplicity, we set it to empty.
        observation_value_system="",  # For simplicity, we set it to empty.
        unit=unit,
        unit_code=unit,  # For simplicity, we use the same value for unit_code.
        unit_code_system=(
            "99XYZ" if unit != "" else ""
        ),  # Set local code system for simplicity.
        status="F",  # Only 'F' (final) is supported for lab results in this implementation.
    )


def generate_random_lab_result_specimen(
    specimen_id: str,
    specimen_code: str,
    sampled_time: str,
    requester_order_number: str,  # ORC-2
    filler_order_number: str,  # ORC-3
    is_admitted: bool,
    enterer: Physician,
    requester: Physician,
    results: list[LabResult],
) -> LabResultSpecimen:
    """
    Generates a random LabResultSpecimen object for testing purposes.
    """
    # Time
    sampling_finished_time = sampled_time  # For simplicity, we set the same time for sampled_time and sampling_finished_time.
    sampled_time_dt = to_datetime_anything(sampled_time)
    reported_time = (sampled_time_dt + generate_random_timedelta(30, 180)).strftime(
        BASE_TIMESTAMP_FORMAT
    )
    transaction_time = reported_time
    order_effective_time = (
        sampled_time_dt
        - generate_random_timedelta(
            10, 1440
        )  # 30 minutes to 24 hours before sampled_time
    ).strftime(BASE_TIMESTAMP_FORMAT)
    # Detect test type
    first_letters = {}
    for r in results:
        first_letter = r.observation_code[0]
        if first_letter not in first_letters:
            first_letters[first_letter] = 1
        else:
            first_letters[first_letter] += 1
    most_common_first_letter = max(first_letters, key=first_letters.get)

    if most_common_first_letter in jlac10_test_types:
        test_type_code = most_common_first_letter
        test_type_name = jlac10_test_types[most_common_first_letter]
        test_type_code_system = "JC10"
    else:
        # If the first letter is not in JLAC10, we use a default value.
        test_type_code = "8"
        test_type_name = "その他の検体検査"
        test_type_code_system = "JC10"

    # Specimen name and code
    if specimen_code in jlac10_specimens:
        specimen_name = jlac10_specimens[specimen_code]
        specimen_code_system = "JC10"
    else:
        specimen_code_system = "99XYZ"  # Local code system
        specimen_name = "不明な検体"  # Default name for other specimens

    return LabResultSpecimen(
        specimen_id=specimen_id,
        specimen_code=specimen_code,
        specimen_name=specimen_name,
        specimen_code_system=specimen_code_system,
        sampled_time=sampled_time,
        test_type_code=test_type_code,
        test_type_name=test_type_name,
        test_type_code_system=test_type_code_system,
        sampling_finished_time=sampling_finished_time,
        reported_time=reported_time,
        parent_result="",  # Not used
        results=results,
        order_status="CM",  # CM only
        transaction_time=transaction_time,
        order_effective_time=order_effective_time,
        requester_order_number=requester_order_number,
        filler_order_number=filler_order_number,
        order_type="I" if is_admitted else "O",  # 'I' for inpatient, 'O' for outpatient
        enterer=enterer,
        requester=requester,
    )
