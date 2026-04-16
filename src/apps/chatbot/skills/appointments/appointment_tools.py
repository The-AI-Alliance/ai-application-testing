"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from langchain_core.tools import tool

from apps.chatbot.tools.appointment_manager import AppointmentManager, AppointmentError

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
def create_appointment(patient_name: str, appointment_time: str, reason: str) -> dict[str, Any]:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Name of the patient
        appointment_time: ISO format datetime string (e.g., "2026-04-15T10:00:00")
        reason: Reason for the appointment
        
    Returns:
        Dictionary with appointment details including appointment_id
        
    Example:
        create_appointment("John Doe", "2026-04-15T10:00:00", "Annual checkup")
    """
    try:
        appt_time = datetime.fromisoformat(appointment_time)
        tool = get_appointment_manager()
        result = tool.create_appointment(patient_name, appt_time, reason)
        return result
    except AppointmentError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": f"Invalid datetime format: {e}"}


@tool
def cancel_appointment(appointment_id: str) -> dict[str, Any]:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
        
    Returns:
        Dictionary with cancellation confirmation
        
    Example:
        cancel_appointment("abc123-def456")
    """
    try:
        tool = get_appointment_manager()
        result = tool.cancel_appointment(appointment_id)
        return result
    except AppointmentError as e:
        return {"success": False, "error": str(e)}


@tool
def confirm_appointment(criteria: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Confirm an existing appointment.
    
    Args:
        criteria: one or more fields to search with
        
    Returns:
        List of matching dictionaries, updated with confirmation details.
        If the input criteria is empty, then all appointments are returned, but unchanged.
        if an error of some kind occurs `{"success": False, "error": error_message}` is returned.
        
    Example:
        confirm_appointment({
            'appointment_time': datetime(2026, 4, 20, 8),
            'patient_name': "John Doe",
        })
    """
    try:
        tool = get_appointment_manager()        
        result = tool.confirm_appointment(criteria)
        return result
    except AppointmentError as e:
        return {"success": False, "error": str(e)}


@tool
def change_appointment(appointment_id: str, new_time: str) -> dict[str, Any]:
    """
    Change an appointment to a new time.
    
    Args:
        appointment_id: ID of the appointment to change
        new_time: New ISO format datetime string
        
    Returns:
        Dictionary with old and new times
        
    Example:
        change_appointment("abc123-def456", "2026-04-16T14:00:00")
    """
    try:
        new_datetime = datetime.fromisoformat(new_time)
        tool = get_appointment_manager()
        result = tool.change_appointment(appointment_id, new_datetime)
        return result
    except AppointmentError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": f"Invalid datetime format: {e}"}


@tool
def list_appointments(include_past: bool = False, status_filter: str = '') -> dict[str, Any]:
    """
    List all active appointments.
    
    Args:
        include_past: Whether to include past appointments (default: False)
        status_filter: Optional status to filter by (e.g., 'scheduled', 'confirmed')
        
    Returns:
        Dictionary with list of appointments
        
    Example:
        list_appointments()
        list_appointments(include_past=True)
        list_appointments(status_filter="confirmed")
    """
    try:
        tool = get_appointment_manager()
        appointments = tool.list_appointments(include_past, status_filter)
        return {
            "success": True,
            "count": len(appointments),
            "appointments": appointments
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export all tools as a list for easy registration
# Note that create_appointment_manager is not in this list. It is handled
# internally and not exposed as a tool.
APPOINTMENT_TOOLS = [
    create_appointment,
    cancel_appointment,
    confirm_appointment,
    change_appointment,
    list_appointments,
]

# Made with Bob