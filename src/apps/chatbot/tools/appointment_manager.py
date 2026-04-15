"""
Appointment management tool for the ChatBot.

This tool manages patient appointments with the following constraints:
- Only one patient at a time
- One-hour appointment slots
- Work week only (Monday-Friday)
- Excludes common USA holidays
- Appointments must be on the hour (e.g., 10:00, 11:00, not 10:30)
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from common.utils import decode_json, encode_json

class AppointmentError(Exception):
    """Custom exception for appointment-related errors"""
    pass


class AppointmentManager:
    """
    Tool for managing patient appointments.
    
    Stores appointments in a JSONL file where each line is a JSON object
    representing an appointment.
    """
    
    # Common USA holidays (simplified list)
    USA_HOLIDAYS = set([
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas
        # Add more as needed
    ])
    
    def __init__(self,
        appointments_file: Path | str,
        logger: Optional[logging.Logger] = None):
        """
        Initialize the appointment tool.
        
        Args:
            appointments_file: Path to the JSONL file storing appointments
            logger: Optional logger instance
        """
        self.appointments_file = Path(appointments_file)
        if logger:
            self.logger: logging.Logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.INFO)

        self.appointments: dict[str, dict[str, Any]] = {}
        
        # Create file if it doesn't exist
        self.__create_file(self.appointments_file)
        
        # Load existing appointments
        self._load_appointments()
    
    def __create_file(self, path: Path, remove_old: bool = False):
        """
        Create the records file. If it already exists and remove_old is False,
        then nothing is done.
        """
        if remove_old:
            self.appointments_file.unlink(missing_ok=True)
        if not self.appointments_file.exists():
            self.appointments_file.parent.mkdir(parents=True, exist_ok=True)
            self.appointments_file.touch()

    @classmethod
    def make_appointment_dict(cls,
        appointment_time: datetime,
        patient_name: str,
        reason: str,
        status: str = 'scheduled',
        appointment_id = str(uuid4())) -> dict[str,Any]:
        """
        Make a "raw" dictionary for an appointment, without checking
        values, etc. This is a service method used by create_appointment(),
        and some tests.
        """
        return {
            'appointment_id': appointment_id,
            'patient_name': patient_name,
            'appointment_time': appointment_time,
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

    def clear(self):
        """Remove all appointments and clear the persistent records."""
        self.appointments.clear()
        self.__create_file(self.appointments_file, remove_old = True)

    def _load_appointments(self) -> None:
        """Load appointments from the JSONL file. The timestamps are parsed with datetime.fromisoformat()"""
        self.appointments = {}
        if self.appointments_file.exists():
            with open(self.appointments_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            appointment = decode_json(line)
                            # Only load non-cancelled appointments
                            if appointment.get('status') != 'cancelled':
                                id = appointment.get('appointment_id')
                                if id:
                                    dt = appointment['appointment_time']
                                    if isinstance(dt, str):
                                        appointment['appointment_time'] = datetime.fromisoformat(dt)
                                    self.appointments[appointment['appointment_id']] = appointment
                                else:
                                    self.logger.error(f"appointment doesn't have an id! appointment = {appointment}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Error parsing appointment line: {e} (line: {line})")
    
    def _save_appointment(self, appointment: dict[str, Any]) -> None:
        """
        Append an appointment to the JSONL file.
        
        Args:
            appointment: The appointment dictionary to save
        """
        with open(self.appointments_file, 'a') as f:
            f.write(encode_json(appointment) + '\n')
    
    def _is_valid_time(self, appointment_time: datetime, in_the_past_allowed: bool = False) -> tuple[bool, str]:
        """
        Check if the appointment time is valid.
        
        Args:
            appointment_time: The proposed appointment time
            in_the_past_allowed: If False (default), a time is invalid if it is in the past. 
            To facilitate some scenarios around "now", like tests, we actually require the
            time to be within one second of now. If the argument is True, then past datetimes 
            are allowed without constraints.
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        one_second = timedelta(seconds=1)
        min_allowed_datetime = datetime.now() - one_second 
        if not in_the_past_allowed and appointment_time < min_allowed_datetime:
            return False, "Appointment time is in the past, which is not allowed."

        # Check if it's on the hour
        if appointment_time.minute != 0 or appointment_time.second != 0:
            return False, "Appointments must be scheduled on the hour (e.g., 10:00, 11:00)"
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if appointment_time.weekday() >= 5:
            return False, "Appointments can only be scheduled on weekdays (Monday-Friday)"
        
        # Check if it's a holiday
        if (appointment_time.month, appointment_time.day) in self.USA_HOLIDAYS:
            return False, "Appointments cannot be scheduled on holidays"
        
        # Check if the time slot is already booked. We do check if any
        # occupied times are within 1 second of the proposed time.
        for appt in self.appointments.values():
            dt = appt.get('appointment_time')
            dtm1 = dt - one_second 
            dtp1 = dt + one_second
            if appt.get('status') != 'cancelled' and dtm1 < appointment_time and dtp1 > appointment_time:
                return False, "This time slot is already booked"
        
        return True, ""
    
    def create_appointment(
        self,
        patient_name: str,
        appointment_time: datetime,
        reason: str
    ) -> dict[str, Any]:
        """
        Create a new appointment.
        
        Args:
            patient_name: Name of the patient
            appointment_time: Desired appointment time
            reason: Reason for the appointment
            
        Returns:
            Dictionary with appointment details
            
        Raises:
            AppointmentError: If the appointment cannot be created, e.g., 
            because the `datetime` is not valid.
        """
        # Validate the time
        is_valid, error_msg = self._is_valid_time(appointment_time)
        if not is_valid:
            raise AppointmentError(error_msg)
        
        # Create the appointment
        appointment_id = str(uuid4())
        appointment = AppointmentManager.make_appointment_dict(
            appointment_time = appointment_time,
            patient_name = patient_name,
            reason = reason,
            status = 'scheduled',
            appointment_id = appointment_id)
        
        # Save to memory and file
        self.appointments[appointment_id] = appointment
        self._save_appointment(appointment)
        
        self.logger.info(f"Created appointment {appointment_id} for {patient_name}")
        
        success = appointment.copy()
        success['success'] = True
        return success
    
    def cancel_appointment(self, appointment_id: str) -> dict[str, Any]:
        """
        Cancel an existing appointment.
        
        Args:
            appointment_id: ID of the appointment to cancel
            
        Returns:
            Dictionary with cancellation details
            
        Raises:
            AppointmentError: If the appointment doesn't exist
        """
        if appointment_id not in self.appointments:
            raise AppointmentError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment['status'] = 'cancelled'
        appointment['cancelled_at'] = datetime.now()
        
        # Save the updated status
        self._save_appointment(appointment)
        
        # Remove from active appointments
        del self.appointments[appointment_id]
        
        self.logger.info(f"Cancelled appointment {appointment_id}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'status': 'cancelled'
        }
    
    def confirm_appointment(self, criteria: dict[str,Any]) -> list[dict[str, Any]]:
        """
        Confirm an existing appointment.
        
        Args:
            criteria: a dictionary containing one or more of the id, timestamp, or patient name, which will be used for matching.
            
        Returns:
            A list of dictionaries with zero or more appointment details that match the criteria.
            If the criteria is empty, then _all_ appointments are returned!
            Any returned dictionaries have key-values `status` set to 'confirmed'
            and `confirmed_at` set to `datetime.now()`.
        """
        if not criteria:
            return self.appointments

        def check(appointment: dict[str,Any]) -> bool:
            for key, value in criteria.items():
                if not value == appointment.get(key):
                    return False
            return True

        found = []
        for appointment in self.appointments.values():
            if check(appointment):
                appointment['status'] = 'confirmed'
                appointment['confirmed_at'] = datetime.now()
                # Save the updated status
                self._save_appointment(appointment)
                found.append(appointment)        
        
        self.logger.info(f"Confirmed appointments for criteria {criteria}: {found}")

        return found
    
    def change_appointment(
        self,
        appointment_id: str,
        new_time: datetime
    ) -> dict[str, Any]:
        """
        Change an appointment to a new time.
        
        Args:
            appointment_id: ID of the appointment to change
            new_time: New appointment time
            
        Returns:
            Dictionary with change details.
            
        Raises:
            AppointmentError: If the appointment doesn't exist or new time is invalid
            or collides with an existing appointment at the same time.
        """
        if appointment_id not in self.appointments:
            raise AppointmentError(f"Appointment {appointment_id} not found")
        
        # Validate the new time
        is_valid, error_msg = self._is_valid_time(new_time)
        if not is_valid:
            raise AppointmentError(error_msg)
        
        appointment = self.appointments[appointment_id]
        old_time = appointment['appointment_time']
        appointment['appointment_time'] = new_time
        appointment['changed_at'] = datetime.now()
        appointment['previous_time'] = old_time
        
        # Save the updated appointment
        self._save_appointment(appointment)
        
        self.logger.info(f"Changed appointment {appointment_id} from {old_time.isoformat()} to {new_time.isoformat()}")
        
        d = appointment.copy()
        d['success'] = True
        return d
    
    def list_appointments(
        self,
        after_datetime: datetime = datetime.min,
        status_filter: str = ''
    ) -> list[dict[str, Any]]:
        """
        List all appointments.
        
        Args:
            after_datetime: Don't include appointments before this value. Pass datetime.now() to only return future appointments.
            status_filter: Optional status to filter by (e.g., 'scheduled', 'confirmed')
            
        Returns:
            List of appointment dictionaries
        """
        now = datetime.now()
        appointments = []
        
        for appointment in self.appointments.values():
            # Filter by status if specified
            if status_filter and appointment.get('status') != status_filter:
                continue
            
            # Only include appointments before `after_datetime`.
            if appointment['appointment_time'] >= after_datetime:
                appointments.append(appointment.copy())
        
        # Sort by appointment time
        appointments.sort(key=lambda x: x['appointment_time'])
        
        return appointments

    def get_appointments_count(self) -> int:
        """Return the number of appointments currently scheduled."""
        return len(self.appointments)

    def get_appointment(self, appointment_id: str) -> dict[str, Any]:
        """
        Get a specific appointment by ID.
        
        Args:
            appointment_id: ID of the appointment
            
        Returns:
            Appointment dictionary or None if not found
        """
        return self.appointments.get(appointment_id, {})


# Made with Bob