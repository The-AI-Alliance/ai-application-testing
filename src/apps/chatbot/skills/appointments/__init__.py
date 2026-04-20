"""
Appointment management skill for the ChatBot.
"""

from .appointment_tools import (
    APPOINTMENT_TOOLS,
    get_appointment_manager,
    create_appointment,
    cancel_appointment,
    confirm_appointment,
    change_appointment,
    list_appointments,
    set_appointments_file,
)

__all__ = [
    'APPOINTMENT_TOOLS',
    'get_appointment_manager',
    'create_appointment',
    'cancel_appointment',
    'confirm_appointment',
    'change_appointment',
    'list_appointments',
    'set_appointments_file',
]

# Made with Bob
