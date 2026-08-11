"""
Unit tests for the common "date_time_utils" module.
Uses Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

from datetime import datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from common.date_time_utils import (
    add_timezone,
    datetimes_approx_equal,
    friendly_date_formats,
    friendly_date_time_formats,
    is_week_day,
    now,
    one_second,
    string_to_date,
    string_to_datetime,
)
from tests.common.hypothesis.datetimes import (
    check_date_to_str_and_back,
    check_datetime_to_str_and_back,
    dates_2000,
    local_datetimes_2000,
    non_weekend_dates,
    weekend_dates,
    year_2000,
)

# pylint: disable=unused-variable,missing-function-docstring


@given(local_datetimes_2000(), st.lists(st.integers(min_value=-120, max_value=120), min_size=0, max_size=10))
def test_datetimes_approx_equal_returns_true_and_empty_string_if_datetimes_approx_equal(dt, ns):
    for n in ns:
        delta = timedelta(seconds=n)
        dt2 = dt + delta
        eql, msg = datetimes_approx_equal(dt, dt2, delta)
        assert eql
        assert msg == ""


@given(local_datetimes_2000(), st.lists(st.integers(min_value=1, max_value=4), min_size=0, max_size=3))
def test_datetimes_approx_equal_returns_false_and_non_empty_string_if_not_datetimes_approx_equal(dt, ns):
    for n in ns:
        delta = timedelta(seconds=n)
        delta1 = timedelta(seconds=n + 1)
        dtp = dt + delta1
        eqlp, msgp = datetimes_approx_equal(dt, dtp, delta)
        assert not eqlp
        assert msgp != ""
        dtm = dt - delta1
        eqlm, msgm = datetimes_approx_equal(dt, dtm, delta)
        assert not eqlm
        assert msgm != ""


def test_now_returns_current_datetime():
    now_dt = now()
    expected_dt = datetime.now().astimezone()
    is_eql, msg = datetimes_approx_equal(expected_dt, now_dt, one_second)
    assert is_eql, msg


@given(local_datetimes_2000())
def test_add_timezone_does_not_modify_datetimes_with_timezones_already(dt: datetime):
    dt2 = add_timezone(dt)
    assert dt2 == dt


@given(non_weekend_dates(min_value=year_2000.date()))
def test_is_weekday_returns_true_for_week_days(week_day):
    assert is_week_day(week_day)


@given(weekend_dates(min_value=year_2000.date()))
def test_is_weekday_returns_false_for_weekend_days(weekend_day):
    assert not is_week_day(weekend_day)


@given(local_datetimes_2000(), st.sampled_from(friendly_date_time_formats))
def test_string_to_datetime_can_parse_friendly_formatted_datetime_strings(dt, fmt):
    check_datetime_to_str_and_back(dt, fmt, string_to_datetime)


@given(local_datetimes_2000())
def test_string_to_datetime_can_parse_iso_formatted_strings(dt):
    dt_iso = dt.isoformat()
    actual, error = string_to_datetime(dt_iso)
    assert dt == actual, f"dt: {dt}"
    assert "" == error


def test_string_to_datetime_returns_an_error_string_for_invalid_date_time_strings():
    for s in ["", "bad", "hello!"]:
        actual, error = string_to_datetime(s)
        assert not actual
        assert "" != error


@given(dates_2000())
def test_string_to_date_can_parse_friendly_formatted_date_strings(d):
    for fmt in friendly_date_formats:
        check_date_to_str_and_back(d, fmt, string_to_date)


@given(dates_2000())
def test_string_to_date_can_parse_iso_formatted_strings(d):
    d_iso = d.isoformat()
    actual, error = string_to_date(d_iso)
    assert d == actual, f"d: {d}"
    assert "" == error
