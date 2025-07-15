"""
This object is for PPR^ZD1 message only.
"""

import random
from typing import Literal
from .physician import Physician
from ..tables import jhsd_0004, h7t_0119
from ..utils import format_timestamp, to_datetime_anything, generate_random_timedelta
from ..config import BASE_TIMESTAMP_FORMAT


class Problem:
    def __init__(
        self,
        action_code: str,  # Nonnull
        action_time: str,  # BASE_TIMESTAMP_FORMAT, nonnullable
        dx_code: str,  # Nonnull
        dx_name: str,  # Nullable
        dx_code_system: str,  # Nonnull, usually MDCDX2
        prb_instance_id: str,  # Nonnull, 60 characters or less
        date_of_diagnosis: str,  # Nullable
        expected_time_solved: str,  # Nullable
        time_solved: str,  # Nullable
        icd10_code: str,  # Nullable
        icd10_name: str,  # Nullable
        diagnosis_type: str,  # jhsd_0004
        provisional: Literal["1", ""],
        time_of_onset: str,  # Nullable
        # ORC fields below
        # Because ORC implementation varies by the message type, some ORC fields are included here.
        transaction_time: str,  # Nonnull
        order_effective_time: str,  # Nullable
        order_control: str,  # h7t_0119, Nonnull
        requester_order_number: str,  # Nonnull
        filler_order_number: str,  # Nullable
        order_type: Literal["I", "O"],
        enterer: Physician,
        requester: Physician,
    ):
        """Initializes the Problem object with the provided attributes.

        Args:
            action_code (str): The action code, must be one of ['AD', 'CD', 'DE', 'LI', 'UC', 'UN', 'UP'].
            action_time (str): The time of the action in 'YYYYMMDD[HH[MM[SS]]' format.
            dx_code (str): The diagnosis code, must not be empty.
            dx_name (str): The diagnosis name, must not be empty.
            dx_code_system (str): The code system for the diagnosis code, must not be empty.
            prb_instance_id (str): The problem instance ID, must not be empty and must be 60 characters or less.
            date_of_diagnosis (str): The date of diagnosis in 'YYYYMMDD[HH[MM[SS]]]' format.
                Optional, but if provided, must be one of jhsd_0004 keys.
            expected_time_solved (str): The expected time to be solved in 'YYYYMMDD[HH[MM[SS]]]' format.
                Optional, but if provided, must be in the correct format.
            time_solved (str): The actual time solved in 'YYYYMMDD[HH[MM[SS]]]' format.
                Optional, but if provided, must be in the correct format.
            icd10_code (str): The ICD-10 code for the diagnosis, must not be empty.
            icd10_name (str): The ICD-10 name for the diagnosis, must not be empty.
            diagnosis_type (str): The type of diagnosis, must be one of jhsd_0004 keys.
            provisional (str): Indicates if the diagnosis is provisional, must be '1' or empty string.
            time_of_onset (str): The time of onset in 'YYYYMMDD[HH[MM[SS]]]' format.
                Optional, but if provided, must be in the correct format.

            NOTE: Arguments below are ORC fields. These arguments are expected to be shared with other orders in the same file.
            transaction_time (str): The time of the transaction in 'YYYYMMDDHHMMSS' format.
                Optional, can be left empty.
            order_effective_time (str): The effective time of the order in 'YYYYMMDD[HH[MM[SS]]]' format.
                Optional, can be left empty.
            order_control (str): The order control code, must be in h7t_0119.
                Usually 'NW' for new order/modification or 'CA' for cancel order.
            requester_order_number (str): The order request number, must be a number shorter than 16 characters long.
                NOTE: This is ORC-2, used for file naming. This value is usually shared with other problems saved in the same file.
            filler_order_number (str): The filler order number, must be a number shorter than 16 characters long.
                Optional, can be left empty.
            order_type (Literal["I", "O"]): The type of order, must be 'I' for inpatient or 'O' for outpatient.
            enterer (Physician): The physician who entered the order.
            requester (Physician): The physician who requested the order.
        """
        # Validate and clean args
        assert action_code in [
            "AD",
            "CD",
            "DE",
            "LI",
            "UC",
            "UN",
            "UP",
        ], f"Invalid action_code: {action_code}. Must be one of ['AD', 'CD', 'DE', 'LI', 'UC', 'UN', 'UP']."
        assert (
            len(dx_code) + len(dx_name) + len(dx_code_system) < 230
        ), "dx_code, dx_name, and dx_code_system combined must be less than 230 characters."
        assert (
            dx_code != "" and dx_code_system != ""
        ), "dx_code and dx_code_system must not be empty."
        if icd10_code != "":
            # Loose validation for ICD-10 code
            assert len(icd10_code) <= 10, f"icd10 code is too long: {icd10_code}."
        assert (
            len(icd10_code) + len(icd10_name) + len(diagnosis_type) < 220
        ), "icd10_code, icd10_name, and diagnosis_type combined should be less than 220 characters."
        assert prb_instance_id != "", "prb_instance_id must not be empty."
        assert (
            len(prb_instance_id) <= 60
        ), f"prb_instance_id must be 60 characters or less, got {len(prb_instance_id)} characters."
        if diagnosis_type != "":
            assert (
                diagnosis_type in jhsd_0004
            ), f"Invalid diagnosis_type: {diagnosis_type}. Must be one of {list(jhsd_0004.keys())}."
        if provisional != "":
            assert (
                provisional == "1"
            ), f"provisional must be '1' or empty string, got '{provisional}'."
        assert order_type in [
            "O",
            "I",
        ], f"order_type must be 'O' for outpatient or 'I' for inpatient, got '{order_type}'."
        assert (
            order_control in h7t_0119
        ), "Invalid order_control. It is usually NW or CA. See h7t_0119."
        assert (requester_order_number.isdigit()) and len(
            requester_order_number
        ) <= 15, f"requester_order_number must be a number shorter than 16 characters long, got '{requester_order_number}'."
        if filler_order_number != "":
            # NOTE: This part in PPR^ZD1 is ambiguous in the guideline. Assume it is 15-digit number.
            assert (filler_order_number.isdigit()) and len(
                filler_order_number
            ) <= 16, f"filler_order_number must be a number shorter than 16 characters long, got '{filler_order_number}'."
        # NOTE: ORC-4 is currently not implemented in PPR^ZD1, because it is unclear in the guideline.

        # Format numbers
        requester_order_number = requester_order_number.zfill(15)
        if filler_order_number != "":
            filler_order_number = filler_order_number.zfill(15)

        # Timestamps
        # Format time strings
        transaction_time = format_timestamp(
            transaction_time, format="YYYYMMDDHHMMSS", allow_null=True
        )  # Allow null (ORC-9)
        order_effective_time = format_timestamp(
            order_effective_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # Allow null (ORC-15)
        action_time = format_timestamp(
            action_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=False
        )  # R
        date_of_diagnosis = format_timestamp(
            date_of_diagnosis, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # O
        expected_time_solved = format_timestamp(
            expected_time_solved, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # O
        time_solved = format_timestamp(
            time_solved, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # O
        time_of_onset = format_timestamp(
            time_of_onset, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # O

        # Set attributes
        self.action_code = action_code
        self.action_time = action_time
        self.dx_code = dx_code
        self.dx_name = dx_name
        self.dx_code_system = dx_code_system
        self.prb_instance_id = prb_instance_id
        self.date_of_diagnosis = date_of_diagnosis
        self.expected_time_solved = expected_time_solved
        self.time_solved = time_solved
        self.time_of_onset = time_of_onset
        self.transaction_time = transaction_time
        self.order_effective_time = order_effective_time
        self.icd10_code = icd10_code
        self.icd10_name = icd10_name
        self.diagnosis_type = diagnosis_type
        self.provisional = provisional
        self.order_type = order_type
        self.order_control = order_control
        self.requester_order_number = requester_order_number
        self.filler_order_number = filler_order_number
        self.enterer = enterer
        self.requester = requester


def generate_random_problem(
    dx_code: str,
    dx_name: str,
    dx_code_system: str,
    prb_instance_id: str,  # May be same with ORC-2
    icd10_code: str,
    icd10_name: str,
    provisional: Literal["1", ""],
    is_admitted: bool,
    action_time: str,
    requester_order_number: str,
    filler_order_number: str,
    enterer: Physician,
    requester: Physician,
) -> Problem:
    """Generates a random Problem object with the provided attributes."""
    # Admission related fields
    if is_admitted:
        order_type = "I"
        diagnosis_type = random.choice(["H", "F"])  # 入院時 or 最終
    else:
        order_type = "O"
        diagnosis_type = random.choice(["O", "F"])  # 外来時 or 最終
    # Timestamps
    action_time_dt = to_datetime_anything(action_time)
    date_of_diagnosis_dt = action_time_dt - generate_random_timedelta(0, 1440)
    time_of_onset_dt = action_time_dt - generate_random_timedelta(0, 1440 * 30)
    expected_time_solved_dt = action_time_dt + generate_random_timedelta(0, 1440 * 30)

    return Problem(
        action_code="AD",  # Always AD
        action_time=action_time,
        dx_code=dx_code,
        dx_name=dx_name,
        dx_code_system=dx_code_system,
        prb_instance_id=prb_instance_id,
        date_of_diagnosis=date_of_diagnosis_dt.strftime(BASE_TIMESTAMP_FORMAT),
        expected_time_solved=expected_time_solved_dt.strftime(BASE_TIMESTAMP_FORMAT),
        time_solved="",  # Currently, not used
        icd10_code=icd10_code,
        icd10_name=icd10_name,
        diagnosis_type=diagnosis_type,
        provisional=provisional,
        time_of_onset=time_of_onset_dt.strftime(BASE_TIMESTAMP_FORMAT),
        transaction_time=action_time,  # Transaction time = action time
        order_effective_time=action_time,  # Order effective time = action time
        order_control="NW",  # Always NW
        requester_order_number=requester_order_number.zfill(15),
        filler_order_number=(
            filler_order_number.zfill(15) if filler_order_number else ""
        ),
        order_type=order_type,
        enterer=enterer,
        requester=requester,
    )
