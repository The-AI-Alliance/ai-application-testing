"""
Unit tests for the appointment management tool.
Uses Hypothesis
"""
from hypothesis import given, strategies as st
import json, os, tempfile, unittest
from collections.abc import Iterator
from datetime import datetime, timedelta, date, time
from pathlib import Path
from typing import Any, Callable

from apps.chatbot.tools.appointment_manager import AppointmentManager, AppointmentError

def is_work_hours(dt: datetime) -> bool:
    if (dt.month, dt.day) in AppointmentManager.USA_HOLIDAYS:
        return False
    elif dt.weekday() > 4:
        return False
    elif dt.hour < 8 or dt.hour >= 17:
        return False
    return True

def future_datetimes(
    datetime_strategy = st.datetimes,
    min_value: datetime = datetime.min,
    max_value: datetime = datetime.max):
    """
    Only return datetimes in the future.

    Args:

    - min_value for the earliest datetime. If the value is < datetime.now(), then datetime.now() is used.
    - max_value for the latest datetime. If the value is <= datetime.now() or < min_value, then datetime.max.
    
    Returns:
    datetimes that occur in the future between the min_value and max_value.
    """
    now = datetime.now()
    if min_value < now:
        min_value = now
    if max_value <= now or max_value < min_value:
        max_value = datetime.max
    return datetime_strategy(min_value = min_value, max_value = max_value)

def years():
    """Only support this year and next"""
    this_year = datetime.now().year
    return st.one_of(st.integers(min_value=this_year, max_value=this_year+1))

def work_dates(future: bool = True):
    today = datetime.now().date()
    min_value = today + timedelta(days=1)
    max_value = date.max
    if not future:
        min_value = date.min
        max_value = today - timedelta(days=1)
    return st.dates(min_value=min_value, max_value=max_value).filter(
        lambda dt: dt.weekday() <= 4 and (dt.month, dt.day) not in AppointmentManager.USA_HOLIDAYS
    )

def work_hours():
    return st.integers(min_value=8, max_value=16)
def non_work_hours():
    return st.one_of(st.integers(min_value=0, max_value=7), st.integers(min_value=17, max_value=23))

def on_the_hour_minutes():
    return st.just(0)
def off_the_hour_minutes():
    return st.integers(min_value=1, max_value=59)

def datetimes(
    date_strategy = work_dates,
    hour_strategy = work_hours,
    minute_strategy = on_the_hour_minutes):
    def tuple_to_datetime(t: tuple[date,int,int]) -> datetime:
        (dte, hour, minute) = t
        return datetime(dte.year, dte.month, dte.day, hour, minute)
    return st.tuples(date_strategy(), hour_strategy(), minute_strategy()).map(
        lambda t: tuple_to_datetime(t)
    )

def past_datetimes(
    hour_strategy = work_hours,
    minute_strategy = on_the_hour_minutes):
    return datetimes(
        date_strategy = lambda: work_dates(future=False),
        hour_strategy = hour_strategy,
        minute_strategy = minute_strategy)


def patient_name(test_strategy = st.text, min_name_parts_size=1, max_name_parts_size=3, min_part_length=1, max_part_length=20):
    if min_name_parts_size < 1:
        min_name_parts_size = 1
    if max_name_parts_size < min_name_parts_size or max_name_parts_size < 1:
        max_name_parts_size = min_name_parts_size + 1
    if min_part_length < 1:
        min_part_length = 1
    if max_part_length < min_part_length or max_part_length < 1:
        max_part_length = min_part_length + 1
    return st.lists(test_strategy(
            min_size=min_part_length, max_size=max_part_length),
        min_size=min_name_parts_size, max_size=max_name_parts_size
    ).map(lambda l: ' '.join(l))

def appointment_dicts(
    datetime_strategy = datetimes,
    patient_name_strategy = patient_name,
    reason_strategy = st.text):
    return st.tuples(datetime_strategy(), patient_name_strategy(), reason_strategy()).map(lambda t:
        AppointmentManager.make_appointment_dict(
        appointment_time = t[0],
        patient_name = t[1],
        reason = t[2],
        status = 'scheduled'))

def list_appointment_dicts(
    datetime_strategy = datetimes,
    patient_name_strategy = patient_name,
    reason_strategy = st.text):
    return st.lists(
        appointment_dicts(
            datetime_strategy = datetime_strategy,
            patient_name_strategy = patient_name_strategy,
            reason_strategy = reason_strategy),
        unique_by=lambda dct: dct['appointment_time'])

