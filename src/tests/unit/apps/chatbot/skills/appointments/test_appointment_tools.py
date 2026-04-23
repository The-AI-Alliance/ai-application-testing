"""
Unit tests for the appointment skills tool.
Uses Hypothesis.
"""
from hypothesis import given, strategies as st
import contextlib, io, json, logging, os, tempfile, unittest
from collections.abc import Iterator
from datetime import datetime, timedelta, date, time
from pathlib import Path
from typing import Any, Callable
from langchain_core.tools.structured import StructuredTool

from apps.chatbot.tools.appointment_manager import AppointmentManager

from apps.chatbot.skills.appointments.appointment_tools import (
    get_appointment_manager,
    create_appointment,
    cancel_appointment,
    change_appointment,
    list_appointments,
    get_appointments_count,
    get_appointment,
    get_appointment_id_for_name_and_date_time,
)

from tests.common.hypothesis.datetimes import (
    is_work_hours,
    future_dates,
    past_dates,
    work_dates,
    work_hours,
    non_work_hours,
    on_the_hour_minutes,
    off_the_hour_minutes,
    future_work_datetimes,
    past_work_datetimes,
)

from tests.common.hypothesis.persons import (
    person_names,
)


from tests.common.hypothesis.appointments import (
    appointment_work_hours,
    appointment_non_work_hours,
    appointment_future_work_datetimes,
    appointment_future_non_work_datetimes,
    appointment_dicts,
    list_appointment_dicts,
)

