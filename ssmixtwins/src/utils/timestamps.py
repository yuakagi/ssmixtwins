import datetime
import numpy as np
from ..config import BASE_TIMESTAMP_FORMAT

DEFAULT_TIMESTAMP_FORMAT = "YYYYMMDD[HH[MM[SS]]]"

TIMESTAMP_FORMATS = {
    # For message time (used for file naming, this uses a unique format)
    "YYYYMMDDHHMMSSFFF": "%Y%m%d%H%M%S%f",
    # Date only
    "YYYYMMDD": "%Y%m%d",
    # + Hour
    "YYYYMMDD[HH]": "%Y%m%d%H",
    "YYYYMMDDHH": "%Y%m%d%H",
    # + Minute
    "YYYYMMDD[HH[MM]]": "%Y%m%d%H%M",
    "YYYYMMDDHH[MM]": "%Y%m%d%H%M",
    "YYYYMMDDHHMM": "%Y%m%d%H%M",
    # + Second
    "YYYYMMDD[HH[MM[SS]]]": "%Y%m%d%H%M%S",
    "YYYYMMDDHH[MM[SS]]": "%Y%m%d%H%M%S",
    "YYYYMMDDHHMM[SS]": "%Y%m%d%H%M%S",
    "YYYYMMDDHHMMSS": "%Y%m%d%H%M%S",
    # + Fractional second (dot)
    "YYYYMMDD[HH[MM[SS[.S[S[S]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDD[HH[MM[SS[.S[S[S[S]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDD[HH[MM[SS[.S[S[S[S[S]]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDD[HH[MM[SS[.S[S[S[S[S[S]]]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S[S]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S[S[S]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S[S[S[S]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S[S[S[S[S]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHH[MM[SS[.S[S[S[S[S[S]]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S[S]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S[S[S]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S[S[S[S]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S[S[S[S[S]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMM[SS[.S[S[S[S[S[S]]]]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S[S]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S[S[S]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S[S[S[S]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S[S[S[S[S]]]]]": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS[.S[S[S[S[S[S]]]]]]": "%Y%m%d%H%M%S.%f",
    # + Fractional second
    "YYYYMMDDHHMMSS.S": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS.SS": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS.SSS": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS.SSSS": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS.SSSSS": "%Y%m%d%H%M%S.%f",
    "YYYYMMDDHHMMSS.SSSSSS": "%Y%m%d%H%M%S.%f",
}


def to_datetime_anything(timestamp: str) -> datetime.datetime:
    """Converts any timestamp string seen in SSMIX2 to adatetime object."""
    # Force any format to YYYYMMDDHHMMSSFFFFFF
    corrected_timestamp = (
        timestamp.replace("/", "")
        .replace(" ", "")
        .replace(":", "")
        .replace(".", "")
        .replace("-", "")
    )
    if len(timestamp) > 20:
        corrected_timestamp = timestamp[:20]
    else:
        corrected_timestamp = timestamp.ljust(20, "0")
    # To datetime object
    try:
        dt = datetime.datetime.strptime(corrected_timestamp, "%Y%m%d%H%M%S%f")
    except ValueError as e:
        # Handle if parsing still fails after correction
        print(f"Timestamp format is invalid: {timestamp}")
        raise ValueError(
            f"Timestamp '{timestamp}' does not match the expected format '{BASE_TIMESTAMP_FORMAT}'."
        ) from e
    return dt


def format_timestamp(
    timestamp: str, format: str = DEFAULT_TIMESTAMP_FORMAT, allow_null: bool = True
) -> str:
    """Formats a timestamp string into the specified format.
    Args:
        timestamp (str): The timestamp string to format.
            This function expects the timestamp to be in the format defined by BASE_TIMESTAMP_FORMAT.
        format (str): The format key to use for formatting. Defaults to DEFAULT_TIMESTAMP_FORMAT.
        allow_null (bool): If True, allows empty or None timestamp. Defaults to True.
            If False, raises ValueError for empty or None timestamp.
    Returns:
        str: The formatted timestamp string.
    Raises:
        ValueError: If the timestamp does not match the expected format.
    """
    if timestamp is None or timestamp == "":
        if allow_null:
            return ""
    else:
        # First, converet to datetime object
        try:
            dt = datetime.datetime.strptime(timestamp, BASE_TIMESTAMP_FORMAT)
        except ValueError:
            dt = to_datetime_anything(timestamp)
        # The, re-format the datetime object to the specified format
        dt_format = TIMESTAMP_FORMATS.get(format)
        if not dt_format:
            raise ValueError(f"Invalid timestamp format key: {format}")
        formatted = dt.strftime(dt_format)
        # Check the length
        if format == "YYYYMMDDHHMMSSFFF":
            formatted = formatted[:17]
        else:
            # NOTE: The longest allowed format in the guideline is "YYYYMMDDHHMMSS[.S[S[S[S]]]]".
            # But, the guideline does not expect this precision.
            # The 'message_time' should be reported to 17-digit format, which is the longest required format.
            # Therefore, we truncate datetime strings up to 17 digits.
            if len(formatted) >= 17:
                formatted = formatted[:17]

        return formatted


def validate_timestamp_format(
    timestamp: str, format: str = DEFAULT_TIMESTAMP_FORMAT, allow_null: bool = True
) -> str:
    """
    Validates if the given timestamp string matches the specified format.

    Args:
        timestamp (str): The timestamp string to validate.
        format (str): The format key to use for validation. Defaults to DEFAULT_TIMESTAMP_FORMAT.
        allow_null (bool): If True, allows empty or None timestamp. Defaults to True.
            If False, raises ValueError for empty or None timestamp.

    Returns:
        str: The validated timestamp string if it matches the format.

    Raises:
        ValueError: If the timestamp does not match the format.
    """
    # Handle None or empty timestamp
    if timestamp is None or timestamp == "":
        if allow_null:
            return ""
        else:
            raise ValueError(
                "Timestamp cannot be None or empty when allow_null is False."
            )

    # Others
    dt_format = TIMESTAMP_FORMATS.get(format)
    if not dt_format:
        raise ValueError(f"Invalid timestamp format key: {format}")

    try:
        dt = datetime.datetime.strptime(timestamp, dt_format)
        reconstructed = dt.strftime(dt_format)
        if timestamp != reconstructed:
            raise ValueError
        return timestamp

    except ValueError as e:
        raise ValueError(
            f"Timestamp '{timestamp}' does not match format '{format}'. "
            f"Expected format: {dt_format}"
        ) from e


def generate_random_timedelta(min_minutes: int, max_minutes: int):
    random_ms = np.random.randint(min_minutes * 60 * 1000, max_minutes * 60 * 1000)
    random_td = datetime.timedelta(milliseconds=random_ms)
    return random_td
