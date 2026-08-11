"""Utilities for working with dates and times."""

# Allow types to self-reference during their definitions.
from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta, timezone, tzinfo

# Too many of these warnings for variables that ARE used in other files.
# pylint: disable=unused-variable

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
def_friendly_date_output_format = "%A, %B %d, %Y"  # pylint: disable=invalid-name
def_friendly_time_output_format = "%I:%M:%S %p %Z"  # pylint: disable=invalid-name
def_friendly_date_time_output_format = (  # pylint: disable=invalid-name
    def_friendly_date_output_format + " " + def_friendly_time_output_format
)

timestamp_str_fmt = "%Y:%m:%d %H:%M:%S%:z"  # pylint: disable=invalid-name
timestamp_file_fmt = "%Y-%m-%d_%H-%M-%S_%Z"  # pylint: disable=invalid-name

one_day = timedelta(days=1)
one_hour = timedelta(hours=1)
one_second = timedelta(seconds=1)

local_timezone = datetime.now(UTC).astimezone().tzinfo

# Define these as within one day of the actual values, because calling
# datetime.min.astimezone() and datetime.max.astimezone(), both fail!
local_datetime_min: datetime = (datetime.min + one_day).astimezone()  # noqa: DTZ901
local_datetime_max: datetime = (datetime.max - one_day).astimezone()  # noqa: DTZ901
local_date_min: date = local_datetime_min.date()
local_date_max: date = local_datetime_max.date()

def_start_hour_inclusive: int = 8  # pylint: disable=invalid-name
def_end_hour_inclusive: int = 17  # pylint: disable=invalid-name


def datetimes_approx_equal(datetime1: datetime, datetime2: datetime, delta: timedelta) -> tuple[bool, str]:
    """
    Are the input `datetimes` equal within the specified `timedelta`?
    """
    # If delta is negative, convert it to positive so the logic below works!
    delta_neg = -delta
    delta = max(delta, delta_neg)
    upper = datetime1 + delta
    lower = datetime1 - delta
    close = datetime1 == datetime2 or (upper >= datetime2 and lower <= datetime2)  # pylint: disable=chained-comparison
    msg = ""
    if not close:
        msg = f"{datetime1} == {datetime2} NOT within +- {delta}"
    return close, msg


def add_timezone(dt: datetime, tz: tzinfo | None = None) -> datetime:
    """
    If the input `datetime` doesn't have timezone information, add
    the input timezone, `tz`. If `tz` is `None`, use the local timezone.
    """
    if dt.tzinfo:
        return dt
    if not tz:
        tz = local_timezone
    return datetime.combine(dt.date(), dt.time(), tz)
    # return dt.astimezone(tz)


def now(tz: timezone | None = None) -> datetime:
    """
    Return the `datetime.datetime` for right now.

    Args:
        tz - Optional timezone. If None, the local timezone is used.

    Returns:
        The current `datetime.datetime`

    Example:
        now(tz=timezone.utc)
    """
    tz2 = tz if tz else local_timezone
    return datetime.now(tz=tz2)


def now_str(fmt: str = timestamp_str_fmt, tz: timezone | None = None) -> str:
    """Return the current time as a string with the input format."""
    return now(tz=tz).strftime(fmt)


today = now().date()
yesterday = today - one_day
tomorrow = today + one_day


def is_week_day(dt: datetime | date) -> bool:
    """
    Return `True` if the input date is a week day, or return `False`.

    Args:
        dt: a `datetime`.

    Returns:
        `True` if the input `datetime` is a week day.

    Example:
        is_week_day(now())
    """
    weekday = dt.weekday()
    return weekday >= 0 and weekday < 5  # pylint: disable=chained-comparison


def is_weekend(dt: datetime | date) -> bool:
    """
    Return `True` if the input date is a Saturday or Sunday, or return `False`.

    Args:
        dt: a `datetime`.

    Returns:
        `True` if the input `datetime` is a Saturday or Sunday.

    Example:
        is_weekend(now())
    """
    return not is_week_day(dt)