class TestAppointmentManager(unittest.TestCase):
    """Test cases for AppointmentManager"""

    one_second = timedelta(seconds=1)

    def _make_tool(self, file_name: str = '', clear: bool = True) -> AppointmentManager:
        if not file_name:
            file_name = self.temp_file.name
        self.tool = AppointmentManager(file_name)
        if clear:
            self.tool.clear()
        return self.tool

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.temp_file.close()
        self._make_tool()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_initialization_creates_file(self):
        """Test that initialization creates the appointments file if it doesn't exist"""
        self.assertTrue(os.path.exists(self.temp_file.name))

    def _result_expected(self, expected: dict[str,Any], actual: dict[str,Any],
        appointment_time: datetime | None = None,
        changed_at: datetime | None = None,
        patient_name: str = '',
        reason: str = ''):

        if not appointment_time:
            appointment_time = expected.get('appointment_time')
        if not changed_at:
            changed_at = expected.get('changed_at')
        if not patient_name:
            patient_name = expected.get('patient_name')
        if not reason:
            reason = expected.get('reason')

        self.assertIn('appointment_id', actual, str(actual))
        self.assertTrue(actual.get('success', True), str(actual))
        
        self.assertEqual(appointment_time, actual.get('appointment_time'), f"appointment_time expected: {appointment_time}, actual: {actual}")
        if changed_at:
            self.assertIsNotNone(actual.get('changed_at')) 
            self.assertGreaterEqual(changed_at, actual.get('changed_at'), f"changed_at expected: {changed_at}, actual: {actual}")
        self.assertEqual(patient_name, actual.get('patient_name'), f"patient_name expected: {patient_name}, actual: {actual}")
        self.assertEqual(reason, actual.get('reason'), f"reason expected: {reason}, actual: {actual}")

    def _check_success(self, appointment_dict: dict[str,Any]):
        before_count = self.tool.get_appointments_count()
        try:
            result = self.tool.create_appointment(
                patient_name = appointment_dict['patient_name'],
                appointment_time = appointment_dict['appointment_time'],
                reason = appointment_dict['reason'])
        except AppointmentError as ae:
            self.fail(f"{ae}, patient_name = {appointment_dict['patient_name']}, appointment_time = {appointment_dict['appointment_time']}, reason = {appointment_dict['reason']}, appointments = {self.tool.appointments}")

        after_count = self.tool.get_appointments_count()
        self.assertEqual(before_count+1, after_count)
        self._result_expected(appointment_dict, result)
        return result

    def _check_failure(self, appointment_dict: dict[str,Any]):
        before_count = self.tool.get_appointments_count()
        with self.assertRaises(AppointmentError, msg=str(appointment_dict)):
            self.tool.create_appointment(
                patient_name = appointment_dict['patient_name'],
                appointment_time = appointment_dict['appointment_time'],
                reason = appointment_dict['reason'])
        after_count = self.tool.get_appointments_count()
        self.assertEqual(before_count, after_count)

    def _check_appointments_list(self, 
        list_appointment_dicts: Iterator[dict[str,Any]],
        get_list: Callable[[], list[dict[str,Any]]],
        get_appointment: Callable[[str], dict[str,Any]] | None = None):
        """
        Test a list of appointments. The get_list lambda returns the list to
        check. The get_appointment lambda returns an appointment by id. The 
        default value of None means, just get the appointment from the list 
        returned by get_appointments.
        """
        # sanity checks:
        self.tool.clear()
        self.assertEqual(0, len(get_list()), str(get_list()))
        dt_set = set([d['appointment_time'] for d in list_appointment_dicts])
        self.assertEqual(len(list_appointment_dicts), len(dt_set), f"{list_appointment_dicts} != {dt_set}")
        
        created = {}
        for appointment_dict in list_appointment_dicts:
            appointment = self._check_success(appointment_dict)
            created[appointment['appointment_id']] = appointment

        appointments = get_list()
        self.assertEqual(len(appointments), len(created))
        for appointment_id in created:
            appointment = None
            if get_appointment:
                appointment = get_appointment(appointment_id) 
            else:
                for appt in appointments:
                    if appt['appointment_id'] == appointment_id:
                        appointment = appt
                        break
            self.assertIsNotNone(appointment)
            expected = created.get(appointment_id)
            self.assertEqual(appointment_id, appointment['appointment_id'])
            self.assertEqual(appointment_id, expected['appointment_id'])
            self.assertEqual(expected['appointment_time'], appointment['appointment_time'])
            self.assertEqual(expected['patient_name'], appointment['patient_name'])
            self.assertEqual(expected['reason'], appointment['reason'])

    @given(appointment_dicts())
    def test_create_appointment_succeeds_if_datetime_in_the_future_on_the_hour_and_slot_is_open(self, 
        appointment_dict: dict[str,Any]):
        """
        Test successful creation of an appointment with a valid time, assuming 
        no other appointments exist.
        """
        self.tool.clear()
        self._check_success(appointment_dict)

    @given(appointment_dicts(datetime_strategy=past_datetimes))     
    def test_create_appointment_fails_if_datetime_in_the_past(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a past datetime.
        """
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = lambda: datetimes(hour_strategy = non_work_hours)))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_a_work_hour(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a future, non-work datetime.
        """
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = lambda: datetimes(minute_strategy = off_the_hour_minutes)))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_on_the_hour(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a future, off-hour work time.
        """
        self._check_failure(appointment_dict)

    @given(appointment_dicts())
    def test_create_appointment_duplicate_time_fails(self, 
        appointment_dict: dict[str,Any]):
        """Test that creating two appointments at the same time fails"""
        self.tool.clear()

        # First appointment should succeed
        self._check_success(appointment_dict)
        
        # Second appointment at same time should fail
        self._check_failure(appointment_dict)

    @given(appointment_dicts())
    def test_cancel_appointment_succeeds_if_it_exists(self, 
        appointment_dict: dict[str,Any]):
        """Test canceling an existing appointment"""
        appointment = self._check_success(appointment_dict)

        id = appointment['appointment_id']
        
        before_count  = self.tool.get_appointments_count()
        cancel_result = self.tool.cancel_appointment(id)
        after_count   = self.tool.get_appointments_count()
        self.assertEqual(before_count-1, after_count)
        self.assertTrue(cancel_result['success'])
        self.assertEqual(cancel_result['status'], 'cancelled')

    @given(st.uuids())
    def test_cancel_nonexistent_appointment_fails(self, uuid):
        """Test that canceling a non-existent appointment fails"""
        before_count  = self.tool.get_appointments_count()
        with self.assertRaises(AppointmentError) as context:
            self.tool.cancel_appointment(str(uuid))
        self.assertIn("not found", str(context.exception).lower())
        after_count   = self.tool.get_appointments_count()
        self.assertEqual(before_count, after_count)

    @given(list_appointment_dicts())
    def test_confirm_appointment_succeeds_if_it_exists(self, dicts: list[dict[str,Any]]):
        """Test confirming an existing appointment"""
        self.tool.clear()
        for d in dicts:
            appt = self._check_success(d)
            criteria = {
                'appointment_id':   appt.get('appointment_id'),
                'appointment_time': appt.get('appointment_time'),
                'patient_name':     appt.get('patient_name'),
            }
            confirm = self.tool.confirm_appointment(criteria)
            self.assertEqual(1, len(confirm), f"{criteria} in {self.tool.appointments}?")
            for key, value in criteria.items():
                self.assertEqual(value, confirm[0].get(key))

    @given(st.uuids())
    def test_confirm_appointment_returns_empty_if_it_does_not_exist(self, uuid):
        self.assertEqual([], self.tool.confirm_appointment(str(uuid)))

    @given(appointment_dicts(), datetimes())
    def test_change_appointment_successful_if_it_exists(self, 
        appointment_dict: dict[str,Any], new_datetime: datetime):
        """
        Test changing an appointment to a new time.
        There is a slight chance the randomly generated new_datetime
        will equal the existing datetime, but we allow this.
        """
        self.tool.clear()
        appointment = self._check_success(appointment_dict)

        if appointment['appointment_time'] == new_datetime:
            match new_datetime.hour:
                case 16:
                    new_datetime = new_datetime - timedelta(hours=1)
                case _:
                    new_datetime = new_datetime + timedelta(hours=1)

        updated = self.tool.change_appointment(
            appointment['appointment_id'],
            new_datetime)
        self._result_expected(appointment_dict, updated,
            appointment_time = new_datetime,
            changed_at = new_datetime)

    @given(appointment_dicts())
    def test_get_appointment_returns_nonempty_if_it_exists(self, 
        appointment_dict: dict[str,Any]):
        """Test that get_appointment returns existing appointments."""
        self.tool.clear()
        appointment = self._check_success(appointment_dict)
        id = appointment['appointment_id']
        appointment2 = self.tool.get_appointment(id)
        self.assertNotEqual({}, appointment2)
        self._result_expected(appointment_dict, appointment2)

    @given(list_appointment_dicts())
    def test_appointments_persist_across_instances(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d)
            ids.append(appointment['appointment_id'])
        
        # Create new instance and verify appointment exists
        new_tool = self._make_tool(clear = False)
        appointments = new_tool.list_appointments()
        # check with both the default way of getting an appointment and
        # passing new_tool.get_appointment
        self._check_appointments_list(list_appointment_dicts, 
            new_tool.list_appointments)
        self._check_appointments_list(list_appointment_dicts, 
            new_tool.list_appointments,
            get_appointment = new_tool.get_appointment)


    @given(list_appointment_dicts())
    def test_clear_erases_appointments(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        apmts = [self._check_success(d) for d in list_appointment_dicts]
        self.assertEqual(len(apmts), self.tool.get_appointments_count())
        self.tool.clear()
        self.assertEqual(0, self.tool.get_appointments_count())
        new_tool = self._make_tool(clear = False)
        self.assertEqual(0, new_tool.get_appointments_count())
        
if __name__ == '__main__':
    unittest.main()

# Made with Bob
