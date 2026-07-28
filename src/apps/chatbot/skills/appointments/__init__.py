"""
Appointment management skill for the ChatBot.
"""

from .appointment_tools import (
    APPOINTMENT_TOOLS,
    cancel_appointment,
    change_appointment,
    create_appointment,
    get_appointment_by_id,
    get_appointment_id_for_name_and_date_time,
    get_appointment_manager,
    get_appointments,
    get_appointments_count,
)

__all__ = [
    "APPOINTMENT_TOOLS",
    "cancel_appointment",
    "change_appointment",
    "create_appointment",
    "get_appointment_by_id",
    "get_appointment_id_for_name_and_date_time",
    "get_appointment_manager",
    "get_appointments",
    "get_appointments_count",
]
