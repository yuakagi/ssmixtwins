""" """

# File namings:
# -1. Patinet ID
# -2. Date
# -3. Type of data
# -4. Order No (Same as ORC-2, 'requester_order_number')
# -5. Time of the message (Time the massage is generated, 'YYYYMMDDHHSSFFF' format)
# -6. Departiment code
# -7. Condition flag (0, 2 or 1, 1 for active.)


import os
from ..tables import udt_0069
from ..utils import format_timestamp


def generate_file_name(
    patient_id: str,
    date: str,
    data_type: str,
    requester_order_number: str,  # 15 digits
    message_time: str,
    department_code: str,
    condition_flag: str,
) -> str:
    """Generates a file name based on the provided parameters.

    Args:
        patient_id (str): The ID of the patient.
        date (str): The date in 'YYYYMMDD' format.
        data_type (str): The type of data (e.g., 'dmg', 'med', 'lab').
        requester_order_number (str): The requester order number, should be 15 digits.
        message_time (str): The time of the message in 'HHMMSSFFF' format.
        department_code (str): The department code.
        condition_flag (str): Condition flag, e.g., '0', '1', or '2'.

    Returns:
        str: The generated file name.
    """
    return f"{patient_id}_{date}_{data_type}_{requester_order_number}_{message_time}_{department_code}_{condition_flag}"


def generate_file_path(
    ssmix_root: str,
    patient_id: str,
    date: str,
    data_type: str,
    requester_order_number: str,  # 15 digits
    message_time: str,
    department_code: str,
    condition_flag: str,
) -> str:
    """Generates a file path based on the provided parameters.
    Args:
        ssmix_root (str): The root directory where the file will be stored.
        patient_id (str): The ID of the patient.
        date (str): The date in 'YYYYMMDD' format.
        data_type (str): The type of data (e.g., 'dmg', 'med', 'lab').
        requester_order_number (str): The requester order number, should be 15 digits.
        message_time (str): The time of the message in 'HHMMSSFFF' format.
        department_code (str): The department code.
        condition_flag (str): Condition flag, e.g., '0', '1', or '2'.
    Returns:
        str: The generated file path.
    """

    file_name = generate_file_name(
        patient_id=patient_id,
        date=date,
        data_type=data_type,
        requester_order_number=requester_order_number,
        message_time=message_time,
        department_code=department_code,
        condition_flag=condition_flag,
    )
    lv1 = patient_id[:3]
    lv2 = patient_id[3:6]
    lv3 = patient_id
    lv4 = date
    lv5 = data_type
    file_path = os.path.join(ssmix_root, lv1, lv2, lv3, lv4, lv5, file_name)
    return file_path


def save_message_to_file(
    message: str,
    ssmix_root: str,
    patient_id: str,
    date: str,
    data_type: str,
    requester_order_number: str,  # 15 digits
    message_time: str,
    department_code: str,
    condition_flag: str,
    encoding: str,
):
    """Saves a message to a file with a structured naming convention.
    Args:
        message (str): The message to be saved.
        ssmix_root (str): The root directory where the file will be stored.
        patient_id (str): The ID of the patient.
        date (str): The date in 'YYYYMMDD' format.
        data_type (str): The type of data (e.g., 'dmg', 'med', 'lab').
        requester_order_number (str): The requester order number, should be 15 digits.
        message_time (str): The time of the message in 'HHMMSSFFF' format.
        department_code (str): The department code.
        condition_flag (str): Condition flag, e.g., '0', '1', or '2'.
        encoding (str): The encoding to use when saving the file.
    """
    # Validate
    assert requester_order_number.isdigit(), "Requester order number must be numeric."
    if len(requester_order_number) != 15:
        requester_order_number = requester_order_number.zfill(15)
    assert len(patient_id) > 6, "Patient ID must be at least 6 characters long."
    assert (
        len(date) == 8
    ) or date == "-", "Date must be in 'YYYYMMDD' format or '-' for static data."
    assert condition_flag in ["0", "1", "2"], "Condition flag must be '0', '1', or '2'."
    if department_code != "-":
        assert (
            department_code in udt_0069
        ), f"Department code must be one of {list(udt_0069.keys())}, got '{department_code}'."
    # Formatting
    message_time = format_timestamp(message_time, format="YYYYMMDDHHMMSSFFF")

    # Save
    file_path = generate_file_path(
        ssmix_root=ssmix_root,
        patient_id=patient_id,
        date=date,
        data_type=data_type,
        requester_order_number=requester_order_number,
        message_time=message_time,
        department_code=department_code,
        condition_flag=condition_flag,
    )
    os.makedirs(
        os.path.dirname(file_path), exist_ok=True
    )  # Create directories if they don't exist
    with open(file_path, "w", encoding=encoding) as f:
        f.write(message)
