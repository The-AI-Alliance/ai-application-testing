"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

from datetime import datetime, date, time

from langchain_core.tools import tool

friendly_date_format = "%A, %B %d %Y"
friendly_time_format = "%I:%m %p"
friendly_datetime_format = f"{friendly_date_format}, at {friendly_time_format}"

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
def is_week_day(a_datetime: datetime) -> bool:
    """
    Return `True` if the input date is a week day, or return `False`.
    
    Args:
        
    Returns:
        a_datetime: `datetime.datetime`
        
    Example:
        is_week_day()
    """
    weekday = a_datetime.weekday() 
    return weekday >= 0 and weekday < 5

# Tools to convert to and from strings.

@tool
def datetime_to_str(a_datetime: datetime, format: str = friendly_datetime_format) -> str:
    """
    Format the input `a_datetime` as a string using the input `format`.
    """
    return a_datetime.strftime(format)

@tool
def date_to_str(a_datetime: datetime, format: str = friendly_date_format) -> str:
    """
    Return the date part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_datetime.date().strftime(format)

@tool
def time_to_str(a_datetime: datetime, format: str = friendly_time_format) -> str:
    """
    Return the time part of the input `datetime` object formatted as
    a string using the input `format`.
    """
    return a_datetime.time().strftime(format)

@tool
def str_to_datetime(a_datetime_str: str, format: str = friendly_datetime_format) -> datetime:
    """
    Using the input `datetime` object, format and return a string using the input `format`.
    """
    return datetime.strptime(a_datetime_str, format)

@tool
def iso_format_str_to_datetime(a_datetime_str: str) -> datetime:
    """
    Return a `datetime` parsed from the ISO format-compatible input string.
    """
    return datetime.fromisoformat(a_datetime_str)

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
