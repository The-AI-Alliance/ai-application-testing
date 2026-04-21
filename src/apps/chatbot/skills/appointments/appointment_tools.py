"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

from langchain_core.tools import tool

from apps.chatbot.tools.appointment_manager import AppointmentManager

# Initialize the appointment tool with a default file location
# This will be overridden when integrated with the ChatBot
_appointments_file = Path("../output/appointments.jsonl")
_appointment_manager_logger = logging.getLogger('AppointmentManager')
_appointment_manager_logger.setLevel(logging.INFO)
_appointment_manager: Optional[AppointmentManager] = None

def get_appointment_manager(
    file_path: Path | str = _appointments_file, 
    logger: logging.Logger = _appointment_manager_logger) -> AppointmentManager:
    """
    Idempotent: Creates and returns a tool if:
    1. It doesn't already exist.
    2. It exists but the input `file_path` is different than the value in the current instance.
    3. It exists but the input `logger` is not `None` and it is different than the value in the current instance.
    Otherwise, the existing tool is returned.
    """
    global _appointments_file
    global _appointment_manager
    global _appointment_manager_logger
    
    create = False
    if not logger and not _appointment_manager_logger == logger:
        _appointment_manager_logger = logger
        create = True

    fp = Path(file_path)
    if _appointments_file != fp:
        _appointments_file = fp
        create = True

    if create or not _appointment_manager:
        _appointment_manager = AppointmentManager(_appointments_file, _appointment_manager_logger)

    return _appointment_manager

def set_appointments_file(file_path: Path | str) -> None:
    """
    Set the appointments file path and reinitialize the tool, unless
    the tool already exists and already has the same file!.
    If the tool already exists, but the file path is new, we reuse the logger.
    
    Args:
        file_path: Path to the appointments JSONL file
    """
    logger = _appointment_manager.logger if _appointment_manager else _appointment_manager_logger
    get_appointment_manager(file_path = file_path, logger = logger)

@tool
def create_appointment(patient_name: str, appointment_date_time: str, reason: str) -> Tuple[bool, str]:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Name of the patient
        appointment_date_time: ISO format datetime string (e.g., "2026-04-15T10:00:00")
        reason: Reason for the appointment
        
    Returns:
        True with success message or False with a failure message with reasons for the failure.
        
    Example:
        create_appointment("John Doe", "2026-04-15T10:00:00", "Annual checkup")
    """
    appt_time = datetime.fromisoformat(appointment_date_time)
    tool = get_appointment_manager()
    return tool.create_appointment(patient_name, appt_time, reason)

@tool
def cancel_appointment(appointment_id: str) -> Tuple[bool, str]:
    """
    Cancel an existing appointment, specified by the appointment ID.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.
    
    Args:
        appointment_id: ID of the appointment to cancel
        
    Returns:
        True with success message or False with a failure message with reasons for the failure.
        
    Example:
        cancel_appointment("abc123-def456")
    """
    tool = get_appointment_manager()
    return tool.cancel_appointment_by_id(appointment_id)

@tool
def change_appointment(appointment_id: str, new_date_time: str) -> Tuple[bool, str]:
    """
    Change an appointment to a new time.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.
    
    Args:
        appointment_id: ID of the appointment to change
        new_time: New ISO format datetime string
        
    Returns:
        True with success message or False with a failure message with reasons for the failure.
        
    Example:
        change_appointment("abc123-def456", "2026-04-16T14:00:00")
    """
    new_datetime = datetime.fromisoformat(new_date_time)
    tool = get_appointment_manager()
    return tool.change_appointment(appointment_id, new_datetime)

@tool
def list_appointments(patient_name: str = '', after_datetime: datetime = datetime.min) -> dict[str, Any]:
    """
    List all active appointments, with optional filtering.
    
    Args:
        patient_name: Only return appointments for this patient (default: all patients)
        after_datetime: Don't include appointments before this date time. Pass `datetime.now()` to only return future appointments.
        
    Returns:
        Dictionary with list of appointments
        
    Example:
        list_appointments()
        list_appointments(include_past=True)
        list_appointments(status_filter="confirmed")
    """
    tool = get_appointment_manager()
    return tool.list_appointments(include_past, status_filter)


@tool
def get_appointments_count() -> int:
    """Return the number of appointments currently scheduled."""
    tool = get_appointment_manager()
    return len(tool.get_appointments_count())

@tool
def get_appointment_by_id(self, appointment_id: str) -> dict[str, Any]:
    """
    Return a specific appointment for the specified ID.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.
    
    Args:
        appointment_id: ID of the appointment
        
    Returns:
        Appointment dictionary or {} if not found
    """
    tool = get_appointment_manager()
    return tool.get_appointment_by_id(appointment_id)


@tool
def get_appointment_id_for_name_and_date_time(self, 
    patient_name: str,
    appointment_date_time: datetime) -> str:
    """
    Retrieve the appointment ID for the specified patient and date time.
    
    Args:
        patient_name: Name of the patient
        appointment_date_time: Date time of the appointment
        
    Returns:
        ID of the appointment or '' if there is no appointment for that patient at that date time.
    """
    tool = get_appointment_manager()
    return tool.get_appointment_id_for_name_and_date_time(patient_name, appointment_date_time)

# Export all tools as a list for easy registration
# Note that create_appointment_manager is not in this list. It is handled
# internally and not exposed as a tool.
APPOINTMENT_TOOLS = [
    create_appointment,
    cancel_appointment,
    change_appointment,
    list_appointments,
    get_appointments_count,
    get_appointment_by_id,
    get_appointment_id_for_name_and_date_time,
]
