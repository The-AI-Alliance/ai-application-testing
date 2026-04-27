"""
Test utilities, e.g., strategy generators for appointments.
"""
from hypothesis import given, strategies as st

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
    person_name_parts,
    person_names,
)

from apps.chatbot.tools.appointment_manager import AppointmentManager

def appointment_work_hours():
    return work_hours(end_hour_inclusive = 16)

def appointment_non_work_hours():
    return non_work_hours(first_evening_hour_inclusive = 17)

def appointment_future_work_datetimes(
    minute_strategy = on_the_hour_minutes):
    return future_work_datetimes(
        date_strategy = lambda: work_dates(
            date_strategy = future_dates,
            holidays = AppointmentManager.USA_HOLIDAYS),
        hour_strategy = appointment_work_hours,
        minute_strategy = minute_strategy)

def appointment_future_non_work_datetimes(
    minute_strategy = on_the_hour_minutes):
    return future_work_datetimes(
        date_strategy = lambda: work_dates(
            date_strategy = future_dates,
            holidays = AppointmentManager.USA_HOLIDAYS),
        hour_strategy = appointment_non_work_hours,
        minute_strategy = minute_strategy)

def appointment_dicts(
    datetime_strategy = appointment_future_work_datetimes,
    patient_name_strategy = person_names,
    reason_strategy = st.text):
    return st.tuples(datetime_strategy(), patient_name_strategy(), reason_strategy()).map(lambda t:
        AppointmentManager.make_appointment_dict(
            appointment_date_time = t[0],
            patient_name = t[1], 
            reason = t[2],
            status = 'scheduled'))

def appointment_dicts_lists(
    datetime_strategy = appointment_future_work_datetimes,
    patient_name_strategy = person_names,
    reason_strategy = st.text):
    return st.lists(
        appointment_dicts(
            datetime_strategy = datetime_strategy,
            patient_name_strategy = patient_name_strategy,
            reason_strategy = reason_strategy),
        unique_by=lambda dct: dct['appointment_date_time'])
