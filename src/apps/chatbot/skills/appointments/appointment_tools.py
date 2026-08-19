"""
LangChain tool wrappers for the appointment management functionality.
These tools are used by the Deep Agent's appointment skill.
"""

import logging
from collections.abc import MutableMapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from apps.chatbot.tools.appointment_manager import AppointmentManager
from common.date_time_utils import now


class AppointmentManagerTool:  # pylint: disable=too-few-public-methods
    """Holds "global" objects for appointment management, but in a more OO way."""

    # Initialize the appointment tool with a default file location
    # This will be overridden when integrated with the ChatBot
    def_appointments_file = Path("../output/appointments.jsonl")
    def_appointment_manager_logger = logging.getLogger("AppointmentManager")
    def_appointment_manager_logger.setLevel(logging.INFO)
    appointment_manager: AppointmentManager
    appointment_manager_initialized: bool = False


def get_appointment_manager(
    file_path: Path | str = "",
    logger: logging.Logger | None = None,
    make_new: bool = False,
) -> AppointmentManager:
    """
    Idempotent: Creates and an instance only if one of the following is true:
    1. It doesn't already exist.
    2. `make_new` is True.
    Otherwise, the existing instance is returned, even if different arguments
    for logger and file_path are passed!

    Args:
        - file_path (Path): Ignored unless a new manager is to be created.
          The storage location. If empty, then `AppointmentManagerTool.def_appointments_file` is used.
        - logger (logging.Logger): Ignored unless a new manager is to be created.
          The logger. If `None`, then `AppointmentManagerTool.def_appointment_manager_logger` is used.
        - make_new (bool): Whether or not to make a new
    Returns:
        The appointment manager.
    """
    if AppointmentManagerTool.appointment_manager_initialized and not make_new:
        return AppointmentManagerTool.appointment_manager

    # Determine the correct file path value:
    fp: Path | None = None
    if file_path:
        fp = Path(file_path)
    else:
        fp = AppointmentManagerTool.def_appointments_file

    # Determine the logger value
    if not logger:
        logger = AppointmentManagerTool.def_appointment_manager_logger  # assign the default logger

    AppointmentManagerTool.appointment_manager = AppointmentManager(appointments_file=fp, logger=logger)
    logger.info(
        "Created a new AppointmentManager (existing appointment count: %d)",
        AppointmentManagerTool.appointment_manager.get_appointments_count(),
    )
    # This version of the previous statement fails the CodeQL check for potential
    # clear text leaks of sensitive data. It is left here for temporary debugging use...
    # logger.info(
    #     "Created a new AppointmentManager(%s, logger) (id = %s, existing appointment count: %d), %s",
    #     fp,
    #     hex(id(AppointmentManagerTool.appointment_manager)),
    #     AppointmentManagerTool.appointment_manager.get_appointments_count(),
    #     AppointmentManagerTool.appointment_manager,
    # )
    AppointmentManagerTool.appointment_manager_initialized = True
    return AppointmentManagerTool.appointment_manager


@tool
def create_appointment(patient_name: str, appointment_date_time: str, reason: str) -> tuple[str, str]:
    """
    Create a new appointment for a patient.

    Args:
        - patient_name (str): Name of the patient
        - appointment_date_time (str): ISO format datetime string (e.g., "2026-04-15T10:00:00")
        - reason (str): Reason for the appointment

    Returns:
        A tuple with the ID for the newly-created appointment and a success message,
        or a tuple with '' and a failure message with reasons for the failure.

    Example:
        create_appointment("John Doe", "2026-04-15T10:00:00", "Annual checkup")
    """
    appt_dt = datetime.fromisoformat(appointment_date_time)
    am = get_appointment_manager()
    return am.create_appointment(patient_name, appt_dt, reason)


@tool
def cancel_appointment(appointment_id: str) -> tuple[bool, str]:
    """
    Cancel an existing appointment, specified by the appointment ID.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.

    Args:
        - appointment_id (str): ID of the appointment to cancel

    Returns:
        True with success message or False with a failure message with reasons for the failure.

    Example:
        cancel_appointment("abc123-def456")
    """
    am = get_appointment_manager()
    return am.cancel_appointment(appointment_id)


@tool
def change_appointment(appointment_id: str, new_date_time: str) -> tuple[bool, str]:
    """
    Change an appointment to a new time.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.

    Args:
        - appointment_id (str): ID of the appointment to change
        - new_date_time (str): New ISO format datetime string

    Returns:
        True with success message or False with a failure message with reasons for the failure.

    Example:
        change_appointment("abc123-def456", "2026-04-16T14:00:00")
    """
    new_dt = datetime.fromisoformat(new_date_time)
    am = get_appointment_manager()
    return am.change_appointment(appointment_id, new_dt)


@tool
def get_appointments(patient_name: str = "", after_date_time: str = "") -> Sequence[MutableMapping[str, Any]]:
    """
    List all active appointments, with optional filtering.

    Args:
        - patient_name (str): Only return appointments for this patient (default: all patients)
        - after_date_time (str): Don't include appointments before this date time. If empty, the value `now().isoformat()` will be used to only return future appointments.

    Returns:
        List of dictionaries for the located appointments

    Example:
        get_appointments()
        get_appointments(after_date_time="2026-04-10 13:00:00")
        get_appointments(patient_name="John Doe")
    """
    am = get_appointment_manager()
    after_dt = datetime.fromisoformat(after_date_time) if after_date_time else now()
    return am.get_appointments(patient_name=patient_name, after_date_time=after_dt)


@tool
def get_appointments_count() -> int:
    """
    Return the number of appointments currently scheduled for all patients.
    """
    am = get_appointment_manager()
    return am.get_appointments_count()


@tool
def get_appointment_by_id(appointment_id: str) -> MutableMapping[str, Any]:
    """
    Return a specific appointment for the specified ID.
    Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name
    and appointment date and time, if necessary.

    Args:
        - appointment_id (str): ID of the appointment

    Returns:
        Appointment dictionary for the input ID or {} if a matching appointment was not found
    """
    am = get_appointment_manager()
    return am.get_appointment_by_id(appointment_id)


@tool
def get_appointment_id_for_name_and_date_time(patient_name: str, appointment_date_time: str) -> str:
    """
    Retrieve the appointment ID for the specified patient and date time.

    Args:
        - patient_name (str): Name of the patient
        - appointment_date_time (str): ISO format datetime string (e.g., "2026-04-15T10:00:00")

    Returns:
        ID of the appointment or '' if there is no appointment for that patient at that date time.
    """
    am = get_appointment_manager()
    appointment_dt = datetime.fromisoformat(appointment_date_time)
    return am.get_appointment_id_for_name_and_date_time(patient_name, appointment_dt)


# Export all tools as a list for easy registration
# Note that get_appointment_manager is not a tool and so it is not in this list.
# It is used internally.
APPOINTMENT_TOOLS = [  # pylint: disable=unused-variable
    create_appointment,
    cancel_appointment,
    change_appointment,
    get_appointment_by_id,
    get_appointments,
    get_appointments_count,
    get_appointment_id_for_name_and_date_time,
]
