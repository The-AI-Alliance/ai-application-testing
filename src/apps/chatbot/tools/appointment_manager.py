"""
Appointment management tool for the ChatBot.

This tool manages patient appointments with the following constraints:
- Only one patient at a time
- One-hour appointment slots
- Work week only (Monday-Friday)
- Excludes common USA holidays
- Appointments must be on the hour (e.g., 10:00, 11:00, not 10:30)
"""

from __future__ import annotations 
import json
import logging
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Tuple
from uuid import uuid4

from common.utils import (
    decode_json,
    encode_json,
    DatetimeDecoder,
    DatetimeEncoder,
)
from common.file_persistent_storage import (
    FilePersistentStorage,
    FilePersistentStorageDecoder,
    FilePersistentStorageEncoder,
)

class AppointmentManagerEncoder(DatetimeEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, AppointmentManager):
            d = o.__dict__.copy()
            d["__class__"] = "AppointmentManager"
            d["storage"] = FilePersistentStorage.def_json_encoder.default(o.storage)
            del d["logger"]
            return d
        return super().default(o)

class AppointmentManagerDecoder(DatetimeDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=AppointmentManagerDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        """
        Create an instance from JSON. There is an ambiguity with what to do with appointments
        that are already in the storage file and those encoded in the JSON. If the list of
        appointments in the JSON is _not_ empty, we use that list of appointments and replace
        any file contents with them.
        """
        if d.get("__class__") == "AppointmentManager":
            storage = FilePersistentStorage.def_json_decoder.from_dict(d.get("storage"))
            appointments = d.get("appointments")
            for key, value in appointments.items():
                # hack to fix up the date times.
                for k, v in value.items():
                    if isinstance(v, dict) and v.get("__class__") == "datetime":
                        dt = datetime.fromisoformat(v.get("iso_str"))
                        value[k] = dt
            start_empty = True if appointments else False
            am = AppointmentManager(appointments_file = storage.storage_path, start_empty = start_empty)
            if appointments:
                am.set_appointments(appointments.values())
            return am
        else:
            return d

class AppointmentManager:
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

    def encode_json(dct: dict[str,Any]) -> str:
        """Create a JSON string from the input object."""
        return AppointmentManager.def_json_encoder.encode(dct)

    def decode_json(text: Any) -> dict[str,Any]:
        """Parse a JSON string, returning a dictionary."""
        return AppointmentManager.def_json_decoder.decode(text)

    
    def __init__(self,
        appointments_file: Path | str,
        start_empty: bool = False,
        logger: Optional[logging.Logger] = None):
        """
        Initialize the appointment tool.
        
        Args:
            appointments_file: Path to the JSONL file storing appointments
            start_empty: True if we should clear the file and start "empty" or False if we should just load whatever appointments the file contains already.
            logger: Optional logger instance
        """
        if logger:
            self.logger: logging.Logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.INFO)

        self.storage = FilePersistentStorage(Path(appointments_file), logger)
        self.appointments: dict[str, dict[str, Any]] = {}
        if start_empty:
            self.storage.clear()
        else:
            self._load_appointments()


    @classmethod
    def make_appointment_dict(cls,
        appointment_date_time: datetime,
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
            'appointment_date_time': appointment_date_time,
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

    def clear(self):
        """Remove all appointments and clear the persistent records."""
        self.appointments.clear()
        self.storage.clear()

    def _load_appointments(self) -> None:
        """Load appointments from the JSONL file. The timestamps are parsed with datetime.fromisoformat()"""
        self.appointments = {}
        appts, errors = self.storage.load()
        if errors:
            self.logger.error(f"{len(errors)} records out of {len(appts)+len(errors)} failed to parse: {errors}")

        for appointment in appts:
            # Only load non-cancelled appointments and those with ids.
            if appointment.get('status') != 'cancelled':
                id = appointment.get('appointment_id')
                if id:
                    dt = appointment['appointment_date_time']
                    if isinstance(dt, str): # Shouldn't actually happen!!
                        appointment['appointment_date_time'] = datetime.fromisoformat(dt)
                    self.appointments[id] = appointment
                else:
                    self.logger.error(f"appointment doesn't have an id! appointment = {appointment}.")
    
    def _save_appointments(self, appointments: list[dict[str, Any]]) -> int:
        """
        Append one or more appointments to the JSONL file.
        
        Args:
            appointments: The list of appointment dictionaries to save.
        """
        count = self.storage.save(appointments)
        lena = len(appointments)
        if count != lena:
            diff = lena - count
            self.logger.error(f"Failed to save {diff} out of {lena} appointments to the storage file {self.storage.storage_path}. appointments = {appointments}")
        return count

    def _is_valid_time(self, appointment_date_time: datetime, in_the_past_allowed: bool = False) -> tuple[bool, str]:
        """
        Check if the appointment time is valid.
        
        Args:
            appointment_date_time: The proposed appointment time
            in_the_past_allowed: If False (default), a time is invalid if it is in the past. 
            To facilitate some scenarios around "now", like tests, we actually require the
            time to be within one second of now. If the argument is True, then past datetimes 
            are allowed without constraints.
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        one_second = timedelta(seconds=1)
        min_allowed_datetime = datetime.now() - one_second 
        if not in_the_past_allowed and appointment_date_time < min_allowed_datetime:
            return False, "Appointment time is in the past, which is not allowed."
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if appointment_date_time.weekday() >= 5:
            return False, "Appointments can only be scheduled on weekdays (Monday-Friday)."
        
        # Check if it's a holiday
        if (appointment_date_time.month, appointment_date_time.day) in self.USA_HOLIDAYS:
            return False, "Appointments cannot be scheduled on holidays."

        # Check if it's between 8AM, inclusive, and 5PM, exclusive
        if appointment_date_time.hour < 8 or appointment_date_time.hour >= 17:
            return False, "Appointments must be scheduled between 8 AM, inclusive, and 5 PM, exclusive (8:00-17:00)."

        # Check if it's on the hour
        if appointment_date_time.minute != 0 or appointment_date_time.second != 0 or appointment_date_time.microsecond != 0:
            return False, "Appointments must be scheduled on the hour (e.g., 10:00, 11:00)."
        
        # Check if the time slot is already booked. We do check if any
        # occupied times are within 1 second of the proposed time.
        for appt in self.appointments.values():
            dt = appt.get('appointment_date_time')
            if not dt:
                self.logger.error(f"_is_valid_time(): Appointment found without a datetime! {appt}")
            else:
                dtm1 = dt - one_second 
                dtp1 = dt + one_second
                if appt.get('status') != 'cancelled' and dtm1 < appointment_date_time and dtp1 > appointment_date_time:
                    return False, f"The time slot {appointment_date_time} is already booked."
        
        return True, ""
    
    def create_appointment(
        self,
        patient_name: str,
        appointment_date_time: datetime,
        reason: str
    ) -> Tuple[str, str]:
        """
        Create a new appointment.
        
        Args:
            patient_name: Name of the patient
            appointment_date_time: Desired appointment time
            reason: Reason for the appointment
            
        Returns:
            Non-empty string with the id of the successfully-created appointment or '' and a failure message with reasons for the failure.
        """
        # Validate the time
        is_valid, error_msg = self._is_valid_time(appointment_date_time)
        if not is_valid:
            error_msg = f"I could not create an appointment for {patient_name} at {appointment_date_time}. {error_msg}"
            self.logger.error(error_msg)
            return '', error_msg
        
        # Create the appointment
        appointment_id = str(uuid4())
        appointment = AppointmentManager.make_appointment_dict(
            appointment_date_time = appointment_date_time,
            patient_name = patient_name,
            reason = reason,
            status = 'scheduled',
            appointment_id = appointment_id)
        
        # Save to memory and file
        self.appointments[appointment_id] = appointment
        self._save_appointments([appointment])
        success_msg = f"I successfully created an appointment for {patient_name} at {appointment_date_time}. The appointment ID is {appointment_id}."
        self.logger.info(success_msg)
        return appointment_id, success_msg
        
    def set_appointments(
        self,
        appointments: list[dict[str,Any]]
    ) -> Tuple[int, str]:
        """
        Set the appointments, replacing the current list. Normally, create_appointment() should be used.
        This method is primarily for "deserializing" from storage, like JSON.
        
        Args:
            appointments: list of appointments to set. They will be validated for unique keys and date times
            (with past date times allowed).
            
        Returns:
            When successful, returns the count of appointments set, which will equal `len(appointments)`, 
            and an empty message string, but if not successful, returns 0 and a non-empty error message string.
        """
        self.clear()
        # Unique ids?
        ids = [a['appointment_id'] for a in appointments]
        unique = set(ids)
        if len(unique) != len(ids):
            return 0, f"{len(ids) - len(unique)} out of {len(ids)} ids are not unique! {ids}"

        # Validate the times
        dt_errors = []
        for appt in appointments:
            dt = appt['appointment_date_time']
            is_valid, error_msg = self._is_valid_time(dt, in_the_past_allowed=True)
            if not is_valid:
                dt_errors.append(f"{dt}: {error_msg}")
        if dt_errors:
            error_msg = f"{len(dt_errors)} invalid date times: [{", ".join(dt_errors)}]"
            self.logger.error(error_msg)
            return 0, error_msg
        
        # All good at this point!
        # Save to memory and file
        self.appointments = dict([(a['appointment_id'], a) for a in appointments])
        self._save_appointments(appointments)
        self.logger.info(f"Appointments replaced with {len(self.appointments)} new appointments.")
        return len(self.appointments), ''
        
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
        self._save_appointments([appointment])
        
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
        is_valid, error_msg = self._is_valid_time(new_date_time)
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
        self._save_appointments([appointment])
        
        self.logger.info(f"I changed appointment {appointment_id} from {old_time.isoformat()} to {new_date_time.isoformat()}.")
        return True, f"I changed appointment {appointment_id} from {old_time} to {new_date_time}."
    
    def list_appointments(
        self,
        patient_name: str = '',
        after_date_time: datetime = datetime.min,
    ) -> list[dict[str, Any]]:
        """
        List all appointments.
        
        Args:
            patient_name: Only return appointments for this patient (default: all patients)
            after_date_time: Don't include appointments before this date time. Pass `datetime.now()` to only return future appointments.
            
        Returns:
            List of appointment dictionaries
        """
        now = datetime.now()
        appointments = []
        
        for appointment in self.appointments.values():
            # Filter by patient name, if specified
            if patient_name and appointment.get('patient_name') != patient_name:
                continue
            
            # Only include appointments before `after_datetime`.
            if appointment['appointment_date_time'] >= after_date_time:
                appointments.append(appointment.copy())
        
        # Sort by appointment time
        appointments.sort(key=lambda a: a['appointment_date_time'])
        
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
            Appointment dictionary or {} if not found
        """
        return self.appointments.get(appointment_id, {})


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
        for appointment in self.appointments.values():
            if not appointment['status'] == 'cancelled' and \
                    appointment['patient_name'] == patient_name and \
                    appointment['appointment_date_time'] == appointment_date_time:
                return appointment['appointment_id']
        
        return ''

    def __str__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        """Create a JSON string from the object."""
        return AppointmentManager.def_json_encoder.encode(self)

    def from_json(text: Any) -> AppointmentManager:
        """Attempt to parse a JSON object, returning an instance."""
        return AppointmentManager.def_json_decoder.decode(text)

