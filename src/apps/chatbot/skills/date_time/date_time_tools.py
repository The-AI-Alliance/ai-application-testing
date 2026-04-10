"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

from datetime import datetime

from langchain_core.tools import tool

@tool
def now() -> datetime:
    """
    Return the `datetime` for right now.
    """
    return datetime.now()

@tool
def now_str() -> str:
    """
    Return the `datetime` for right now.
    """
    return str(datetime.now())

# Export all tools as a list for easy registration
# Note that create_appointment_tool is not in this list. It is handled
# internally and not exposed as a tool.
DATE_TIME_TOOLS = [
    now,
    now_str,
]
