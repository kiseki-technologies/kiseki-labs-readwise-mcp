# Standard Library
import re
from datetime import date, timedelta
from typing import Tuple


def parse_duration(duration_str: str) -> Tuple[date, date]:
    """
    Parses a duration string (e.g., '1w', '1d', '2h', '30m') and returns a datetime range.

    The second datetime in the tuple is always the current datetime.
    The first datetime is calculated by subtracting the duration from the current datetime.

    Args:
        duration_str: The duration string. Valid units: 'h' (hour), 'm' (minute), 'w' (week), 'd' (day).

    Returns:
        A tuple containing (from_datetime, to_datetime).

    Raises:
        ValueError: If the duration string format is invalid or the unit is unknown.
    """
    to_date = date.today()

    # Use regex to parse the duration string (e.g., "12w", "3h", "45m")
    match = re.fullmatch(r"(\d+)([hwdm])", duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: '{duration_str}'. Expected format like '1w', '1d', '2h', '30m'.")

    value = int(match.group(1))
    unit = match.group(2)

    delta = None
    if unit == "h":
        delta = timedelta(hours=value)
    elif unit == "m":
        delta = timedelta(minutes=value)
    elif unit == "d":
        delta = timedelta(days=value)
    elif unit == "w":
        delta = timedelta(weeks=value)
    else:
        # This case should not be reachable due to the regex pattern
        raise ValueError(f"Unknown duration unit: '{unit}'. Valid units are 'h', 'm', 'd', 'w'.")

    from_date = to_date - delta

    return from_date, to_date