def is_work_hours(
    dt: datetime,
    weekdays_only: bool = True,
    start_hour_inclusive: int = def_start_hour_inclusive,
    end_hour_inclusive: int = def_end_hour_inclusive,
    holidays: set[tuple[int, int]] | None = None,
) -> bool:
    """
    Returns `True` if the input `datetime` falls within work hours,
    including if it is a weekday (when `weekdays_only` is `True`),
    the hours fall within `start_hour_inclusive` and `end_hour_inclusive`,
    and the date isn't in the optional set of `holidays`.
    """
    if holidays and (dt.month, dt.day) in holidays:
        return False
    return not (weekdays_only and is_week_day(dt) or dt.hour < start_hour_inclusive or dt.hour > end_hour_inclusive)


def _str_to_object[DT](
    date_time_str: str,
    input_format: str,
    friendly_formats: list[str],
    extract: Callable[[datetime], DT],
) -> tuple[DT | None, str]:

    def clean_dt_str(dt_str):
        """Return YYY MM DDTHH MM SS... and variations of the ordering"""
        dt_str2 = dt_str.strip().replace(",", "")
        dt_str3 = re.sub(r" +at +", "T", dt_str2)
        dt_str4 = re.sub(r"\s{2,}", " ", dt_str3)
        dt_str5 = re.sub(r"^(\d{2,4})[-_](\d{2})[-_](\d{2,4})", "\\1 \\2 \\3", dt_str4)
        dt_str6 = re.sub(r"([ T])(\d{2})[-_:](\d{2})[-_:](\d{2})", "T\\2 \\3 \\4", dt_str5)
        return dt_str6

    def fromiso(dt_str):
        try:
            dt = datetime.fromisoformat(dt_str)
            return add_timezone(dt) if dt else None
        except ValueError:
            return None

    def err_msg():
        input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
        return f"""I could not parse string "{date_time_str}" with {input_format_msg}formats, {friendly_formats}, nor using fromisoformat()."""

    dt_str = date_time_str.strip()

    # If no format is provided, try the ISO-format first
    if not input_format.strip():
        dt = fromiso(dt_str)
        if dt:
            return extract(dt), ""

    # Okay, try the the input format and if that fails, the supplied
    # friendly formats. First try without the "cleaning" step, which
    # would cause some formats like %c to fail. Then try the cleaned
    # string.
    fmts = [input_format] + friendly_formats
    for fmt in fmts:
        if not fmt:  # skip empties...
            continue
        try:
            dt = datetime.strptime(dt_str, fmt)  # noqa: DTZ007
            if not dt:
                dt = datetime.strptime(clean_dt_str(dt_str), fmt)  # noqa: DTZ007
            if dt:
                return extract(add_timezone(dt)), ""
        except ValueError:
            pass

    # If here, none of our "friendly formats" worked. Try ISO, which
    # will be a repeat attempt if "input_format" is empty, which is
    # harmless, if slightly wasteful...
    dt = fromiso(dt_str)
    if dt:
        return extract(dt), ""
    return None, err_msg()


def string_to_datetime(date_time_str: str, input_format: str = "") -> tuple[datetime | None, str]:
    """
    Using the input `date_time_str` string, format and return a `datetime` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat()`. If that fails, we return an
    error message.

    Args:
        - date_time_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `datetime` and an empty string or `None` and an error message.
    """
    return _str_to_object(date_time_str, input_format, friendly_date_time_formats, lambda dt: dt)


def string_to_date(date_str: str, input_format: str = "") -> tuple[date | None, str]:
    """
    Using the input `date_str` string, format and return a `date` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat()`. If that fails, we return an
    error message.

    Args:
        - date_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `date` and an empty string or `None` and an error message.
    """
    return _str_to_object(date_str, input_format, friendly_date_formats, lambda dt: dt.date())


def string_to_time(time_str: str, input_format: str = "") -> tuple[time | None, str]:
    """
    Using the input `time_str` string, format and return a `time` parsed
    using the input `input_format`, if not empty. If the format is empty or parsing with
    it fails, we try a list of "friendly" formats and hope one of them works. If none works,
    we try passing the string to `datetime.fromisoformat().time()`. If that fails, we return an
    error message.

    Args:
        - time_str (str): The string to parse.
        - input_format (str): The format that should be tried first, if not empty.

    Returns:
        a tuple with the constructed `time` and an empty string or `None` and an error message.
    """
    return _str_to_object(time_str, input_format, friendly_time_formats, lambda dt: dt.time())


def iso_format_string_to_datetime(date_time_str: str) -> datetime:
    """
    Return a `datetime` parsed from the ISO format-compatible input string.
    Add the local timezone if not defined in the parsed datetime.
    """
    return add_timezone(datetime.fromisoformat(date_time_str))
