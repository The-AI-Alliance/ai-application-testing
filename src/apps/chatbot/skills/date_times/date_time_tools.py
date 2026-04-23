"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

from datetime import datetime, date, time

from langchain_core.tools import tool

friendly_date_format_day               = "%A, %B %d %Y"
friendly_date_format                   = "%B %d %Y"
friendly_date_formats = [
    friendly_date_format_day,
    friendly_date_format,
]

friendly_time_format_mins_secs_pm      = "%I:%M %p"
friendly_time_format_mins_secs         = "%I:%M"
friendly_time_format_mins_pm           = "%I %p"
friendly_time_format_mins              = "%I"
friendly_time_formats = [
    friendly_time_format_mins_secs_pm,
    friendly_time_format_mins_secs,
    friendly_time_format_mins_pm,
    friendly_time_format_mins,
]


friendly_date_time_formats = []
for d in friendly_date_formats:
    for t in friendly_time_formats:
        friendly_date_time_formats.append(f"{d}, at {t}")

def_friendly_date_time_format = friendly_date_time_formats[0]
def_friendly_date_format      = friendly_date_format_day
def_friendly_time_format      = friendly_time_format_mins_secs_pm

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
def str_to_datetime(a_date_time_str: str, input_format: str = '') -> datetime:
    """
    Using the input `a_date_time_str` string, format and return a datetime parsed 
    using the input `format`, if not empty. If the format is empty or parsing fails,
    we try a list of "friendly" formats and hope one of them works. If non works, 
    a `ValueError` is raised.
    """
    fmts = [input_format] + friendly_date_time_formats if input_format else friendly_date_time_formats
    for fmt in fmts:
        try:
            return datetime.strptime(a_date_time_str, fmt)
        except ValueError as ve:
            pass
    # If here, we failed...
    input_format_msg = "" if not format else f"""input format "{input_format}", nor other """
    raise ValueError(f"""Could not parse date time string "{a_date_time_str}" with {input_format_msg}formats: {friendly_formats}""")

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
    str_to_datetime,
    iso_format_str_to_datetime,
]
