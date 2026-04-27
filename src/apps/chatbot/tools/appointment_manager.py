"""
Appointment management tool for the ChatBot.

This tool manages patient appointments with the following constraints:
- Only one patient at a time
- One-hour appointment slots
- Work week only (Monday-Friday)
- Excludes common USA holidays
- Appointments must be on the hour (e.g., 10:00, 11:00, not 10:30)
"""

# Allow types to self-reference during their definitions.
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Callable, Optional, Tuple
from uuid import uuid4

from common.utils import (
    decode_json,
    encode_json,
    DatetimeDecoder,
    DatetimeEncoder,
)
from common.file_persistent_storage import FilePersistentStorage

from .resource_manager import ResourceManager

class AppointmentManagerEncoder(json.JSONEncoder):
    """Handles `datetime`s and `FilePersistentStorage` attributes."""
    def default(self, o: Any) -> Any:
        """
        The name of the derived type of `ResourceManager` is used
        by calling `type(self).__name__`.
        """
        if isinstance(o, AppointmentManager):
            d = {}
            d['__class__'] = type(self).__name__
            d['storage_path'] = o.storage.storage_path
            return d
        return super().default(o)

class AppointmentManagerDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook = AppointmentManagerDecoder.from_dict)

    @classmethod
    def from_dict(cls, d: dict[str,Any]) -> Any:
        """
        Create an instance from JSON. There is an ambiguity with what to do with resources
        that are already in the storage file and those encoded in the JSON. If the list of
        resources in the JSON is _not_ empty, we use that list of resources and replace
        any file contents with them. See `AppointmentManager.make()` for details.
        """
        if d.get('__class__') == cls.__name__:
            storage_path = d.get('storage_path', '')
            return AppointmentManager(storage_path)
        else:
            return d

