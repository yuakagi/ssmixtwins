"""
Objects for drug orders.
"""

import random
from typing import Literal
from datetime import timedelta
from .physician import Physician
from ..tables import h7t_0119, merit_9_3, merit_9_4, udt_0162, jhsi_0002, udt_0164
from ..utils import format_timestamp, generate_random_timedelta, to_datetime_anything
from ..random_data import (
    NAME_TO_PRESCRIPTION_UNIT,
    NAME_TO_DOSE_FORM,
    NAME_TO_PRESCRIPTION_ROUTE,
)
from ..config import BASE_TIMESTAMP_FORMAT


class PrescriptionOrder:
    """
    This class represents a prescription order.
    """

    def __init__(
        self,
        drug_code: str,
        drug_name: str,
        drug_code_system: str,
        dose_unit_code: str,  # R, use 'MERIT-9 処方オーダ 表 4 単位略号'
        dosage_form_code: str,  # R, use 'MERIT-9 処方オーダ 表 3 剤形略号'
        minimum_dose: str,  # R, NM
        dispense_amount: str,  # R
        dispense_unit_code: str,  # R, use 'MERIT-9 処方オーダ 表 4 単位略号'
        prescription_number: str,
        repeat_pattern_code: str,
        repeat_pattern_name: str,
        repeat_pattern_code_system: str,
        duration_in_days: str,  # For prescription, this is 'number of days'
        start_time: str,  # TQ1-7, YYYYMMDD[HH[MM]]
        end_time: str,  # TQ1-8, YYYYMMDD[HH[MM]]
        total_occurrences: str,
        route_code: str,
        # ORC fields below
        # Because ORC implementation varies by the message type, some ORC fields are included here.
        recipe_number: str,  # Expected to be 2-digit
        order_admin_number: str,  # Expected to be 3-digit.
        transaction_time: str,
        order_effective_time: str,
        order_control: str,  # h7t_0119
        requester_order_number: str,
        filler_order_number: str,
        order_type: Literal["I", "O"],
        enterer: Physician,
        requester: Physician,
    ):
        """
        Initializes a PrescriptionOrder object with the provided parameters.

        Args:
            drug_code (str): The code for the drug.
            drug_name (str): The name of the drug.
            drug_code_system (str): The code system for the drug.
            dose_unit_code (str): The unit code for the dose, must be one of 'MERIT-9 処方オーダ 表 4 単位略号'.
            dosage_form_code (str): The dosage form code, must be one of 'MERIT-9 処方オーダ 表 3 剤形略号'.
            minimum_dose (str): The minimum dose of the drug, must be a digit and less than 20 characters long.
            dispense_amount (str): The amount to be dispensed, must be a digit and less than 20 characters long.
            dispense_unit_code (str): The unit code for the dispense amount, must be one of 'MERIT-9 処方オーダ 表 4 単位略号'.
            prescription_number (str): The prescription number, must be less than 20 characters long.
            repeat_pattern_code (str): The code for the repeat pattern, must be less than 520 characters long when combined with repeat_pattern_name and repeat_pattern_code_system.
            repeat_pattern_name (str): The name for the repeat pattern, must be less than 520 characters long when combined with repeat_pattern_code and repeat_pattern_code_system.
            repeat_pattern_code_system (str): The code system for the repeat pattern, must be less than 520 characters long when combined with repeat_pattern_code and repeat_pattern_name.
            duration_in_days (str): The duration in days for the prescription, must be a digit and less than 18 characters long.
            start_time (str): The start time for the prescription in 'YYYYMMDD[HH[MM]]' format, can be empty.
            end_time (str): The end time for the prescription in 'YYYYMMDD[HH[MM]]' format, can be empty.
            total_occurrences (str): The total occurrences for the prescription, must be a digit and less than 10 characters long.
            route_code (str): The route code for administration, must be one of 'udt_0162'.
            recipe_number (str): The recipe number, expected to be a 2-digit number.
                NOTE: This is unique to medication orders.
            order_admin_number (str): The order administration number, expected to be a 3-digit number.
                NOTE: This is unique to medication orders.

            NOTE: Arguments below are ORC fields. These arguments are expected to be shared with other orders in the same file.
            transaction_time (str): The transaction time in 'YYYYMMDDHHMMSS' format, can be empty.
            order_effective_time (str): The effective time of the order in 'YYYYMMDD[HH[MM[SS]]]' format, can be empty.
            order_control (str): The order control code, must be one of 'h7t_0119'.
            requester_order_number (str): The order number requested by the requester, must be a digit and less than 16 characters long.
                NOTE: This is ORC-2, used for file naming. This value is usually shared with other orders saved in the same file.
            filler_order_number (str): The order number filled by the filler, can be empty but must be a digit and less than 16 characters long if provided.
            order_type (Literal["I", "O"]): The type of order, must be either 'I' for inpatient or 'O' for outpatient.
            enterer (Physician): The physician who entered the order, must be a Physician object.
            requester (Physician): The physician who requested the order, must be a Physician object.
        """
        # Validate and clean args
        assert drug_code != "", "drug_code must not be empty."
        assert drug_code_system != "", "drug_code_system must not be empty."
        assert (
            len(drug_code) + len(drug_name) + len(drug_code_system) < 230
        ), f"drug_code, drug_name, and drug_code_system combined must be less than 230 characters, got {len(drug_code)+len(drug_name)+len(drug_code_system)}."
        assert minimum_dose != "", "minimum_dose must not be empty."
        assert (
            minimum_dose.isdigit() and len(minimum_dose) <= 20
        ), f"minimum_dose must be a digit and less than 20 characters, got '{minimum_dose}'."
        assert (
            dose_unit_code in merit_9_4
        ), f"dose_unit_code must be one of {list(merit_9_4.keys())}, got '{dose_unit_code}'."
        assert dosage_form_code == "" or (
            dosage_form_code in merit_9_3
        ), f"dosage_form_code must be one of {list(merit_9_3.keys())}, got '{dosage_form_code}'."
        # NOTE: dispense_amount, dispense_unit_code are REQUIRED in prescription, but not in injection.
        assert dispense_amount != "", "dispense_amount must not be empty."
        assert (
            dispense_amount.isdigit() and len(dispense_amount) <= 20
        ), f"dispense_amount must be a digit and less than 20 characters, got '{dispense_amount}'."
        assert (
            dispense_unit_code in merit_9_4
        ), f"dispense_unit_code must be one of {list(merit_9_4.keys())}, got '{dispense_unit_code}'."
        # NOTE; Prescription number is actually REQUIRED, even if the table says 'O' (optional). Tricky.
        assert prescription_number != "", "prescription_number must not be empty."
        assert (
            len(prescription_number) <= 20
        ), f"prescription_number must be less than 20 characters, got {len(prescription_number)}."
        assert (
            len(repeat_pattern_code)
            + len(repeat_pattern_name)
            + len(repeat_pattern_code_system)
            < 520
        ), f"repeat_pattern_code, repeat_pattern_name, and repeat_pattern_code_system combined must be less than 520 characters, got {len(repeat_pattern_code)+len(repeat_pattern_name)+len(repeat_pattern_code_system)}."
        if duration_in_days != "":
            assert (
                duration_in_days.isdigit() and len(duration_in_days) <= 18
            ), f"duration_in_days must be a digit and less than 18 characters, got '{duration_in_days}'."
        if total_occurrences != "":
            assert (
                total_occurrences.isdigit() and len(total_occurrences) <= 10
            ), f"total_occurrences must be a digit and less than 10 characters, got '{total_occurrences}'."
        assert (
            route_code in udt_0162
        ), f"route_code must be one of {list(udt_0162.keys())}, got '{route_code}'."
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

        assert (
            recipe_number.isdigit() and len(recipe_number) == 2
        ), f"recipe_number must be a 2-digit number, got '{recipe_number}'."
        assert (
            order_admin_number.isdigit() and len(order_admin_number) == 3
        ), f"order_admin_number must be a 3-digit number, got '{order_admin_number}'."
        assert isinstance(enterer, Physician), "enterer must be a Physician object."
        assert isinstance(requester, Physician), "requester must be a Physician object."

        # Format numbers
        requester_order_number = requester_order_number.zfill(15)
        if filler_order_number != "":
            filler_order_number = filler_order_number.zfill(15)
        # Requester_group_number logics
        # NOTE: This logic is defined for injection orders. This is not excplicitly defined for prescription orders.
        #       However, the logic for prescription orders is unclear in the guideline. Therefore, we use the same logic as injection orders.
        requester_group_number = "_".join(
            [requester_order_number, recipe_number, order_admin_number]
        )

        # Timestamps
        transaction_time = format_timestamp(
            transaction_time, format="YYYYMMDDHHMMSS", allow_null=True
        )  # Allow null (ORC-9)
        order_effective_time = format_timestamp(
            order_effective_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # Allow null (ORC-15)
        start_time = format_timestamp(
            start_time, format="YYYYMMDD[HH[MM]]", allow_null=True
        )  # Allow null (TQ1-7)
        end_time = format_timestamp(
            end_time, format="YYYYMMDD[HH[MM]]", allow_null=True
        )  # Allow null (TQ1-8)

        # Action time is required in prescription orders.
        # Set attributes
        self.drug_code = drug_code
        self.drug_name = drug_name
        self.drug_code_system = drug_code_system
        self.dose_unit_code = dose_unit_code
        self.dosage_form_code = dosage_form_code
        self.minimum_dose = minimum_dose
        self.dispense_amount = dispense_amount
        self.dispense_unit_code = dispense_unit_code
        self.prescription_number = prescription_number
        self.repeat_pattern_code = repeat_pattern_code
        self.repeat_pattern_name = repeat_pattern_name
        self.repeat_pattern_code_system = repeat_pattern_code_system
        self.duration_in_days = duration_in_days
        self.start_time = start_time
        self.end_time = end_time
        self.total_occurrences = total_occurrences
        self.route_code = route_code
        # ORC fields below
        self.order_type = order_type
        self.order_control = order_control
        self.requester_order_number = requester_order_number
        self.filler_order_number = filler_order_number
        self.requester_group_number = requester_group_number
        self.transaction_time = transaction_time
        self.order_effective_time = order_effective_time
        self.enterer = enterer
        self.requester = requester


class InjectionComponent:
    """
    This class represents a component of an injection order.
    """

    def __init__(
        self,
        component_type: Literal["A", "B"],
        component_code: str,
        component_name: str,
        component_code_system: str,
        component_quantity: str,
        component_unit_code: str,
        component_unit_name: str,
        component_unit_code_system: str,
    ):
        """
        Initializes an InjectionComponent object with the provided parameters.

        Args:
            component_type (Literal["A", "B"]): The type of the component, must be either 'A' or 'B'.
            component_code (str): The code for the component, must not be empty.
            component_name (str): The name of the component.
            component_code_system (str): The code system for the component, must not be empty.
            component_quantity (str): The quantity of the component, must be a digit and less than 20 characters long.
            component_unit_code (str): The unit code for the component, must not be empty.
            component_unit_name (str): The name of the unit for the component, must not be empty.
            component_unit_code_system (str): The code system for the unit, must not be empty.
        """
        # Validate
        assert component_type in [
            "A",
            "B",
        ], "component_type must be either A or B"
        assert component_code != "", "component_code must not be empty."
        assert (
            component_unit_code_system != ""
        ), "component_unit_code_system must not be empty."
        assert (
            len(component_code) + len(component_name) + len(component_code_system) < 240
        ), "The combination of component_code, component_name, component_code_system is too long."
        assert (
            component_quantity.isdigit() and len(component_quantity) < 20
        ), "component_quantity must be a number, less than 20-character long."
        # NOTE: Component unit validation is minimum here, because the guideline is ambiguous.
        assert component_unit_code != ""
        assert component_unit_name != ""
        assert component_unit_code_system != ""
        # Set attributes
        self.component_type = component_type
        self.component_code = component_code
        self.component_name = component_name
        self.component_code_system = component_code_system
        self.component_quantity = component_quantity
        self.component_unit_code = component_unit_code
        self.component_unit_name = component_unit_name
        self.component_unit_code_system = component_unit_code_system


class InjectionOrder:
    """
    This class represents a injection order.
    """

    def __init__(
        self,
        injection_type_code: str,  # R, use jhsi_0002
        dose_unit_code: str,  # R, unit for minimum dose, use merit_9_4 or ISO+
        dose_unit_name: str,
        dose_unit_code_system: str,
        minimum_dose: str,  # Water volume given per dose (e.g., 120, for 120 mL)
        dispense_amount: str,
        dispense_unit_code: str,  # R, use merit_9_4 or ISO+
        dispense_unit_name: str,
        dispense_unit_code_system: str,
        prescription_number: str,
        repeat_pattern_code: str,
        repeat_pattern_name: str,
        repeat_pattern_code_system: str,
        start_time: str,  # TQ1-7, YYYYMMDD[HH[MM]]
        end_time: str,  # TQ1-8, YYYYMMDD[HH[MM]]
        total_occurrences: str,
        route_code: str,  # R, use udt_0162
        route_device_code: str,  # R, use udt_0164
        components: list[InjectionComponent],
        # ORC fields below
        # Because ORC implementation varies by the message type, some ORC fields are included here.
        recipe_number: str,  # Expected to be 2-digit
        order_admin_number: str,  # Expected to be 3-digit.
        transaction_time: str,
        order_effective_time: str,
        order_control: str,  # h7t_0119
        requester_order_number: str,
        filler_order_number: str,
        order_type: Literal["I", "O"],
        enterer: Physician,
        requester: Physician,
    ):
        """
        Initializes a InjectionOrder object with the provided parameters.

        Args:

            injection_type_code (str): The code for the injection type, must be one of 'jhsi_0002'.
            dose_unit_code (str): The unit code for the dose, must be one of 'merit_9_4' or ISO+.
            dose_unit_name (str): The name of the dose unit, must not be empty.
            dose_unit_code_system (str): The code system for the dose unit, must not be empty.
            minimum_dose (str): The minimum dose of the injection, must be a digit and less than 20 characters long.
            dispense_amount (str): The amount to be dispensed, can be empty but if provided, must be a digit and less than 20 characters long.
            dispense_unit_code (str): The unit code for the dispense amount, must be one of 'merit_9_4' or ISO+.
            dispense_unit_name (str): The name of the dispense unit, must not be empty if dispense_unit_code is not in 'merit_9_4'.
            dispense_unit_code_system (str): The code system for the dispense unit, must not be empty if dispense_unit_code is not in 'merit_9_4'.
            prescription_number (str): The prescription number, must not be empty and must be less than 20 characters long.
            repeat_pattern_code (str):
                The code for the repeat pattern, must be less than 520 characters long when combined with
                repeat_pattern_name and repeat_pattern_code_system.
            repeat_pattern_name (str):
                The name for the repeat pattern, must be less than 520 characters long when combined with
                repeat_pattern_code and repeat_pattern_code_system.
            repeat_pattern_code_system (str):
                The code system for the repeat pattern, must be less than 520 characters long when combined with
                repeat_pattern_code and repeat_pattern_name.
            start_time (str): The start time for the injection in 'YYYYMMDD[HH[MM]]' format, can be empty.
            end_time (str): The end time for the injection in 'YYYYMMDD[HH[MM]]' format, can be empty.
            total_occurrences (str): The total occurrences for the injection, must be a digit and less than 10 characters long.
            route_code (str): The route code for administration, must be one of 'udt_0162'.
            route_device_code (str): The route device code for administration, must be one of 'udt_0164' if provided.
            components (list[InjectionComponent]):
                A list of InjectionComponent objects representing the components of the injection.
            recipe_number (str): The recipe number, expected to be a 2-digit number.
                NOTE: This is unique to medication orders.
            order_admin_number (str): The order administration number, expected to be a 3-digit number.
                NOTE: This is unique to medication orders.

            NOTE: Arguments below are ORC fields. These arguments are expected to be shared with other orders in the same file.
            transaction_time (str): The transaction time in 'YYYYMMDDHHMMSS' format, can be empty.
            order_effective_time (str): The effective time of the order in 'YYYYMMDD[HH[MM[SS]]]' format, can be empty.
            order_control (str): The order control code, must be one of 'h7t_0119'.
            requester_order_number (str): The order number requested by the requester, must be a digit and less than 16 characters long.
                NOTE: This is ORC-2, used for file naming. This value is usually shared with other orders saved in the same file.
            filler_order_number (str): The order number filled by the filler, can be empty but  must be a digit and less than 16 characters long if provided.
            order_type (Literal["I", "O"]): The type of order, must be either 'I' for inpatient or 'O' for outpatient.
            enterer (Physician):
                The physician who entered the order, must be a Physician object.
            requester (Physician):
                The physician who requested the order, must be a Physician object.

        """
        # Validate and clean args
        assert (
            injection_type_code in jhsi_0002
        ), f"injection_type_code must be one of {list(jhsi_0002.keys())}, got '{injection_type_code}'."
        assert minimum_dose != "", "minimum_dose must not be empty."
        assert (
            minimum_dose.isdigit() and len(minimum_dose) <= 20
        ), f"minimum_dose must be a digit and less than 20 characters, got '{minimum_dose}'."
        # NOTE: For prescription orders, dose_unit_code is ensured to be in merit_9_4, but, because injection order may use ISO+,
        #       , we allow using codes not in merit_9_4.
        # NOTE: Implement ISO+ here if needed. Currently, we do not implement ISO+ because its list is too extensive.
        assert dose_unit_code != "", "dose_unit_name must not be empty."
        if dose_unit_code not in merit_9_4:
            assert dose_unit_name != "", "dose_unit_name must not be empty."
            assert (
                dose_unit_code_system != ""
            ), "dose_unit_code_system must not be empty."
        # NOTE: dispense_amount is not required for injection orders, but required for prescription orders
        if dispense_amount != "":
            assert (
                dispense_amount.isdigit() and len(dispense_amount) <= 20
            ), f"dispense_amount must be a digit and less than 20 characters, got '{dispense_amount}'."
            if dispense_unit_code != "":
                if dispense_unit_code not in merit_9_4:
                    # Dispense doese unit must be given if dispense_unit_code is not in merit_9_4.
                    assert (
                        dispense_unit_name != ""
                    ), "dispense_unit_name must not be empty."
                    assert (
                        dispense_unit_code_system != ""
                    ), "dispense_unit_code_system must not be empty."
        else:
            assert (
                dispense_unit_code == ""
            ), "dispense_amount must not be provided if dispense_unit_code is not provided."
            assert (
                dispense_unit_name == ""
            ), "dispense_unit_name must not be provided if dispense_amount is not provided."
            assert (
                dispense_unit_code_system == ""
            ), "dispense_unit_code_system must not be provided if dispense_amount is not provided."
        # Prescriotion number is REQUIRED.
        assert prescription_number != "", "prescription_number must not be empty."
        assert (
            len(prescription_number) <= 20
        ), f"prescription_number must be less than 20 characters, got {len(prescription_number)}."
        assert (
            len(repeat_pattern_code)
            + len(repeat_pattern_name)
            + len(repeat_pattern_code_system)
            < 520
        ), f"repeat_pattern_code, repeat_pattern_name, and repeat_pattern_code_system combined must be less than 520 characters, got {len(repeat_pattern_code)+len(repeat_pattern_name)+len(repeat_pattern_code_system)}."
        if total_occurrences != "":
            assert (
                total_occurrences.isdigit() and len(total_occurrences) <= 10
            ), f"total_occurrences must be a digit and less than 10 characters, got '{total_occurrences}'."
        assert (
            route_code in udt_0162
        ), f"route_code must be one of {list(udt_0162.keys())}, got '{route_code}'."
        if route_device_code != "":
            assert (
                route_device_code in udt_0164
            ), f"route_device_code must be one of {list(udt_0164.keys())}, got '{route_device_code}'."
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
        assert (
            recipe_number.isdigit() and len(recipe_number) == 2
        ), f"recipe_number must be a 2-digit number, got '{recipe_number}'."
        assert (
            order_admin_number.isdigit() and len(order_admin_number) == 3
        ), f"order_admin_number must be a 3-digit number, got '{order_admin_number}'."
        assert isinstance(enterer, Physician), "enterer must be a Physician object."
        assert isinstance(requester, Physician), "requester must be a Physician object."
        assert isinstance(
            components, list
        ), "components must be a list of InjectionComponent objects."
        for component in components:
            assert isinstance(
                component, InjectionComponent
            ), "Each component must be an instance of InjectionComponent."

        # Clean args
        injection_type_name = jhsi_0002[injection_type_code]
        injection_type_code_system = "99I02"
        if dose_unit_code in merit_9_4:
            dose_unit_name = merit_9_4[dose_unit_code]
            dose_unit_code_system = "MR9P"
        if dispense_unit_code in merit_9_4:
            dispense_unit_name = merit_9_4[dispense_unit_code]
            dispense_unit_code_system = "MR9P"
        requester_order_number = requester_order_number.zfill(15)
        if filler_order_number != "":
            filler_order_number = filler_order_number.zfill(15)
        # Requester_group_number logics
        # NOTE: This logic is defined for injection orders. This is not excplicitly defined for prescription orders.
        #       However, the logic for prescription orders is unclear in the guideline. Therefore, we use the same logic as injection orders.
        requester_group_number = "_".join(
            [requester_order_number, recipe_number, order_admin_number]
        )
        # Timestamps
        transaction_time = format_timestamp(
            transaction_time, format="YYYYMMDDHHMMSS", allow_null=True
        )  # Allow null (ORC-9)
        order_effective_time = format_timestamp(
            order_effective_time, format="YYYYMMDD[HH[MM[SS]]]", allow_null=True
        )  # Allow null (ORC-15)
        start_time = format_timestamp(
            start_time, format="YYYYMMDD[HH[MM]]", allow_null=True
        )  # Allow null (TQ1-7)
        end_time = format_timestamp(
            end_time, format="YYYYMMDD[HH[MM]]", allow_null=True
        )  # Allow null (TQ1-8)

        # Action time is required in prescription orders.
        # Set attributes
        self.injection_type_code = injection_type_code
        self.injection_type_name = injection_type_name
        self.injection_type_code_system = injection_type_code_system
        self.dose_unit_code = dose_unit_code
        self.dose_unit_name = dose_unit_name
        self.dose_unit_code_system = dose_unit_code_system
        self.minimum_dose = minimum_dose
        self.dispense_amount = dispense_amount
        self.dispense_unit_code = dispense_unit_code
        self.dispense_unit_name = dispense_unit_name
        self.dispense_unit_code_system = dispense_unit_code_system
        self.prescription_number = prescription_number
        self.repeat_pattern_code = repeat_pattern_code
        self.repeat_pattern_name = repeat_pattern_name
        self.repeat_pattern_code_system = repeat_pattern_code_system
        self.start_time = start_time
        self.end_time = end_time
        self.total_occurrences = total_occurrences
        self.route_code = route_code
        self.route_device_code = route_device_code
        self.components = components  # List of InjectionComponent objects
        # ORC fields below
        self.order_type = order_type
        self.order_control = order_control
        self.requester_order_number = requester_order_number
        self.filler_order_number = filler_order_number
        self.requester_group_number = requester_group_number
        self.transaction_time = transaction_time
        self.order_effective_time = order_effective_time
        self.enterer = enterer
        self.requester = requester


def generate_random_prescription_order(
    drug_code: str,
    drug_name: str,
    drug_code_system: str,
    prescription_number: str,
    start_time: str,
    transaction_time: str,
    recipe_number: str,
    order_admin_number: str,
    requester_order_number: str,
    filler_order_number: str,
    is_admitted: bool,
    enterer: Physician,
    requester: Physician,
) -> PrescriptionOrder:
    """
    Generates a random prescription order for testing purposes.
    """
    # Timestamps
    order_effective_time = transaction_time  # Use transaction time as effective time

    # Unit
    dose_unit_code = "DOSE"  # Set default first (~回分)
    for k, v in NAME_TO_PRESCRIPTION_UNIT.items():
        for value in v:
            if value in drug_name:
                dose_unit_code = k
                break
        if dose_unit_code != "DOSE":
            break
    dose_unit_name = merit_9_4[dose_unit_code]
    dose_unit_code_system = "MR9P"
    # Dose form
    dosage_form_code = ""  # Set default (null)
    for k, v in NAME_TO_DOSE_FORM.items():
        for value in v:
            if value in drug_name:
                dosage_form_code = k
                break
        if dosage_form_code != "":
            break
    # Dispense
    # NOTE: For simplicity, we use dose_unit_code
    dispense_unit_code = dose_unit_code
    dispense_amount = str(random.randint(1, 20))  # Random 1 ~ 20
    # Minimum dose
    minimum_dose = "1"
    # Repeat pattern
    # NOTE: Chose from some patterns randomly, may be inconsistent with the dose units
    if random.random() <= 0.5:
        repeat_pattern_code = "1013044400000000"
        repeat_pattern_name = "内服・経口・１日３回朝昼夕食後"
        repeat_pattern_code_system = "JAMISDP01"
    else:
        repeat_pattern_code = "1012040400000000"
        repeat_pattern_name = "内服・経口・１日２回朝夕食後"
        repeat_pattern_code_system = "JAMISDP01"
    # Duration in days:
    # NOTE: Dispense amount and duration x repeat pattern display inconsistensy.
    if is_admitted:
        duration_in_days = random.choice(["7", "30", "60", "90"])
    else:
        duration_in_days = str(random.randint(1, 7))
    # Total occurence
    if dose_unit_code == "DOSE":
        total_occurrences = dispense_amount
    else:
        total_occurrences = ""
    # Route
    route_code = "OTH"  # Set default, 'others'
    for k, v in NAME_TO_PRESCRIPTION_ROUTE.items():
        for value in v:
            if value in drug_name:
                route_code = k
                break
        if route_code != "OTH":
            break

    order = PrescriptionOrder(
        drug_code=drug_code,
        drug_name=drug_name,
        drug_code_system=drug_code_system,
        dose_unit_code=dose_unit_code,
        dosage_form_code=dosage_form_code,
        minimum_dose=minimum_dose,
        dispense_amount=dispense_amount,
        dispense_unit_code=dispense_unit_code,
        prescription_number=prescription_number,
        repeat_pattern_code=repeat_pattern_code,
        repeat_pattern_name=repeat_pattern_name,
        repeat_pattern_code_system=repeat_pattern_code_system,
        duration_in_days=duration_in_days,
        start_time=start_time,
        end_time="",  # Empty
        total_occurrences=total_occurrences,
        route_code=route_code,
        recipe_number=recipe_number,
        order_admin_number=order_admin_number,
        transaction_time=transaction_time,
        order_effective_time=order_effective_time,
        order_control="NW",
        requester_order_number=requester_order_number,
        filler_order_number=filler_order_number,
        order_type="I" if is_admitted else "O",
        enterer=enterer,
        requester=requester,
    )

    return order


def generate_random_injection_component(
    component_code: str,
    component_name: str,
    component_code_system: str,
) -> InjectionComponent:
    """
    Generates a random injection component for testing purposes.
    """
    # Component type
    base_kws = [
        "生食",
        "生理食塩",
        "ブドウ糖液",
        "ブドウ糖注射液",
        "ブドウ糖注",
        "注射用水",
        "蒸留水",
        "ソリタ",
        "ラクトリンゲル",
        "ソリューゲン",
        "ビカネイト",
        "リプラス",
        "NK",
        "EL",
        "マルトス",
        "キリット",
        "糖液",
        "糖注",
        "リンゲル",
        "ハルトマン",
        "ニソリ",
        "ヴィーン",
        "アクメイン",
        "ペロール",
        "ビカーボン",
        "ボルベン",
        "デキストラン",
        "デノサリン",
        "ソルデム",
        "ラクテック",
        "ソルアセト",
        "ソルラクト",
        "フィジオ",
        "ビーフリード",
        "エルネオパ",
        "ハイカリック",
    ]
    for kw in base_kws:
        if kw in component_name:
            component_type = "B"  # base
            break
    else:
        component_type = "A"  # additive

    # quantity
    if component_type == "A":
        # Additive
        component_quantity = random.choice(["10", "120", "240", "360"])
        component_unit_code = "mg"
        component_unit_name = "mg"
        component_unit_code_system = "ISO+"
    else:
        # Base
        component_quantity = random.choice(["100", "500", "1000", "1500", "2000"])
        component_unit_code = "ml"
        component_unit_name = "ml"
        component_unit_code_system = "ISO+"

    # Create InjectionComponent object
    return InjectionComponent(
        component_type=component_type,
        component_code=component_code,
        component_name=component_name,
        component_code_system=component_code_system,
        component_quantity=component_quantity,
        component_unit_code=component_unit_code,
        component_unit_name=component_unit_name,
        component_unit_code_system=component_unit_code_system,
    )


def generate_random_injection_order(
    prescription_number: str,
    start_time: str,
    transaction_time: str,
    components: list[InjectionComponent],
    recipe_number: str,  # Expected to be 2-digit
    order_admin_number: str,  # Expected to be 3-digit.
    requester_order_number: str,
    filler_order_number: str,
    is_admitted: bool,
    enterer: Physician,
    requester: Physician,
) -> InjectionOrder:
    """
    Generates a random prescription order for testing purposes.
    """
    # Timestamps
    start_time_dt = to_datetime_anything(start_time)
    end_time = (start_time_dt + timedelta(days=1)).strftime(BASE_TIMESTAMP_FORMAT)
    order_effective_time = transaction_time  # Use transaction time as effective time

    # Dose (For OML-02, this is total water volume)
    minimum_dose = "120"
    dose_unit_code = "ml"
    dose_unit_name = "ml"
    dose_unit_code_system = "ISO+"
    # Dispense
    # NOTE: Random
    if random.random() < 0.8:
        dispense_amount = ""
        dispense_unit_code = ""
        dispense_unit_name = ""
        dispense_unit_code_system = ""
    else:
        dispense_amount = random.choice(["120", "240", "360"])
        dispense_unit_code = "ml"
        dispense_unit_name = "ml"
        dispense_unit_code_system = "ISO+"

    order = InjectionOrder(
        injection_type_code="01",  # We only use '01' (一般) for now
        dose_unit_code=dose_unit_code,
        dose_unit_name=dose_unit_name,
        dose_unit_code_system=dose_unit_code_system,
        minimum_dose=minimum_dose,
        dispense_amount=dispense_amount,
        dispense_unit_code=dispense_unit_code,
        dispense_unit_name=dispense_unit_name,
        dispense_unit_code_system=dispense_unit_code_system,
        prescription_number=prescription_number,
        repeat_pattern_code="",
        repeat_pattern_name="",
        repeat_pattern_code_system="",
        start_time=start_time,
        end_time=end_time,
        total_occurrences="",
        route_code="IV",  # Fixed to IV (静脈内)
        route_device_code="IVP",  # Fixed to IVP (点滴ポンプ)
        components=components,
        # ORC fields below
        recipe_number=recipe_number,
        order_admin_number=order_admin_number,
        transaction_time=transaction_time,
        order_effective_time=order_effective_time,
        order_control="NW",
        requester_order_number=requester_order_number,
        filler_order_number=filler_order_number,
        order_type="I" if is_admitted else "O",
        enterer=enterer,
        requester=requester,
    )

    return order
