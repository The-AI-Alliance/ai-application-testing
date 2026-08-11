"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

from datetime import date, datetime, time, timezone

from langchain_core.tools import tool

from common.date_time_utils import (
    add_timezone,
    def_friendly_date_output_format,
    def_friendly_date_time_output_format,
    def_friendly_time_output_format,
)
from common.date_time_utils import (
    is_week_day as is_week_day_util,
)
from common.date_time_utils import (
    now as now_util,
)
from common.date_time_utils import (
    string_to_date as string_to_date_util,
)
from common.date_time_utils import (
    string_to_datetime as string_to_datetime_util,
)
from common.date_time_utils import (
    string_to_time as string_to_time_util,
)

# Too many of these warnings for variables that ARE used in other files.
# pylint: disable=unused-variable

@tool
def now(tz: timezone | None = None) -> datetime:
    """
    Return the `datetime.datetime` for right now.

    Args:
        tz - Optional timezone. The local timezone is used, if None.

    Returns:
        The current `datetime.datetime`

    Example:
        now()
    """
    return now_util(tz)


@tool
def today(tz: timezone | None = None) -> date:
    """
    Return the `datetime.date` for today's date.

    Args:

    Returns:
        Today's `datetime.date`

    Example:
        today()
    """
    return now_util(tz=tz).date()


@tool
def is_week_day(a_date_time: datetime) -> bool:
    """
    Return `True` if the input date is a week day, or return `False`.

    Args:
        a_date_time: a `datetime`.

    Returns:
        `True` if the input `datetime` is a week day.

    Example:
        is_week_day(now())
    """
    return is_week_day_util(a_date_time)


# Tools to convert to and from strings.


@tool
def datetime_to_string(a_date_time: datetime, output_format: str = def_friendly_date_time_output_format) -> str:
    """
    Format the input `a_date_time` as a string using the input `format`.
    """
    return a_date_time.strftime(output_format)


@tool
def date_to_string(a_date: date, output_format: str = def_friendly_date_output_format) -> str:
    """
    Return the date part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_date.strftime(output_format)


@tool
def time_to_string(a_time: time, output_format: str = def_friendly_time_output_format) -> str:
    """
    Return the time part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_time.strftime(output_format)


@tool
def string_to_datetime(a_date_time_str: str, input_format: str = "") -> tuple[datetime | None, str]:
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
    return string_to_datetime_util(a_date_time_str, input_format)


@tool
def string_to_date(a_date_str: str, input_format: str = "") -> tuple[date | None, str]:
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
    return string_to_date_util(a_date_str, input_format)


@tool
def string_to_time(a_time_str: str, input_format: str = "") -> tuple[time | None, str]:
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
    return string_to_time_util(a_time_str, input_format)


@tool
def iso_format_string_to_datetime(a_date_time_str: str) -> datetime:
    """
    Return a `datetime` parsed from the ISO format-compatible input string.
    Add the local timezone if not defined in the parsed datetime.
    """
    return add_timezone(datetime.fromisoformat(a_date_time_str))


# Export all tools as a list for easy registration
# Note that create_appointment_manager is not in this list. It is handled
# internally and not exposed as a tool.
DATE_TIME_TOOLS = [
    now,
    is_week_day,
    datetime_to_string,
    date_to_string,
    time_to_string,
    iso_format_string_to_datetime,
    string_to_datetime,
    string_to_date,
    string_to_time,
]