class TestAppointmentTools(unittest.TestCase):
    """
    Test cases for the _skills_ tools in `appointment_tools.py`.
    A few notes about unit tests for these tools. Although the tool definitions look
    like normal method definitions, the `@tool` annotation turns them into LangChain's
    `StructuredTools`. Hence, you don't invoke, e.g., `create_appointment` as follows:
    ```
    create_appointment(patient_name, date_time_string)
    ```

    Instead, you invoke it as follows: 
    ```
    create_appointment.run({
        'patient_name': patient_name, 
        'appointment_date_time': date_time_string
    })
    ```

    Also, it appears the tool writes to `sys.stderr` sometimes, so we capture that output.
    """

    def _make_manager(self) -> AppointmentManager:
        file_path = Path(self.temp_file.name)
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.CRITICAL) # suppress almost everything...
        
        self.tool = get_appointment_manager(file_path, logger = logger, make_new = True)
        self.assertEqual(file_path, self.tool.storage.storage_path)
        return self.tool

    def _clear(self):
        self.tool.clear()
        self.assertEqual({}, self.tool.appointments)

    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.temp_file.close()
        self._make_manager()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def _check_file(self, file: Path | str = None):
        if not file:
            file = Path(self.temp_file.name)
        self.assertTrue(os.path.exists(file))
        self.assertEqual(str(file), str(self.tool.storage.storage_path))

    def test_get_appointment_manager_instantiates_a_manager(self):
        self._check_file()

    def test_get_appointment_manager_instantiates_a_new_manager_when_make_new_is_true(self):
        original_tool = self.tool
        new_tool = get_appointment_manager(self.tool.storage.storage_path, logger=self.tool.logger,
            make_new=True)
        self.assertIsNot(original_tool, new_tool)

    def test_get_appointment_manager_does_not_instantiate_a_new_manager_even_with_diff_arguments(self):
        original_tool = self.tool
        same_tool = get_appointment_manager('toss.jsonl', logger=None)
        self.assertIs(original_tool, same_tool)

    def test_get_appointment_manager_does_not_instantiate_a_new_manager_with_no_arguments(self):
        original_tool = self.tool
        same_tool = get_appointment_manager()
        self.assertIs(original_tool, same_tool)

    def test_initialization_creates_file(self):
        """Test that initialization creates the appointments file if it doesn't exist"""
        self._check_file()

    def _result_expected(self, expected: dict[str,Any], actual: dict[str,Any],
        appointment_date_time: datetime | None = None,
        changed_at: datetime | None = None,
        patient_name: str = '',
        reason: str = ''):

        if not appointment_date_time:
            appointment_date_time = expected.get('appointment_date_time')
        if not changed_at:
            changed_at = expected.get('changed_at')
        if not patient_name:
            patient_name = expected.get('patient_name')
        if not reason:
            reason = expected.get('reason')

        self.assertIn('appointment_id', actual, str(actual))
        self.assertTrue(actual.get('success', True), str(actual))
        
        self.assertEqual(appointment_date_time, actual.get('appointment_date_time'), f"appointment_date_time expected: {appointment_date_time}, actual: {actual}")
        if changed_at:
            self.assertIsNotNone(actual.get('changed_at')) 
            self.assertGreaterEqual(changed_at, actual.get('changed_at'), f"changed_at expected: {changed_at}, actual: {actual}")
        self.assertEqual(patient_name, actual.get('patient_name'), f"patient_name expected: {patient_name}, actual: {actual}")
        self.assertEqual(reason, actual.get('reason'), f"reason expected: {reason}, actual: {actual}")

    def _results_list_expected(self, expected: list[dict[str,Any]], actual: list[dict[str,Any]]):
        self.assertEqual(len(expected), len(actual))
        expected2 = sorted(expected, key=lambda a: a['appointment_date_time'])
        actual2   = sorted(actual,   key=lambda a: a['appointment_date_time'])
        for i in range(len(expected2)):
            e = expected2[i]
            a = actual2[i]
            self._result_expected(e, a)

    def _capture_output(self, tool: StructuredTool, params: dict[str,Any]) -> Any:
        with contextlib.redirect_stdout(io.StringIO()) as fout:
            with contextlib.redirect_stderr(io.StringIO()) as ferr:
                success, message = tool.run(params)
                if success:
                    self.assertEqual('', fout.getvalue())
                    self.assertEqual('', ferr.getvalue())
                else:
                    self.assertEqual('', fout.getvalue())
                    self.assertNotEqual('', ferr.getvalue())
                return success, message

    def _check_success(self, 
        appointment_dict: dict[str,Any],
        all: list[dict[str,Any]] = []) -> dict[str,Any]:
        before_count = get_appointments_count.run({})
        patient_name = appointment_dict['patient_name']
        appointment_date_time = appointment_dict['appointment_date_time'].isoformat()
        reason = appointment_dict['reason']
        id, msg = self._capture_output(create_appointment, {
            'patient_name': patient_name,
            'appointment_date_time': appointment_date_time,
            'reason': reason
        })
        self.assertNotEqual('', id, f"{msg}, dict: {appointment_dict}, all: {all}, appointments: {list_appointments.run({})}")
        self.assertNotEqual('', msg, "Returned message is empty!")
        after_count = get_appointments_count.run({})
        self.assertEqual(before_count+1, after_count)
        id = get_appointment_id_for_name_and_date_time.run({
            'patient_name': patient_name, 
            'appointment_date_time': appointment_date_time,
        })
        self.assertNotEqual('', id)
        appt = get_appointment.run({'appointment_id': id})
        self._result_expected(appointment_dict, appt)
        return appt

    def _check_failure(self, appointment_dict: dict[str,Any]):
        before_count = get_appointments_count.run({})
        patient_name = appointment_dict['patient_name']
        appointment_date_time = appointment_dict['appointment_date_time'].isoformat()
        reason = appointment_dict['reason']
        id, msg = self._capture_output(create_appointment, {
            'patient_name': patient_name,
            'appointment_date_time': appointment_date_time,
            'reason': reason,
        })
        self.assertEqual('', id, msg)
        self.assertNotEqual('', msg, "Returned message is empty!")
        after_count = get_appointments_count.run({})
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
        self._clear()
        self.assertEqual(0, len(get_list()), str(get_list()))
        dt_set = set([d['appointment_date_time'] for d in list_appointment_dicts])
        self.assertEqual(len(list_appointment_dicts), len(dt_set), f"{list_appointment_dicts} != {dt_set}")
        
        created = {}
        for appointment_dict in list_appointment_dicts:
            appointment = self._check_success(appointment_dict, all=list_appointment_dicts)
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
        self._clear()
        self._check_success(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = past_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_past(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a past datetime.
        """
        self._clear()
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = appointment_future_non_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_a_work_hour(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a future, non-work datetime.
        """
        self._clear()
        self._check_failure(appointment_dict)

    @given(appointment_dicts(
        datetime_strategy = lambda: appointment_future_work_datetimes(minute_strategy = off_the_hour_minutes)))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_on_the_hour(self, 
        appointment_dict: dict[str,Any]):
        """
        Test failure to create an appointment with a future, off-hour work time.
        """
        self._clear()
        self._check_failure(appointment_dict)

    @given(appointment_dicts())
    def test_create_appointment_duplicate_time_fails(self, 
        appointment_dict: dict[str,Any]):
        """Test that creating two appointments at the same time fails"""
        self._clear()

        # First appointment should succeed
        self._check_success(appointment_dict)
        
        # Second appointment at same time should fail
        self._check_failure(appointment_dict)

    @given(appointment_dicts())
    def test_cancel_appointment_succeeds_if_it_exists(self, 
        appointment_dict: dict[str,Any]):
        """Test canceling an existing appointment"""
        self._clear()
        appointment = self._check_success(appointment_dict)
        id = appointment['appointment_id']
        
        before_count  = get_appointments_count.run({})
        success, msg = self._capture_output(cancel_appointment, {'appointment_id': id})
        after_count   = get_appointments_count.run({})
        self.assertTrue(success, msg)
        self.assertNotEqual('', msg)
        self.assertEqual(before_count-1, after_count)
        appt = get_appointment.run({'appointment_id': id})
        self.assertEqual({}, appt)

    @given(st.uuids())
    def test_cancel_nonexistent_appointment_fails(self, uuid):
        """Test that canceling a non-existent appointment fails"""
        self._clear()
        before_count = get_appointments_count.run({})
        success, msg = self._capture_output(cancel_appointment, {'appointment_id': str(uuid)})
        self.assertFalse(success, msg)
        self.assertNotEqual('', msg)
        after_count  = get_appointments_count.run({})
        self.assertEqual(before_count, after_count)

    @given(appointment_dicts(), appointment_future_work_datetimes())
    def test_change_appointment_successful_if_it_exists(self, 
        appointment_dict: dict[str,Any], new_date_time: datetime):
        """
        Test changing an appointment to a new time.
        There is a slight chance the randomly generated new_date_time
        will equal the existing datetime, but we allow this.
        """
        self._clear()
        appointment = self._check_success(appointment_dict)
        if appointment['appointment_date_time'] == new_date_time:
            match new_date_time.hour:
                case 16:
                    new_date_time = new_date_time - timedelta(hours=1)
                case _:
                    new_date_time = new_date_time + timedelta(hours=1)

        id = appointment['appointment_id']
        success, msg = self._capture_output(change_appointment, {
            'appointment_id': id,
            'new_date_time': new_date_time.isoformat()
        })
        self.assertTrue(success, msg)
        updated = get_appointment.run({'appointment_id': id})
        self._result_expected(appointment_dict, updated,
            appointment_date_time = new_date_time,
            changed_at = new_date_time)

    @given(list_appointment_dicts())
    def test_list_appointments_with_no_filters_returns_all_appointments(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self._clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d, all=list_appointment_dicts)
            ids.append(appointment['appointment_id'])
        
        appointments = list_appointments.run({})
        self._results_list_expected(list_appointment_dicts, appointments)

    @given(list_appointment_dicts().filter(lambda l: len(l) > 0))
    def test_list_appointments_with_patient_name_filter_returns_appointments_for_that_patient(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self._clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d, all=list_appointment_dicts)
            ids.append(appointment['appointment_id'])
        
        patient_name = list_appointment_dicts[0]['patient_name']
        expected_list = list(filter(lambda a: a['patient_name'] == patient_name, list_appointments.run({})))
        appointments = list_appointments.run({'patient_name': patient_name})
        self._results_list_expected(expected_list, appointments)

    @given(list_appointment_dicts().filter(lambda l: len(l) > 0))
    def test_list_appointments_with_date_time_lower_bound_returns_appointments_later_than_that_date_time(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self._clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d, all=list_appointment_dicts)
            ids.append(appointment['appointment_id'])
        
        # Pick an entry in the middle:
        i = int(len(list_appointment_dicts)/2)
        date_time = list_appointment_dicts[i]['appointment_date_time']
        expected_list = list(filter(lambda a: a['appointment_date_time'] >= date_time, list_appointments.run({})))
        appointments = list_appointments.run({'after_date_time': date_time.isoformat()})
        self._results_list_expected(expected_list, appointments)

    @given(list_appointment_dicts())
    def test_get_appointments_count_returns_the_number_of_appointments(self,
        list_appointment_dicts: list[dict[str,Any]]):
        self._clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d, all=list_appointment_dicts)
            ids.append(appointment['appointment_id'])
        self.assertEqual(len(list_appointment_dicts), get_appointments_count.run({}))

    @given(appointment_dicts())
    def test_get_appointment_returns_nonempty_dict_if_it_exists(self, 
        appointment_dict: dict[str,Any]):
        self._clear()
        appointment2 = self._check_success(appointment_dict)
        appointment = get_appointment.run({
            'appointment_id': appointment2['appointment_id']
        })
        self._result_expected(appointment_dict, appointment)

    @given(appointment_dicts())
    def test_get_appointment_returns_empty_dict_if_key_does_not_exist(self, 
        appointment_dict: dict[str,Any]):
        self._clear()
        appointment2 = self._check_success(appointment_dict)
        appointment = get_appointment.run({
            'appointment_id': appointment2['appointment_id']+'bad'
        })
        self.assertEqual({}, appointment)

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_nonempty_if_match_exists(self, 
        appointment_dict: dict[str,Any]):
        self._clear()
        appointment2 = self._check_success(appointment_dict)
        id = get_appointment_id_for_name_and_date_time.run({
            'patient_name': appointment_dict['patient_name'],
            'appointment_date_time': appointment_dict['appointment_date_time'].isoformat()
        })
        self.assertEqual(appointment2['appointment_id'], id)

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_empty_if_match_does_not_exist(self, 
        appointment_dict: dict[str,Any]):
        self._clear()
        appointment2 = self._check_success(appointment_dict)
        id = get_appointment_id_for_name_and_date_time.run({
            'patient_name': appointment_dict['patient_name']+'bad',
            'appointment_date_time': appointment_dict['appointment_date_time'].isoformat()
        })
        self.assertEqual('', id)
        bad_dt = (appointment_dict['appointment_date_time']+timedelta(seconds=1)).isoformat()
        id = get_appointment_id_for_name_and_date_time.run({
            'patient_name': appointment_dict['patient_name'],
            'appointment_date_time': bad_dt
        })
        self.assertEqual('', id)

    @given(list_appointment_dicts())
    def test_appointments_persist_across_instances(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self._clear()
        ids = []
        for d in list_appointment_dicts:
            appointment = self._check_success(d, all=list_appointment_dicts)
            ids.append(appointment['appointment_id'])
        self.assertEqual(len(list_appointment_dicts), len(self.tool.appointments))
        
        # Create new instance and verify appointments exist.
        old_tool = self.tool
        new_tool = self._make_manager()
        self.assertIsNot(old_tool, new_tool)
        appointments = new_tool.list_appointments()
        # check with both the default way of getting an appointment and
        # passing new_tool.get_appointment
        self._check_appointments_list(list_appointment_dicts, 
            new_tool.list_appointments)
        self._check_appointments_list(list_appointment_dicts, 
            new_tool.list_appointments,
            get_appointment = new_tool.get_appointment)

    @given(list_appointment_dicts().filter(lambda l: len(l) > 0))
    def test_clear_erases_appointments(self,
        list_appointment_dicts: list[dict[str,Any]]):
        """Test that appointments persist across tool instances"""
        self._clear()
        apmts = [self._check_success(d, all=list_appointment_dicts) for d in list_appointment_dicts]
        self.assertEqual(len(apmts), get_appointments_count.run({}))
        self._clear()
        self.assertEqual(0, get_appointments_count.run({}))
        
if __name__ == '__main__':
    unittest.main()
