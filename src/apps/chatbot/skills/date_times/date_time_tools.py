"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

import re
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timezone

from langchain_core.tools import tool

# The "friendly" formats used for parsing strings. They don't include
# punctuation. They are used by _str_to_object() where punctuation
# will be removed from input date-time strings and they will also be
# converted to have the date and time separated by a literal "T",
# with optimal timezone information.

friendly_date_formats = [
    "%A %B %d %Y",
    "%A %Y %m %d",
    "%A %b %d %Y",
    "%A %d %B %Y",
    "%A %d %b %Y",
    "%B %d %Y",
    "%b %d %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%Y %m %d",
    "%m %d %Y",
    "%a %B %d %Y",
    "%a %Y %m %d",
    "%a %b %d %Y",
    "%a %d %B %Y",
    "%a %d %b %Y",
]

friendly_time_formats = [
    "%I %M %S %p",
    "%H %M %S",
    "%I %M %p",
    "%H %M",
    "%I %p",
    "%H",
]

friendly_date_time_formats = ["%c", "%x %X"]
for d in friendly_date_formats:
    for t in friendly_time_formats:
        friendly_date_time_formats.append(f"{d}T{t}")
        friendly_date_time_formats.append(f"{d}T{t}%z")
        friendly_date_time_formats.append(f"{d}T{t} %Z")

friendly_date_formats.append("%x")  # add this AFTER the previous loop.
friendly_time_formats.append("%X")  # add this AFTER the previous loop.

# "Friendly" output formats.
def_friendly_date_output_format = "%A, %B %d, %Y"
def_friendly_time_output_format = "%I:%M:%S %p %Z"
def_friendly_date_time_output_format = def_friendly_date_output_format + " " + def_friendly_time_output_format


@tool
def now(tz: timezone = UTC) -> datetime:
    """
    Return the `datetime.datetime` for right now.

    Args:

    Returns:
        The current `datetime.datetime`

    Example:
        now()
    """
    return datetime.now(tz=tz)


@tool
def today(tz: timezone = UTC) -> date:
    """
    Return the `datetime.date` for today's date.

    Args:

    Returns:
        Today's `datetime.date`

    Example:
        today()
    """
    return datetime.now(tz=tz).date()


@tool
def is_week_day(a_date_time: datetime) -> bool:
    """
    Return `True` if the input date is a week day, or return `False`.

    Args:

    Returns:
        a_date_time: `datetime.datetime`

    Example:
        is_week_day()
    """
    weekday = a_date_time.weekday()
    return weekday >= 0 and weekday < 5


# Tools to convert to and from strings.


@tool
def datetime_to_str(a_date_time: datetime, output_format: str = def_friendly_date_time_output_format) -> str:
    """
    Format the input `a_date_time` as a string using the input `format`.
    """
    return a_date_time.strftime(output_format)


@tool
def date_to_str(a_date: date, output_format: str = def_friendly_date_output_format) -> str:
    """
    Return the date part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_date.strftime(output_format)


@tool
def time_to_str(a_time: time, output_format: str = def_friendly_time_output_format) -> str:
    """
    Return the time part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_time.strftime(output_format)


def _str_to_object[DT](
    a_date_time_str: str,
    input_format: str,
    friendly_formats: list[str],
    extract: Callable[[datetime], DT],
) -> tuple[DT | None, str]:

    def clean_dt_str(dt_str):
        """Return YYY MM DDTHH MM SS... and variations of the ordering"""
        dt_str2 = dt_str.strip().replace(",", "")
        dt_str3 = re.sub(" +at +", "T", dt_str2)
        dt_str4 = re.sub(r"^(\d{2,4})[-_](\d{2})[-_](\d{2,4})", "\\1 \\2 \\3", dt_str3)
        dt_str5 = re.sub(r"([ T])(\d{2})[-_:](\d{2})[-_:](\d{2})", "T\\2 \\3 \\4", dt_str4)
        return dt_str5

    def fromiso(dt_str):
        try:
            dt = datetime.fromisoformat(dt_str)
            if dt:
                if not dt.tzinfo:
                    dt = dt.astimezone(UTC)
                return dt
            else:
                return None
        except ValueError:
            return None

    def err_msg():
        input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
        return f"""I could not parse string "{a_date_time_str}" with {input_format_msg}formats, {friendly_formats}, nor using fromisoformat()."""

    dt_str = a_date_time_str.strip()

    # If no format is provided, try the ISO-format first
    if not input_format.strip():
        dt = fromiso(dt_str)
        if dt:
            return extract(dt), ""

    fmts = [input_format] + friendly_formats
    for fmt in fmts:
        if not fmt:  # skip empties...
            continue
        try:
            dt = datetime.strptime(clean_dt_str(dt_str), fmt)  # noqa: DTZ007
            if dt:
                if not dt.tzinfo:
                    dt = dt.astimezone(UTC)
                return extract(dt), ""
        except ValueError:
            pass

    # If here, none of our "friendly formats" worked. Try ISO, which
    # will be a repeat attempt if "input_format" is empty, which is
    # harmless, if slightly wasteful...
    dt = fromiso(dt_str)
    if dt:
        return extract(dt), ""
    else:
        return None, err_msg()


@tool
def str_to_datetime(a_date_time_str: str, input_format: str = "") -> tuple[datetime | None, str]:
    """
    Using the input `a_date_time_str` string, format and return a `datetime` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat()`. If that fails, we return an
    error message.

    Args:
        - a_date_time_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `datetime` and an empty string or `None` and an error message.
    """
    return _str_to_object(a_date_time_str, input_format, friendly_date_time_formats, lambda dt: dt)


@tool
def str_to_date(a_date_str: str, input_format: str = "") -> tuple[date | None, str]:
    """
    Using the input `a_date_str` string, format and return a `date` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat()`. If that fails, we return an
    error message.

    Args:
        - a_date_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `date` and an empty string or `None` and an error message.
    """
    return _str_to_object(a_date_str, input_format, friendly_date_formats, lambda dt: dt.date())


@tool
def str_to_time(a_time_str: str, input_format: str = "") -> tuple[time | None, str]:
    """
    Using the input `a_time_str` string, format and return a `time` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat().time()`. If that fails, we return an
    error message.

    Args:
        - a_time_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `time` and an empty string or `None` and an error message.
    """
    return _str_to_object(a_time_str, input_format, friendly_time_formats, lambda dt: dt.time())


@tool
def iso_format_str_to_datetime(a_date_time_str: str) -> datetime:
    """
    Return a `datetime` parsed from the ISO format-compatible input string.
    Add the UTC timezone if not defined in the parsed datetime.
    """
    dt = datetime.fromisoformat(a_date_time_str)
    if not dt.tzinfo:
        dt = dt.astimezone(UTC)
    return dt


# Export all tools as a list for easy registration
# Note that create_appointment_manager is not in this list. It is handled
# internally and not exposed as a tool.
DATE_TIME_TOOLS = [
    now,
    is_week_day,
    datetime_to_str,
    date_to_str,
    time_to_str,
    iso_format_str_to_datetime,
    str_to_datetime,
    str_to_date,
    str_to_time,
]
