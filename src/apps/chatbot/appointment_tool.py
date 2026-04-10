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


class AppointmentError(Exception):
    """Custom exception for appointment-related errors"""
    pass


class AppointmentTool:
    """
    Tool for managing patient appointments.
    
    Stores appointments in a JSONL file where each line is a JSON object
    representing an appointment.
    """
    
    # Common USA holidays (simplified list)
    USA_HOLIDAYS = [
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas
        # Add more as needed
    ]
    
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
        if not self.appointments_file.exists():
            self.appointments_file.parent.mkdir(parents=True, exist_ok=True)
            self.appointments_file.touch()
        
        # Load existing appointments
        self._load_appointments()
    
    def _load_appointments(self) -> None:
        """Load appointments from the JSONL file"""
        self.appointments = {}
        if self.appointments_file.exists():
            with open(self.appointments_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            appointment = json.loads(line)
                            # Only load non-cancelled appointments
                            if appointment.get('status') != 'cancelled':
                                id = appointment.get('appointment_id')
                                if id:
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
            f.write(json.dumps(appointment) + '\n')
    
    def _is_valid_time(self, appointment_time: datetime) -> tuple[bool, str]:
        """
        Check if the appointment time is valid.
        
        Args:
            appointment_time: The proposed appointment time
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's on the hour
        if appointment_time.minute != 0 or appointment_time.second != 0:
            return False, "Appointments must be scheduled on the hour (e.g., 10:00, 11:00)"
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if appointment_time.weekday() >= 5:
            return False, "Appointments can only be scheduled on weekdays (Monday-Friday)"
        
        # Check if it's a holiday
        if (appointment_time.month, appointment_time.day) in self.USA_HOLIDAYS:
            return False, "Appointments cannot be scheduled on holidays"
        
        # Check if the time slot is already booked
        time_str = appointment_time.isoformat()
        for appt in self.appointments.values():
            if appt.get('appointment_time') == time_str and appt.get('status') != 'cancelled':
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
            AppointmentError: If the appointment cannot be created
        """
        # Validate the time
        is_valid, error_msg = self._is_valid_time(appointment_time)
        if not is_valid:
            raise AppointmentError(error_msg)
        
        # Create the appointment
        appointment_id = str(uuid4())
        appointment = {
            'appointment_id': appointment_id,
            'patient_name': patient_name,
            'appointment_time': appointment_time.isoformat(),
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        # Save to memory and file
        self.appointments[appointment_id] = appointment
        self._save_appointment(appointment)
        
        self.logger.info(f"Created appointment {appointment_id} for {patient_name}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'patient_name': patient_name,
            'appointment_time': appointment_time.isoformat(),
            'reason': reason,
            'status': 'scheduled'
        }
    
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
        appointment['cancelled_at'] = datetime.now().isoformat()
        
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
    
    def confirm_appointment(self, appointment_id: str) -> dict[str, Any]:
        """
        Confirm an existing appointment.
        
        Args:
            appointment_id: ID of the appointment to confirm
            
        Returns:
            Dictionary with confirmation details
            
        Raises:
            AppointmentError: If the appointment doesn't exist
        """
        if appointment_id not in self.appointments:
            raise AppointmentError(f"Appointment {appointment_id} not found")
        
        appointment = self.appointments[appointment_id]
        appointment['status'] = 'confirmed'
        appointment['confirmed_at'] = datetime.now().isoformat()
        
        # Save the updated status
        self._save_appointment(appointment)
        
        self.logger.info(f"Confirmed appointment {appointment_id}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'status': 'confirmed'
        }
    
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
            Dictionary with change details
            
        Raises:
            AppointmentError: If the appointment doesn't exist or new time is invalid
        """
        if appointment_id not in self.appointments:
            raise AppointmentError(f"Appointment {appointment_id} not found")
        
        # Validate the new time
        is_valid, error_msg = self._is_valid_time(new_time)
        if not is_valid:
            raise AppointmentError(error_msg)
        
        appointment = self.appointments[appointment_id]
        old_time = appointment['appointment_time']
        appointment['appointment_time'] = new_time.isoformat()
        appointment['changed_at'] = datetime.now().isoformat()
        appointment['previous_time'] = old_time
        
        # Save the updated appointment
        self._save_appointment(appointment)
        
        self.logger.info(f"Changed appointment {appointment_id} from {old_time} to {new_time.isoformat()}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'old_time': old_time,
            'new_time': new_time.isoformat()
        }
    
    def list_appointments(
        self,
        include_past: bool = False,
        status_filter: str = ''
    ) -> list[dict[str, Any]]:
        """
        List all appointments.
        
        Args:
            include_past: Whether to include past appointments
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
            
            # Filter past appointments if requested
            if not include_past:
                appt_time = datetime.fromisoformat(appointment['appointment_time'])
                if appt_time < now:
                    continue
            
            appointments.append(appointment.copy())
        
        # Sort by appointment time
        appointments.sort(key=lambda x: x['appointment_time'])
        
        return appointments
    
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