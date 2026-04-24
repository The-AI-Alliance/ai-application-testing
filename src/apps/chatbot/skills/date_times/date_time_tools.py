"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

from datetime import datetime, date, time

from langchain_core.tools import tool

friendly_date_formats = [
    "%A, %B %d, %Y",
    "%A, %b %d, %Y",
    "%A %B %d, %Y",
    "%A %b %d, %Y",
    "%A, %B %d %Y",
    "%A, %b %d %Y",
    "%A %B %d %Y",
    "%A %b %d %Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%b %d %Y",

    "%A, %Y-%m-%d",
    "%A %Y-%m-%d",
    "%Y-%m-%d",
]

friendly_time_formats = [
    "%I:%M %p",
    "%I:%M",
    "%I %p",
    "%I",
]

friendly_date_time_formats = ["%c", "%x %X"]
for d in friendly_date_formats:
    for t in friendly_time_formats:
        friendly_date_time_formats.append(f"{d} {t}")
        friendly_date_time_formats.append(f"{d}T{t}")
        friendly_date_time_formats.append(f"{d}, at {t}")

friendly_date_formats.append("%x") # add this AFTER the previous loop.
friendly_time_formats.append("%X") # add this AFTER the previous loop.
def_friendly_date_time_format = friendly_date_time_formats[0]
def_friendly_date_format      = friendly_date_formats[0]
def_friendly_time_format      = friendly_time_formats[0]

@tool
def now() -> datetime:
    """
    Return the `datetime.datetime` for right now.
    
    Args:
        
    Returns:
        The current `datetime.datetime`
        
    Example:
        now()
    """
    return datetime.now()


@tool
def today() -> date:
    """
    Return the `datetime.date` for today's date.
    
    Args:
        
    Returns:
        Today's `datetime.date`
        
    Example:
        today()
    """
    return datetime.now().date()

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
def datetime_to_str(a_date_time: datetime, output_format: str = def_friendly_date_time_format) -> str:
    """
    Format the input `a_date_time` as a string using the input `format`.
    """
    return a_date_time.strftime(output_format)

@tool
def date_to_str(a_date: date, output_format: str = def_friendly_date_format) -> str:
    """
    Return the date part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_date.strftime(output_format)

@tool
def time_to_str(a_time: time, output_format: str = def_friendly_time_format) -> str:
    """
    Return the time part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_time.strftime(output_format)

@tool
def str_to_datetime(a_date_time_str: str, input_format: str = '') -> tuple[datetime, str]:
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
    fmts = [input_format] + friendly_date_time_formats if input_format else friendly_date_time_formats
    for fmt in fmts:
        try:
            return datetime.strptime(a_date_time_str, fmt), ''
        except ValueError as ve:
            pass
    try:
        return datetime.fromisoformat(a_date_time_str), ''
    except ValueError as ve:
        # If here, we failed...
        input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
        return None, f"""I could not parse date time string "{a_date_time_str}" with {input_format_msg}formats: {friendly_date_time_formats}"""

@tool
def str_to_date(a_date_str: str, input_format: str = '') -> tuple[date, str]:
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
    fmts = [input_format] + friendly_date_formats if input_format else friendly_date_formats
    for fmt in fmts:
        try:
            dt = datetime.strptime(a_date_str, fmt)
            if dt:
                return dt.date(), ''
        except ValueError as ve:
            pass
    try:
        dt = datetime.fromisoformat(a_date_str)
        if dt:
            return dt.date(), ''
    except ValueError as ve:
        # If here, we failed...
        input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
        return None, f"""I could not parse date string "{a_date_str}" with {input_format_msg}formats: {friendly_date_formats}"""

@tool
def str_to_time(a_time_str: str, input_format: str = '') -> tuple[time, str]:
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
    fmts = [input_format] + friendly_time_formats if input_format else friendly_time_formats
    for fmt in fmts:
        try:
            dt = datetime.strptime(a_time_str, fmt)
            if dt:
                return dt.time(), ''
        except ValueError as ve:
            pass
    try:
        dt = datetime.fromisoformat(a_time_str)
        if dt:
            return dt.time(), ''
    except ValueError as ve:
        # If here, we failed...
        input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
        return None, f"""I could not parse time string "{a_time_str}" with {input_format_msg}formats: {friendly_time_formats}"""

@tool
def iso_format_str_to_datetime(a_date_time_str: str) -> datetime:
    """
    Return a `datetime` parsed from the ISO format-compatible input string.
    """
    return datetime.fromisoformat(a_date_time_str)

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
