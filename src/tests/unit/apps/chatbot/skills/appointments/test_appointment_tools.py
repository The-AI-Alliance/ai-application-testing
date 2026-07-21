"""
Unit tests for the appointment skills tool.
Uses Hypothesis.
"""

from hypothesis import given, strategies as st
import contextlib
import io
import logging
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence, Tuple
from langchain_core.tools.structured import BaseTool

from apps.chatbot.tools.appointment_manager import AppointmentManager

from apps.chatbot.skills.appointments.appointment_tools import (
    get_appointment_manager,
    create_appointment,
    cancel_appointment,
    change_appointment,
    get_appointment_by_id,
    get_appointments,
    get_appointments_count,
    get_appointment_id_for_name_and_date_time,
)

from tests.common.hypothesis.datetimes import (
    off_the_hour_minutes,
    past_work_datetimes,
)


from tests.common.hypothesis.appointments import (
    appointment_future_work_datetimes,
    appointment_future_non_work_datetimes,
    appointment_dicts,
    appointment_dicts_lists,
)


class AppointmentToolsTestUtil:
    """
    Supports test cases for the _skills_ tools in `appointment_tools.py`.
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

    def __init__(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=True, delete_on_close=False, suffix=".jsonl")
        self.temp_file.close()
        self.tool = self.make_manager(make_new=True)

    def make_manager(self, make_new=True) -> AppointmentManager:
        file_path = Path(self.temp_file.name)
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.CRITICAL)  # suppress almost everything...

        tool = get_appointment_manager(file_path, logger=logger, make_new=make_new)
        assert file_path == tool.storage.storage_path
        return tool

    def clear(self):
        self.tool.clear()
        assert [] == self.tool.get_resources()

    def check_file(self, file: Path | str = ""):
        if not file:
            file = Path(self.temp_file.name)
        assert os.path.exists(file)
        assert str(file) == str(self.tool.storage.storage_path)

    def result_expected(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        appointment_date_time: datetime | None = None,
        changed_at: datetime | None = None,
        patient_name: str = "",
        reason: str = "",
    ):
        if not appointment_date_time:
            appointment_date_time = expected.get("appointment_date_time", datetime.now())
        if not changed_at:
            changed_at = expected.get("changed_at", datetime.now())
        if not patient_name:
            patient_name = expected.get("patient_name", "")
        if not reason:
            reason = expected.get("reason", "")

        assert "id" in actual
        assert actual.get("success", True)
        assert appointment_date_time == actual.get(
            "appointment_date_time"
        ), f"appointment_date_time expected: {appointment_date_time}, actual: {actual}"

        if changed_at:
            actual_changed_at = actual.get("changed_at", datetime(1970, 1, 1))
            assert changed_at >= actual_changed_at, f"changed_at expected: {changed_at}, actual: {actual}"

        assert patient_name == actual.get("patient_name"), f"patient_name expected: {patient_name}, actual: {actual}"
        assert reason == actual.get("reason"), f"reason expected: {reason}, actual: {actual}"

    def results_list_expected(self, expected: list[dict[str, Any]], actual: list[dict[str, Any]]):
        assert len(expected) == len(actual)
        expected2 = sorted(expected, key=lambda a: a["appointment_date_time"])
        actual2 = sorted(actual, key=lambda a: a["appointment_date_time"])
        for i in range(len(expected2)):
            e = expected2[i]
            a = actual2[i]
            self.result_expected(e, a)

    def capture_output(self, tool: BaseTool, params: dict[str, Any]) -> Tuple[Any, Any]:
        # We assert that stdout and stderr are empty.
        with contextlib.redirect_stdout(io.StringIO()) as fout:
            with contextlib.redirect_stderr(io.StringIO()) as ferr:
                success, message = tool.run(params)
                assert "" == fout.getvalue()
                assert "" == ferr.getvalue()
                return success, message

    def successfully_add_valid_appointment(
        self, appointment_dict: dict[str, Any], all: list[dict[str, Any]] = []
    ) -> dict[str, Any]:
        before_count = get_appointments_count.run({})
        patient_name = appointment_dict["patient_name"]
        appointment_date_time = appointment_dict["appointment_date_time"].isoformat()
        reason = appointment_dict["reason"]
        id, msg = self.capture_output(
            create_appointment,
            {
                "patient_name": patient_name,
                "appointment_date_time": appointment_date_time,
                "reason": reason,
            },
        )
        assert (
            "" != id
        ), f"{msg}, dict: {appointment_dict},\nall: {all},\nexisting appointments: {get_appointments.run({})}"
        assert "" != msg, "Returned message is empty!"
        after_count = get_appointments_count.run({})
        assert before_count + 1 == after_count
        id = get_appointment_id_for_name_and_date_time.run(
            {
                "patient_name": patient_name,
                "appointment_date_time": appointment_date_time,
            }
        )
        assert "" != id
        appt = get_appointment_by_id.run({"id": id})
        self.result_expected(appointment_dict, appt)
        return appt

    def fail_to_add_invalid_appointment(self, appointment_dict: dict[str, Any]):
        before_count = get_appointments_count.run({})
        patient_name = appointment_dict["patient_name"]
        appointment_date_time = appointment_dict["appointment_date_time"].isoformat()
        reason = appointment_dict["reason"]
        id, msg = self.capture_output(
            create_appointment,
            {
                "patient_name": patient_name,
                "appointment_date_time": appointment_date_time,
                "reason": reason,
            },
        )
        assert "" == id, msg
        assert "" != msg, "Returned message is empty!"
        after_count = get_appointments_count.run({})
        assert before_count == after_count

    def check_appointments_lists(
        self,
        expected_appointments: Sequence[Mapping[str, Any]],
        actual_appointments: Sequence[Mapping[str, Any]],
    ):
        """
        Test that two lists of appointments are identical.
        """
        assert len(expected_appointments) == len(actual_appointments)
        for i in range(len(expected_appointments)):
            ea = expected_appointments[i]
            aa = actual_appointments[i]
            assert ea["id"] == aa["id"]
            assert ea["appointment_date_time"] == aa["appointment_date_time"]
            assert ea["patient_name"] == aa["patient_name"]
            assert ea["reason"] == aa["reason"]


class TestAppointmentTools:
    @given(appointment_dicts())
    def test_create_appointment_succeeds_if_datetime_in_the_future_on_the_hour_and_slot_is_open(
        self, appointment_dict: dict[str, Any]
    ):
        """
        Test successful creation of an appointment with a valid time, assuming
        no other appointments exist.
        """
        test_util = AppointmentToolsTestUtil()
        test_util.successfully_add_valid_appointment(appointment_dict)

    @given(appointment_dicts(datetime_strategy=past_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_past(self, appointment_dict: dict[str, Any]):
        """
        Test failure to create an appointment with a past datetime.
        """
        test_util = AppointmentToolsTestUtil()
        test_util.fail_to_add_invalid_appointment(appointment_dict)

    @given(appointment_dicts(datetime_strategy=appointment_future_non_work_datetimes))
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_a_work_hour(
        self, appointment_dict: dict[str, Any]
    ):
        """
        Test failure to create an appointment with a future, non-work datetime.
        """
        test_util = AppointmentToolsTestUtil()
        test_util.fail_to_add_invalid_appointment(appointment_dict)

    @given(
        appointment_dicts(
            datetime_strategy=lambda: appointment_future_work_datetimes(minute_strategy=off_the_hour_minutes)
        )
    )
    def test_create_appointment_fails_if_datetime_in_the_future_but_not_on_the_hour(
        self, appointment_dict: dict[str, Any]
    ):
        """
        Test failure to create an appointment with a future, off-hour work time.
        """
        test_util = AppointmentToolsTestUtil()
        test_util.fail_to_add_invalid_appointment(appointment_dict)

    @given(appointment_dicts())
    def test_create_appointment_duplicate_time_fails(self, appointment_dict: dict[str, Any]):
        """Test that creating two appointments at the same time fails"""
        test_util = AppointmentToolsTestUtil()

        # First appointment should succeed
        test_util.successfully_add_valid_appointment(appointment_dict)

        # Second appointment at same time should fail
        test_util.fail_to_add_invalid_appointment(appointment_dict)

    @given(appointment_dicts())
    def test_cancel_appointment_succeeds_if_it_exists(self, appointment_dict: dict[str, Any]):
        """Test canceling an existing appointment"""
        test_util = AppointmentToolsTestUtil()
        appointment = test_util.successfully_add_valid_appointment(appointment_dict)
        id = appointment["id"]

        before_count = get_appointments_count.run({})
        success, msg = test_util.capture_output(cancel_appointment, {"id": id})
        after_count = get_appointments_count.run({})
        assert success, msg
        assert "" != msg
        assert before_count - 1 == after_count
        appt = get_appointment_by_id.run({"id": id})
        assert appt and appt.get("status") == "cancelled"

    @given(st.uuids())
    def test_cancel_nonexistent_appointment_fails(self, uuid):
        """Test that canceling a non-existent appointment fails"""
        test_util = AppointmentToolsTestUtil()
        before_count = get_appointments_count.run({})
        success, msg = test_util.capture_output(cancel_appointment, {"id": str(uuid)})
        assert not success, msg
        assert "" != msg
        after_count = get_appointments_count.run({})
        assert before_count == after_count

    @given(appointment_dicts(), appointment_future_work_datetimes())
    def test_change_appointment_successful_if_it_exists(
        self, appointment_dict: dict[str, Any], new_date_time: datetime
    ):
        """
        Test changing an appointment to a new time.
        There is a slight chance the randomly generated new_date_time
        will equal the existing datetime, but we allow this.
        """
        test_util = AppointmentToolsTestUtil()
        appointment = test_util.successfully_add_valid_appointment(appointment_dict)
        if appointment["appointment_date_time"] == new_date_time:
            match new_date_time.hour:
                case 16:
                    new_date_time = new_date_time - timedelta(hours=1)
                case _:
                    new_date_time = new_date_time + timedelta(hours=1)

        id = appointment["id"]
        success, msg = test_util.capture_output(
            change_appointment, {"id": id, "new_date_time": new_date_time.isoformat()}
        )
        assert success, msg
        updated = get_appointment_by_id.run({"id": id})
        test_util.result_expected(
            appointment_dict,
            updated,
            appointment_date_time=new_date_time,
            changed_at=new_date_time,
        )

    @given(appointment_dicts_lists())
    def test_get_appointments_with_no_filters_returns_all_appointments(self, appointment_dicts: list[dict[str, Any]]):
        """Test that appointments persist across tool instances"""
        test_util = AppointmentToolsTestUtil()
        ids = []
        for d in appointment_dicts:
            appointment = test_util.successfully_add_valid_appointment(d, all=appointment_dicts)
            ids.append(appointment["id"])

        appointments = get_appointments.run({})
        test_util.results_list_expected(appointment_dicts, appointments)

    @given(appointment_dicts_lists().filter(lambda lst: len(lst) > 0))
    def test_get_appointments_with_patient_name_filter_returns_appointments_for_that_patient(
        self, appointment_dicts: list[dict[str, Any]]
    ):
        """Test that appointments persist across tool instances"""
        test_util = AppointmentToolsTestUtil()
        ids = []
        for d in appointment_dicts:
            appointment = test_util.successfully_add_valid_appointment(d, all=appointment_dicts)
            ids.append(appointment["id"])

        patient_name = appointment_dicts[0]["patient_name"]
        expected_list = list(filter(lambda a: a["patient_name"] == patient_name, get_appointments.run({})))
        appointments = get_appointments.run({"patient_name": patient_name})
        test_util.results_list_expected(expected_list, appointments)

    @given(appointment_dicts_lists().filter(lambda lst: len(lst) > 0))
    def test_get_appointments_with_date_time_lower_bound_returns_appointments_later_than_that_date_time(
        self, appointment_dicts: list[dict[str, Any]]
    ):
        """Test that appointments persist across tool instances"""
        test_util = AppointmentToolsTestUtil()
        ids = []
        for d in appointment_dicts:
            appointment = test_util.successfully_add_valid_appointment(d, all=appointment_dicts)
            ids.append(appointment["id"])

        # Pick an entry in the middle:
        i = int(len(appointment_dicts) / 2)
        date_time = appointment_dicts[i]["appointment_date_time"]
        expected_list = list(
            filter(
                lambda a: a["appointment_date_time"] >= date_time,
                get_appointments.run({}),
            )
        )
        appointments = get_appointments.run({"after_date_time": date_time.isoformat()})
        test_util.results_list_expected(expected_list, appointments)

    @given(appointment_dicts_lists())
    def test_get_appointments_count_returns_the_number_of_appointments(self, appointment_dicts: list[dict[str, Any]]):
        test_util = AppointmentToolsTestUtil()
        ids = []
        for d in appointment_dicts:
            appointment = test_util.successfully_add_valid_appointment(d, all=appointment_dicts)
            ids.append(appointment["id"])
        actual_count = get_appointments_count.run({})
        assert len(appointment_dicts) == actual_count

    @given(appointment_dicts())
    def test_get_appointment_by_id_returns_nonempty_dict_if_it_exists(self, appointment_dict: dict[str, Any]):
        test_util = AppointmentToolsTestUtil()
        appointment2 = test_util.successfully_add_valid_appointment(appointment_dict)
        appointment = get_appointment_by_id.run({"id": appointment2["id"]})
        test_util.result_expected(appointment_dict, appointment)

    @given(appointment_dicts())
    def test_get_appointment_by_id_returns_empty_dict_if_key_does_not_exist(self, appointment_dict: dict[str, Any]):
        test_util = AppointmentToolsTestUtil()
        appointment2 = test_util.successfully_add_valid_appointment(appointment_dict)
        appointment = get_appointment_by_id.run({"id": appointment2["id"] + "bad"})
        assert {} == appointment

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_nonempty_id_if_match_exists(
        self, appointment_dict: dict[str, Any]
    ):
        test_util = AppointmentToolsTestUtil()
        appointment2 = test_util.successfully_add_valid_appointment(appointment_dict)
        id = get_appointment_id_for_name_and_date_time.run(
            {
                "patient_name": appointment_dict["patient_name"],
                "appointment_date_time": appointment_dict["appointment_date_time"].isoformat(),
            }
        )
        assert appointment2["id"] == id

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_empty_id_if_match_does_not_exist(
        self, appointment_dict: dict[str, Any]
    ):
        test_util = AppointmentToolsTestUtil()
        appointment = test_util.successfully_add_valid_appointment(appointment_dict)
        name = appointment["patient_name"]
        dt = appointment["appointment_date_time"]

        id = get_appointment_id_for_name_and_date_time.run(
            {"patient_name": name + "bad", "appointment_date_time": dt.isoformat()}
        )
        assert "" == id, f"{name+'bad'}, {appointment_dict}"

        bad_dt = dt + timedelta(seconds=10)
        id = get_appointment_id_for_name_and_date_time.run(
            {"patient_name": name, "appointment_date_time": bad_dt.isoformat()}
        )
        assert "" == id, f"{bad_dt}, {appointment_dict}"

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_matching_values(self, appointment_dict: dict[str, Any]):
        """Test that get_appointment returns existing appointments."""
        test_util = AppointmentToolsTestUtil()
        appointment = test_util.successfully_add_valid_appointment(appointment_dict)
        expected_id = appointment["id"]
        name = appointment["patient_name"]
        dt = appointment["appointment_date_time"]
        id = test_util.tool.get_appointment_id_for_name_and_date_time(name, dt)
        assert expected_id == id

    @given(appointment_dicts())
    def test_get_appointment_id_for_name_and_date_time_returns_empty_for_nonmatching_values(
        self, appointment_dict: dict[str, Any]
    ):
        """Test that get_appointment returns existing appointments."""
        test_util = AppointmentToolsTestUtil()
        appointment = test_util.successfully_add_valid_appointment(appointment_dict)
        name = appointment["patient_name"]
        dt = appointment["appointment_date_time"]
        id1 = test_util.tool.get_appointment_id_for_name_and_date_time(name + "bad", dt)
        assert "" == id1
        id2 = test_util.tool.get_appointment_id_for_name_and_date_time(name, dt + timedelta(seconds=10))
        assert "" == id2

    def test_get_appointment_id_for_name_and_date_time_raises_ValueError_for_invalid_name_or_date_time(self):
        paramss = [
            ["", datetime.now().isoformat()],
            ["John Doe", ""],
        ]
        for params in paramss:
            try:
                d = {
                    "patient_name": params[0],
                    "appointment_date_time": params[1],
                }
                get_appointment_id_for_name_and_date_time.run(d)
                assert False, f"ValueError not thrown for d = {d}"
            except ValueError:
                pass

    def _add_apmts(self, appointment_dicts: list[dict[str, Any]]) -> tuple[AppointmentToolsTestUtil, list[str]]:
        test_util = AppointmentToolsTestUtil()
        assert 0 == len(test_util.tool.get_resources())
        assert 0 == get_appointments_count.run({})
        ids = []
        date_times = [d["appointment_date_time"] for d in appointment_dicts]
        date_times_set = set(date_times)
        assert len(date_times) == len(date_times_set)
        for d in appointment_dicts:
            appointment = test_util.successfully_add_valid_appointment(d, all=appointment_dicts)
            ids.append(appointment["id"])
        assert len(appointment_dicts) == len(test_util.tool.get_resources())
        return test_util, ids

    @given(appointment_dicts_lists())
    def test_appointments_persist_across_instances(self, appointment_dicts: list[dict[str, Any]]):
        """Test that appointments persist across tool instances"""
        test_util, ids = self._add_apmts(appointment_dicts)

        # Create new instance and verify appointments exist.
        old_tool = test_util.tool
        first_appointments = old_tool.get_appointments()

        # Create new instance and verify appointments exist.
        new_tool = test_util.make_manager()
        assert old_tool is not new_tool
        second_appointments = new_tool.get_appointments()

        # Check that they both have the same list of appointments.
        test_util.check_appointments_lists(first_appointments, second_appointments)

    @given(appointment_dicts_lists().filter(lambda lst: len(lst) > 0))
    def test_clear_erases_appointments(self, appointment_dicts: list[dict[str, Any]]):
        """Test that appointments persist across tool instances"""
        test_util, ids = self._add_apmts(appointment_dicts)
        test_util.clear()
        assert 0 == get_appointments_count.run({})

    def test_get_appointment_manager_instantiates_a_manager(self):
        test_util = AppointmentToolsTestUtil()
        test_util.check_file()

    def test_get_appointment_manager_instantiates_a_new_manager_when_make_new_is_true(self):
        test_util = AppointmentToolsTestUtil()
        original_tool = test_util.tool
        new_tool = get_appointment_manager(
            test_util.tool.storage.storage_path, logger=test_util.tool.logger, make_new=True
        )
        assert original_tool is not new_tool
        test_util.tool = new_tool  # Update the utility!!

    def test_get_appointment_manager_does_not_instantiate_a_new_manager_even_with_diff_arguments(self):
        test_util = AppointmentToolsTestUtil()
        original_tool = test_util.tool
        same_tool = get_appointment_manager("toss.jsonl", logger=None)
        assert original_tool is same_tool

    def test_get_appointment_manager_does_not_instantiate_a_new_manager_with_no_arguments(self):
        test_util = AppointmentToolsTestUtil()
        original_tool = test_util.tool
        same_tool = get_appointment_manager()
        assert original_tool is same_tool

    def test_initialization_creates_file(self):
        """Test that initialization creates the appointments file if it doesn't exist"""
        test_util = AppointmentToolsTestUtil()
        test_util.check_file()
