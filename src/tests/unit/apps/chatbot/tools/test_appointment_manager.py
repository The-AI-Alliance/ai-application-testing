"""
Unit tests for the appointment management tool.
Uses Hypothesis.
"""
from hypothesis import given, strategies as st
import json, logging, os, tempfile, unittest
from collections.abc import Iterator
from datetime import datetime, timedelta, date, time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from apps.chatbot.tools.appointment_manager import AppointmentManager

from tests.common.hypothesis.datetimes import (
    off_the_hour_minutes,
    past_work_datetimes,
)

from tests.common.hypothesis.appointments import (
    appointment_work_hours,
    appointment_non_work_hours,
    appointment_future_work_datetimes,
    appointment_future_non_work_datetimes,
    appointment_dicts,
    appointment_dicts_lists,
)

class TestAppointmentManager(unittest.TestCase):
    """Test cases for AppointmentManager"""

    one_second = timedelta(seconds=1)

    def _make_tool(self, file_name: str = '', clear: bool = True) -> AppointmentManager:
        if not file_name:
            file_name = self.temp_file.name
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.CRITICAL) # suppress almost everything...
        self.tool = AppointmentManager(file_name, logger=logger)
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

    def _result_expected(self, expected: Mapping[str,Any], actual: Mapping[str,Any],
        appointment_date_time: datetime | None = None,
        changed_at: datetime | None = None,
        patient_name: str = '',
        reason: str = ''):

        if not appointment_date_time:
            appointment_date_time = expected.get('appointment_date_time', datetime.now())
        if not changed_at:
            changed_at = expected.get('changed_at', datetime.now())
        if not patient_name:
            patient_name = expected.get('patient_name', '')
        if not reason:
            reason = expected.get('reason', '')

        self.assertIn('id', actual, str(actual))
        self.assertTrue(actual.get('success', True), str(actual))
        
        self.assertEqual(appointment_date_time, actual.get('appointment_date_time'), f"appointment_date_time expected: {appointment_date_time}, actual: {actual}")
        if changed_at:
            actual_changed_at = actual.get('changed_at', datetime(1970, 1, 1))
            self.assertTrue(changed_at >= actual_changed_at, f"changed_at expected: {changed_at}, actual: {actual}")
        self.assertEqual(patient_name, actual.get('patient_name'), f"patient_name expected: {patient_name}, actual: {actual}")
        self.assertEqual(reason, actual.get('reason'), f"reason expected: {reason}, actual: {actual}")

    def _results_list_expected(self, expected: Sequence[Mapping[str,Any]], actual: Sequence[Mapping[str,Any]]):
        self.assertEqual(len(expected), len(actual))
        expected2 = sorted(expected, key=lambda a: a['appointment_date_time'])
        actual2   = sorted(actual,   key=lambda a: a['appointment_date_time'])
        for i in range(len(expected2)):
            e = expected2[i]
            a = actual2[i]
            self._result_expected(e, a)

    def _check_success(self, appointment_dict: Mapping[str,Any]) -> Mapping[str,Any]:
        before_count = self.tool.get_appointments_count()
        patient_name = appointment_dict['patient_name']
        appointment_date_time = appointment_dict['appointment_date_time']
        reason = appointment_dict['reason']
        id, msg = self.tool.create_appointment(
            patient_name = patient_name,
            appointment_date_time = appointment_date_time,
            reason = reason)
        self.assertNotEqual('', id, msg)
        self.assertNotEqual('', msg)
        after_count = self.tool.get_appointments_count()
        self.assertEqual(before_count+1, after_count)
        appt = self.tool.get_appointment_by_id(id)
        self._result_expected(appointment_dict, appt)
        return appt

    def _check_failure(self, appointment_dict: Mapping[str,Any]):
        before_count = self.tool.get_appointments_count()
        patient_name = appointment_dict['patient_name']
        appointment_date_time = appointment_dict['appointment_date_time']
        reason = appointment_dict['reason']
        id, msg = self.tool.create_appointment(
            patient_name = patient_name,
            appointment_date_time = appointment_date_time,
            reason = reason)
        self.assertEqual('', id)
        self.assertNotEqual('', msg)
        after_count = self.tool.get_appointments_count()
        self.assertEqual(before_count, after_count)

    def _check_appointments_list(self, 
        appointment_dicts_lists: Sequence[Mapping[str,Any]],
        get_list: Callable[[], Sequence[Mapping[str,Any]]],
        get_appointment: Callable[[str], Mapping[str,Any]] | None = None):
        """
        Test a list of appointments. The get_list lambda returns the list to
        check. The get_appointment lambda returns an appointment by id. The 
        default value of None means, just get the appointment from the list 
        returned by get_appointments.
        """
        # sanity checks:
        self.tool.clear()
        self.assertEqual(0, len(get_list()), str(get_list()))
        dt_set = set([d['appointment_date_time'] for d in appointment_dicts_lists])
        self.assertEqual(len(appointment_dicts_lists), len(dt_set), f"{appointment_dicts_lists} != {dt_set}")
        
        created = {}
        for appointment_dict in appointment_dicts_lists:
            appointment = self._check_success(appointment_dict)
            created[appointment['id']] = appointment

        appointments = get_list()
        self.assertEqual(len(appointments), len(created))
        for appointment_id in created:
            appointment = {}
            if get_appointment:
                appointment = get_appointment(appointment_id) 
            else:
                for appt in appointments:
                    if appt['id'] == appointment_id:
                        appointment = appt
                        break
            self.assertIsNotNone(appointment)
            expected = created.get(appointment_id, {})
            self.assertIsNotNone(expected)
            if expected and appointment: # redundant with previous lines, but enables proper typing.
                self.assertEqual(appointment_id, appointment['id'])
                self.assertEqual(appointment_id, expected['id'])
                self.assertEqual(expected['appointment_date_time'], appointment['appointment_date_time'])
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

    @given(appointment_dicts(
        datetime_strategy = past_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_past(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a past datetime.
        """
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = appointment_future_non_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_a_work_hour(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a future, non-work datetime.
        """
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = lambda: appointment_future_work_datetimes(minute_strategy = off_the_hour_minutes)))
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
        self.tool.clear()
        appointment = self._check_success(appointment_dict)
        id = appointment['id']
        
        before_count  = self.tool.get_appointments_count()
        success, msg  = self.tool.cancel_appointment(id)
        after_count   = self.tool.get_appointments_count()
        self.assertTrue(success, msg)
        self.assertNotEqual('', msg)
        self.assertEqual(before_count-1, after_count)
        appt = self.tool.get_appointment_by_id(id)
        self.assertEqual({}, appt)

    @given(st.uuids())
    def test_cancel_nonexistent_appointment_fails(self, uuid):
        """Test that canceling a non-existent appointment fails"""
        self.tool.clear()
        before_count = self.tool.get_appointments_count()
        success, msg = self.tool.cancel_appointment(str(uuid))
        self.assertFalse(success, msg)
        self.assertNotEqual('', msg)
        after_count  = self.tool.get_appointments_count()
        self.assertEqual(before_count, after_count)

    @given(appointment_dicts(), appointment_future_work_datetimes())
    def test_change_appointment_successful_if_it_exists(self, 
        appointment_dict: dict[str,Any], new_date_time: datetime):
        """
        Test changing an appointment to a new time.
        There is a slight chance the randomly generated new_date_time
        will equal the existing datetime, but we allow this.
        """
        self.tool.clear()
        appointment = self._check_success(appointment_dict)
        if appointment['appointment_date_time'] == new_date_time:
            match new_date_time.hour:
                case 16:
                    new_date_time = new_date_time - timedelta(hours=1)
                case _:
                    new_date_time = new_date_time + timedelta(hours=1)

        id = appointment['id']
        success, msg = self.tool.change_appointment(id, new_date_time)
        self.assertTrue(success, msg)
        updated = self.tool.get_appointment_by_id(id)
        self._result_expected(appointment_dict, updated,
            appointment_date_time = new_date_time,
            changed_at = new_date_time)

    @given(appointment_dicts_lists())
    def test_get_appointments_with_no_filters_returns_all_appointments(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        ids = []
        for d in appointment_dicts_lists:
            appointment = self._check_success(d)
            ids.append(appointment['id'])
        
        appointments = self.tool.get_appointments()
        self._results_list_expected(appointment_dicts_lists, appointments)

    @given(appointment_dicts_lists().filter(lambda l: len(l) > 0))
    def test_get_appointments_with_patient_name_filter_returns_appointments_for_that_patient(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        ids = []
        for d in appointment_dicts_lists:
            appointment = self._check_success(d)
            ids.append(appointment['id'])
        
        patient_name = appointment_dicts_lists[0]['patient_name']
        expected_list = list(filter(lambda a: a['patient_name'] == patient_name, self.tool.get_appointments()))
        appointments = self.tool.get_appointments(patient_name = patient_name)
        self._results_list_expected(expected_list, appointments)

    @given(appointment_dicts_lists().filter(lambda l: len(l) > 0))
    def test_get_appointments_with_date_time_lower_bound_returns_appointments_later_than_that_date_time(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        ids = []
        for d in appointment_dicts_lists:
            appointment = self._check_success(d)
            ids.append(appointment['id'])
        
        # Pick an entry in the middle:
        i = int(len(appointment_dicts_lists)/2)
        date_time = appointment_dicts_lists[i]['appointment_date_time']
        expected_list = list(filter(lambda a: a['appointment_date_time'] >= date_time, self.tool.get_appointments()))
        appointments = self.tool.get_appointments(after_date_time = date_time)
        self._results_list_expected(expected_list, appointments)

    @given(appointment_dicts_lists())
    def test_get_appointments_count_returns_the_number_of_appointments(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        self.tool.clear()
        ids = []
        for d in appointment_dicts_lists:
            appointment = self._check_success(d)
            ids.append(appointment['id'])
        self.assertEqual(len(appointment_dicts_lists), self.tool.get_appointments_count())

    @given(appointment_dicts())
    def test_get_appointment_returns_nonempty_dict_if_it_exists(self, 
        appointment_dict: dict[str,Any]):
        self.tool.clear()
        appointment2 = self._check_success(appointment_dict)
        appointment = self.tool.get_appointment_by_id(appointment2['id'])
        self._result_expected(appointment_dict, appointment)

    @given(appointment_dicts())
    def test_get_appointment_returns_empty_dict_if_key_does_not_exist(self, 
        appointment_dict: dict[str,Any]):
        self.tool.clear()
        appointment2 = self._check_success(appointment_dict)
        appointment = self.tool.get_appointment_by_id(appointment2['id']+'bad')
        self.assertEqual({}, appointment)

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_nonempty_if_match_exists(self, 
        appointment_dict: dict[str,Any]):
        self.tool.clear()
        appointment2 = self._check_success(appointment_dict)
        id = self.tool.get_appointment_id_for_name_and_date_time(
            appointment_dict['patient_name'],
            appointment_dict['appointment_date_time'])
        self.assertEqual(appointment2['id'], id)

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_empty_if_match_does_not_exist(self, 
        appointment_dict: dict[str,Any]):
        self.tool.clear()
        appointment = self._check_success(appointment_dict)
        name = appointment_dict['patient_name']
        dt = appointment_dict['appointment_date_time']

        id = self.tool.get_appointment_id_for_name_and_date_time(
            name+'bad', dt)
        self.assertEqual('', id, f"{name+'bad'}, {appointment_dict}")
        
        bad_dt = dt+timedelta(seconds=10)
        id = self.tool.get_appointment_id_for_name_and_date_time(
            name, bad_dt)
        self.assertEqual('', id, f"{bad_dt}, {appointment_dict}")

    @given(appointment_dicts_lists())
    def test_appointments_persist_across_instances(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        ids = []
        for d in appointment_dicts_lists:
            appointment = self._check_success(d)
            ids.append(appointment['id'])
        
        # Create new instance and verify appointment exists
        new_tool = self._make_tool(clear = False)
        appointments = new_tool.get_appointments()
        # check with both the default way of getting an appointment and
        # passing new_tool.get_appointment
        self._check_appointments_list(appointment_dicts_lists, 
            new_tool.get_appointments)
        self._check_appointments_list(appointment_dicts_lists, 
            new_tool.get_appointments,
            get_appointment = new_tool.get_appointment_by_id)

    @given(appointment_dicts_lists().filter(lambda l: len(l) > 0))
    def test_clear_erases_appointments(self,
        appointment_dicts_lists: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self.tool.clear()
        apmts = [self._check_success(d) for d in appointment_dicts_lists]
        self.assertEqual(len(apmts), self.tool.get_appointments_count())
        self.tool.clear()
        self.assertEqual(0, self.tool.get_appointments_count())
        new_tool = self._make_tool(clear = False)
        self.assertEqual(0, new_tool.get_appointments_count())

    @given(appointment_dicts_lists().filter(lambda l: len(l) > 0))
    def test_to_json_from_json_are_reversible(self, 
        appointment_dicts_lists: list[dict[str,Any]]):
        self.tool.clear()
        apmts = [self._check_success(d) for d in appointment_dicts_lists]
        am_json = self.tool.to_json()
        am2 = AppointmentManager.from_json(am_json)
        self.assertIsNotNone(am2, am_json)
        self.assertEqual(self.tool.storage.storage_path, am2.storage.storage_path, f"{am_json} -> {am2}")
        self.assertEqual(self.tool.appointments, am2.appointments, am_json)
        
if __name__ == '__main__':
    unittest.main()