class AppointmentManager(ResourceManager):
    """
    A simple tool for managing patient appointments using a simple calendar
    with local file storage.
    
    Appointments are stored in a JSONL file where each line is a JSON object
    representing an appointment. The method return values are designed to work
    with LLMs in an agent context.
    """
    
    # Common USA holidays (simplified list)
    USA_HOLIDAYS = set([
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas
        # Add more as needed
    ])

    def_json_encoder = AppointmentManagerEncoder()
    def_json_decoder = AppointmentManagerDecoder()
    
    def __init__(self,
        appointments_file: Path | str,
        start_empty: bool = False,
        logger: Optional[logging.Logger] = None):
        """
        Initialize the appointment tool.
        
        Args:
            - appointments_file (Path | str): Path to the JSONL file storing appointments
            - start_empty (bool): `True` if we should clear the file and start "empty"
              or False if we should just load whatever appointments the file contains already.
            - logger (logging.Logger): Optional logger instance
        """
        super().__init__(appointments_file, start_empty, logger)
        # Create an alias for "self.resources" that is more appropriate
        # for appointments...
        self.appointments = self.resources

    def _ignore(self, resource: dict[str,Any]) -> bool:
        """
        Implement this hook to ignore appointment records for 
        "cancelled" appointments.
        """
        return resource.get('status') == 'cancelled'

    @classmethod
    def make_appointment_dict(cls,
        appointment_date_time: datetime,
        patient_name: str | list[str],
        reason: str,
        status: str = 'scheduled') -> dict[str,Any]:
        """
        Make a "raw" dictionary for an appointment, without checking
        values, etc. This is a service method used by create_appointment(),
        and some tests.
        """
        if isinstance(patient_name, list):
            pname = ' '.join(patient_name)
        else:
            pname = patient_name
        return {
            'patient_name': pname,
            'appointment_date_time': appointment_date_time,
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
    
    def _further_date_time_validation(self, a_date_time: datetime) -> tuple[bool,str]:
        """
        For appointments, we have additional requirements compared to the
        requirements defined in `ResourceManager._is_valid_date_time()`:
        1. Only weekday and non-holiday date-times are allowed.
        2. Only on-the-hour date-times between 8AM, inclusive, and 5PM, exclusive, are allowed.

        Args:
            - a_date_time (datetime): A datetime to validate
            
        Returns:
            A tuple with `(True, '')` on success or `(False, error_message)` on failure.
        """        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if a_date_time.weekday() >= 5:
            return False, "Allowed date-times can only be scheduled on weekdays (Monday-Friday)."
        
        # Check if it's a holiday
        if (a_date_time.month, a_date_time.day) in self.USA_HOLIDAYS:
            return False, "Allowed date-times cannot be scheduled on holidays."

        # Check if it's between 8AM, inclusive, and 5PM, exclusive
        if a_date_time.hour < 8 or a_date_time.hour >= 17:
            return False, "Allowed date-times must be scheduled between 8 AM, inclusive, and 5 PM, exclusive (8:00-17:00)."

        # Check if it's on the hour
        if a_date_time.minute != 0 or a_date_time.second != 0 or a_date_time.microsecond != 0:
            return False, "Allowed date-times must be scheduled on the hour (e.g., 10:00, 11:00)."
                
        return True, ""
    
    def _is_valid_resource(self, fields: dict[str,Any]) -> tuple[bool,str]:
        """
        For appointment "resources", the appointment date-time must be valid
        and the patient name must be non-empty.

        Args:
            - fields (dict[str,Any]): The dictionary to use to create the resource record.
            
        Returns:
            A tuple with `(True, '')` on success or `(False, error_message)` on failure.
        """
        # Validate the date-time
        is_valid_dt = True
        dt_error_msg = ''
        dt = fields.get('appointment_date_time')
        if not dt:
            is_valid_dt = False
            dt_error_msg = f"No field 'appointment_date_time' found."
        else:
            is_valid_dt, dt_error_msg = self._is_valid_date_time(
                dt,
                in_the_past_allowed = False,
                unique_datetime_key = 'appointment_date_time')

        is_valid_pn = True
        pn_error_msg = ''
        pn = fields.get('patient_name')
        if pn == None:
            is_valid_pn = False
            pn_error_msg = f"No field 'patient_name' found."
        elif pn.strip() == '':
            is_valid_pn = False
            pn_error_msg = f"'patient_name' field can't be empty."

        if not is_valid_dt or not is_valid_pn:
            return False, f"{dt_error_msg} {pn_error_msg} Input fields: {fields}."
        else:
            return True, ''

    def create_appointment(
        self,
        patient_name: str,
        appointment_date_time: datetime,
        reason: str
    ) -> Tuple[str, str]:
        """
        Create a new appointment.
        
        Args:
            - patient_name (str): Name of the patient
            - appointment_date_time (datetime): Desired appointment time
            - reason (str): Reason for the appointment
            
        Returns:
            Non-empty string with the id of the successfully-created appointment or '' and a failure message with reasons for the failure.
        """        
        # Create the appointment
        appointment = AppointmentManager.make_appointment_dict(
            appointment_date_time = appointment_date_time,
            patient_name = patient_name,
            reason = reason,
            status = 'scheduled')
        return self._create_resource(appointment)
        
    def set_appointments(
        self,
        appointments: list[dict[str,Any]]
    ) -> Tuple[int, str]:
        """
        Set the appointments, replacing the current list. Normally, create_appointment() should be used.
        This method is primarily for "deserializing" from storage, like JSON.
        
        Args:
            - appointments (list[dict[str,Any]]): list of appointments to set. They will be validated for unique keys and date times
              (with past date times allowed). Each dictionary must have an `id` key-value pair and the values 
              must be unique.
            
        Returns:
            When successful, returns the count of appointments set, which will equal `len(appointments)`, 
            and an empty message string, but if not successful, returns 0 and a non-empty error message string.
        """
        # This method is just an alias for `set_resources()`.
        return self.set_resources(appointments)
        
    def cancel_appointment(self, appointment_id: str) -> Tuple[bool, str]:
        """
        Cancel an existing appointment.
        
        Args:
            appointment_id: ID of the appointment to cancel
            
        Returns:
            True with success message or False with a failure message with reasons for the failure.
        """
        if appointment_id not in self.appointments:
            error_msg = f"There is no appointment with ID {appointment_id}."
            self.logger.error(error_msg)
            return False, error_msg
        
        appointment = self.appointments[appointment_id]
        appointment['status'] = 'cancelled'
        appointment['cancelled_at'] = datetime.now()
        
        # Save the updated status
        self._save_resources([appointment])
        
        # Remove from active appointments
        del self.appointments[appointment_id]
        
        success_msg = f"Appointment {appointment_id} is now cancelled."
        self.logger.info(success_msg)
        return True, success_msg

    def change_appointment(
        self,
        appointment_id: str,
        new_date_time: datetime
    ) -> Tuple[bool, str]:
        """
        Change an appointment to a new time.
        
        Args:
            appointment_id: ID of the appointment to change
            new_date_time: New appointment time
            
        Returns:
            True with a success message or False a failure message with reasons for the failure.
        """
        if appointment_id not in self.appointments:
            error_msg = f"No appointment with ID {appointment_id} was found."
            self.logger.error(error_msg)
            return False, error_msg
        
        # Validate the new time
        is_valid, error_msg = self._is_valid_date_time(
            new_date_time,
            in_the_past_allowed = False,
            unique_datetime_key = 'appointment_date_time')
        if not is_valid:
            error_msg = f"I could not change the appointment {appointment_id}. {error_msg}"
            self.logger.error(error_msg)
            return False, error_msg
        
        appointment = self.appointments[appointment_id]
        old_time = appointment['appointment_date_time']
        appointment['appointment_date_time'] = new_date_time
        appointment['changed_at'] = datetime.now()
        appointment['previous_time'] = old_time
        
        # Save the updated appointment
        self._save_resources([appointment])
        
        self.logger.info(f"I changed appointment {appointment_id} from {old_time.isoformat()} to {new_date_time.isoformat()}.")
        return True, f"I changed appointment {appointment_id} from {old_time} to {new_date_time}."
    
    def get_appointments_by_criteria(self, criteria: dict[str,Callable[[Any],bool]]) -> list[dict[str,Any]]:
        """An alias for `get_resources_by_criteria()`.""" 
        return self.get_resources_by_criteria(criteria)

    def get_appointment_ids_by_criteria(self, criteria: dict[str,Any]) -> list[str]:
        """An alias for `get_resource_ids_by_criteria()`.""" 
        return self.get_resource_ids_by_criteria(criteria)

    def get_appointments(
        self,
        patient_name: str = '',
        after_date_time: datetime = datetime.min,
    ) -> list[dict[str, Any]]:
        """
        Get all appointments, possibly filtered by patient name and/or
        after a specified date-time.
        
        Args:
            - patient_name (str): Only return appointments for this patient (default: all patients)
            - after_date_time (datetime): Don't include appointments before this date time. Pass `datetime.now()` to only return future appointments.
            
        Returns:
            List of appointment dictionaries
        """
        criteria = {}
        if patient_name:
            criteria['patient_name'] = lambda pn: pn == patient_name
        if after_date_time:
            criteria['appointment_date_time'] = lambda dt: dt >= after_date_time
        
        return self.get_resources_by_criteria(criteria, sort_by_key = 'appointment_date_time')

    def get_appointments_count(self) -> int:
        """Return the number of appointments currently scheduled."""
        return self.get_resources_count()

    def get_appointment_by_id(self, appointment_id: str) -> dict[str, Any]:
        """An alias for `get_resource_by_id()`.""" 
        return self.get_resource_by_id(appointment_id)

    def get_appointment_id_for_name_and_date_time(self, 
        patient_name: str,
        appointment_date_time: datetime) -> str:
        """
        Retrieve the appointment ID for the specified patient and date time.
        There are restrictions on the arguments, as the assumption is that 
        this function is called with the expectation that an appointment
        really exists for this patient at this date-time. A `ValueError` is
        raised if more than one matching appointment is found, since patient's
        can't logically have more than one appointment at the same time!
        
        Args:
            - patient_name (str): Name of the patient. Can't be empty. 
              Otherwise a `ValueError` is raised.
            - appointment_date_time (datetime): Date time of the appointment.
              It must pass `_is_valid_date_time()`. Otherwise a `ValueError` 
              is raised. To handle rare rounding errors in datetime values, we
              compare them within one second.
            
        Returns:
            ID of the appointment or '' if there is no appointment for that patient at that date time.
        """
        errors = []
        if not patient_name:
            errors.append("The patient_name argument can't be empty!")
        if not self._is_valid_date_time(appointment_date_time):
            errors.append(f"The appointment_date_time argument '{appointment_date_time}' is invalid!")
        if errors:
            raise ValueError(' '.join(errors))

        criteria = {}
        if patient_name:
            criteria['patient_name'] = lambda pn: pn == patient_name
        if appointment_date_time:
            # Check within one second:
            one_second = timedelta(seconds = 1)
            dt_eq = lambda dt: dt >= appointment_date_time - one_second and dt <= appointment_date_time + one_second
            criteria['appointment_date_time'] = dt_eq
        
        found = self.get_resource_ids_by_criteria(criteria)
        match len(found):
            case 0:
                return ''
            case 1:
                return found[0]
            case n:
                raise ValueError(f"Logic error. {n} > 1 appointments found for {patient_name} at {appointment_date_time}. Should be 0 or 1. appointments = {self.appointments}")

    def __str__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        """Create a JSON string from the object."""
        return AppointmentManager.def_json_encoder.encode(self)

    def from_json(text: Any) -> AppointmentManager:
        """Attempt to parse a JSON object, returning an instance."""
        return AppointmentManager.def_json_decoder.decode(text)

