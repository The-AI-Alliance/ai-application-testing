"""
Unit tests for the appointment skills tool.
Uses Hypothesis.
"""
from hypothesis import given, strategies as st
import contextlib, io, json, logging, os, tempfile, unittest
from collections.abc import Iterator
from datetime import datetime, timedelta, date, time
from typing import Any, Callable
from langchain_core.tools.structured import StructuredTool

from apps.chatbot.skills.date_times.date_time_tools import (
    now,
    is_week_day,
    datetime_to_str,
    date_to_str,
    time_to_str,
    str_to_datetime,
    iso_format_str_to_datetime,
    friendly_date_time_formats,
    friendly_date_formats,
    friendly_time_formats,
    def_friendly_date_time_format,
    def_friendly_date_format,
    def_friendly_time_format,
)

from tests.common.hypothesis.datetimes import (
    is_work_hours,
    future_dates,
    past_dates,
    weekend_dates,
    non_weekend_dates,
    work_dates,
    work_hours,
    non_work_hours,
    on_the_hour_minutes,
    off_the_hour_minutes,
    future_work_datetimes,
    past_work_datetimes,
)

class TestDateTimeTools(unittest.TestCase):
    """
    Test cases for the _skills_ tools in `date_time_tools.py`.
    A few notes about unit tests for these tools. Although the tool definitions look
    like normal method definitions, the `@tool` annotation turns them into LangChain's
    `StructuredTools`. Hence, you don't invoke, e.g., `datetime_to_str` as follows:
    ```
    datetime_to_str(some_date_time, some_format)
    ```

    Instead, you invoke it as follows: 
    ```
    datetime_to_str.run({
        'a_date_time': some_date_time, 
        'output_format': some_format
    })
    ```

    Also, it appears the tool writes to `sys.stderr` sometimes, so we capture that output.
    """

    one_second = timedelta(seconds=1)

    def setUp(self):
        pass

    def tearDown(self):
        pass

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

    def test_now_returns_current_datetime(self):
        now_dt = now.run({})
        expected_dt = datetime.now()
        self.assertAlmostEqual(datetime.now(), now_dt, delta = TestDateTimeTools.one_second)

    @given(non_weekend_dates())
    def test_is_weekday_returns_true_for_week_days(self, week_day):
        self.assertTrue(is_week_day.run({'a_date_time': week_day}))

    @given(weekend_dates())
    def test_is_weekday_returns_false_for_weekend_days(self, weekend_day):
        self.assertFalse(is_week_day.run({'a_date_time': weekend_day}))

    @given(st.datetimes())
    def test_datetime_to_str_returns_properly_formatted_string_based_on_desired_format(self, dt):
        for fmt in friendly_date_time_formats:
            expected = dt.strftime(fmt)
            actual = datetime_to_str.run({'a_date_time': dt, 'output_format': fmt})
            self.assertEqual(expected, actual, f"dt: {dt}, fmt: {fmt}")

    @given(st.datetimes())
    def test_datetime_to_str_uses_a_default_format(self, dt):
        expected = dt.strftime(def_friendly_date_time_format)
        actual = datetime_to_str.run({'a_date_time': dt})
        self.assertEqual(expected, actual, f"dt: {dt}, fmt: {def_friendly_date_time_format}")


    @given(st.dates())
    def test_date_to_str_returns_properly_formatted_string_based_on_desired_format(self, d):
        for fmt in friendly_date_formats:
            expected = d.strftime(fmt)
            actual = date_to_str.run({'a_date': d, 'output_format': fmt})
            self.assertEqual(expected, actual, f"d: {d}, fmt: {fmt}")

    @given(st.dates())
    def test_date_to_str_uses_a_default_format(self, d):
        expected = d.strftime(def_friendly_date_format)
        actual = date_to_str.run({'a_date': d})
        self.assertEqual(expected, actual, f"d: {d}, fmt: {def_friendly_date_format}")


    @given(st.times())
    def test_time_to_str_returns_properly_formatted_string_based_on_desired_format(self, t):
        for fmt in friendly_time_formats:
            expected = t.strftime(fmt)
            actual = time_to_str.run({'a_time': t, 'output_format': fmt})
            self.assertEqual(expected, actual, f"t: {t}, fmt: {fmt}")

    @given(st.times())
    def test_time_to_str_uses_a_default_format(self, t):
        expected = t.strftime(def_friendly_time_format)
        actual = time_to_str.run({'a_time': t})
        self.assertEqual(expected, actual, f"t: {t}, fmt: {def_friendly_time_format}")


if __name__ == '__main__':
    unittest.main()
