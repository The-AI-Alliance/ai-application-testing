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
_def_appointments_file = Path("../output/appointments.jsonl")
_def_appointment_manager_logger = logging.getLogger('AppointmentManager')
_def_appointment_manager_logger.setLevel(logging.INFO)
_appointment_manager: Optional[AppointmentManager] = None

def get_appointment_manager(
    file_path: Path | str = None, 
    logger: logging.Logger = None,
    make_new: bool = False) -> AppointmentManager:
    """
    Idempotent: Creates and an instance only if one of the following is true:
    1. It doesn't already exist.
    2. `make_new` is True.
    Otherwise, the existing instance is returned. 

    Args:
        - file_path (Path): Ignored unless a new manager is to be created.
          The storage location. If `None`, then `_def_appointments_file` is used.
        - logger (logging.Logger): Ignored unless a new manager is to be created.
          The logger. If `None`, then `_def_appointment_manager_logger` is used.
    """
    global _appointment_manager

    if _appointment_manager and not make_new:
        return _appointment_manager

    # Determine the correct file path value:
    fp: Path | None = None
    if file_path:
        fp = Path(file_path)
    else:
        fp = _def_appointments_file

    # Determine the logger value
    if not logger:
        logger = _def_appointment_manager_logger  # assign the default logger
    
    _appointment_manager = AppointmentManager(fp, logger)
    logger.info(f"Created a new AppointmentManager({fp}, logger).")
    return _appointment_manager

@tool
def create_appointment(patient_name: str, appointment_date_time: str, reason: str) -> Tuple[str, str]:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Name of the patient
        appointment_date_time: ISO format datetime string (e.g., "2026-04-15T10:00:00")
        reason: Reason for the appointment
        
    Returns:
        A tuple with the ID for the newly-created appointment and a success message, or a tuple with '' and a failure message with reasons for the failure.
        
    Example:
        create_appointment("John Doe", "2026-04-15T10:00:00", "Annual checkup")
    """
    appt_dt = datetime.fromisoformat(appointment_date_time)
    am = get_appointment_manager()
    return am.create_appointment(patient_name, appt_dt, reason)

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
    am = get_appointment_manager()
    return am.cancel_appointment(appointment_id)

@tool
def change_appointment(appointment_id: str, new_date_time: str) -> Tuple[bool, str]:
    """
    Change an appointment to a new time.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.
    
    Args:
        appointment_id: ID of the appointment to change
        new_date_time: New ISO format datetime string
        
    Returns:
        True with success message or False with a failure message with reasons for the failure.
        
    Example:
        change_appointment("abc123-def456", "2026-04-16T14:00:00")
    """
    new_dt = datetime.fromisoformat(new_date_time)
    am = get_appointment_manager()
    return am.change_appointment(appointment_id, new_dt)

@tool
def list_appointments(patient_name: str = '', after_date_time: str = '') -> list[dict[str, Any]]:
    """
    List all active appointments, with optional filtering.
    
    Args:
        patient_name: Only return appointments for this patient (default: all patients)
        after_date_time: Don't include appointments before this date time. If empty, the value `datetime.now().isoformat()` will be used to only return future appointments.
        
    Returns:
        List of dictionaries for the located appointments
        
    Example:
        list_appointments()
        list_appointments(after_date_time="2026-04-10 13:00:00")
        list_appointments(patient_name="John Doe")
    """
    am = get_appointment_manager()
    after_dt = datetime.fromisoformat(after_date_time) if after_date_time else datetime.now()
    return am.list_appointments(patient_name = patient_name, after_date_time = after_dt)


@tool
def get_appointments_count() -> int:
    """
    Return the number of appointments currently scheduled for all patients.
    """
    am = get_appointment_manager()
    return am.get_appointments_count()

@tool
def get_appointment(appointment_id: str) -> dict[str, Any]:
    """
    Return a specific appointment for the specified ID.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.
    
    Args:
        appointment_id: ID of the appointment
        
    Returns:
        Appointment dictionary for the input ID or {} if a matching appointment was not found
    """
    am = get_appointment_manager()
    return am.get_appointment(appointment_id)

@tool
def get_appointment_id_for_name_and_date_time( 
    patient_name: str,
    appointment_date_time: str) -> str:
    """
    Retrieve the appointment ID for the specified patient and date time.
    
    Args:
        patient_name: Name of the patient
        appointment_date_time: Date time of the appointment
        appointment_date_time: ISO format datetime string (e.g., "2026-04-15T10:00:00")
        
    Returns:
        ID of the appointment or '' if there is no appointment for that patient at that date time.
    """
    am = get_appointment_manager()
    appointment_dt = datetime.fromisoformat(appointment_date_time)
    return am.get_appointment_id_for_name_and_date_time(patient_name, appointment_dt)

# Export all tools as a list for easy registration
# Note that get_appointment_manager is not a tool and so it is not in this list. 
# It is used internally.
APPOINTMENT_TOOLS = [
    create_appointment,
    cancel_appointment,
    change_appointment,
    list_appointments,
    get_appointments_count,
    get_appointment,
    get_appointment_id_for_name_and_date_time,
]
