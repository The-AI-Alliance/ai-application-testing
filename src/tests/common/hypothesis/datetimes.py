"""
Test utilities, e.g., strategy generators for Hypothesis.
"""

from collections.abc import Callable
from collections.abc import Set as AbstractSet
from datetime import date, datetime, time

from hypothesis import strategies as st

from common.date_time_utils import (
    datetimes_approx_equal,
    def_end_hour_inclusive,
    def_start_hour_inclusive,
    is_week_day,
    is_weekend,
    local_datetime_max,
    local_datetime_min,
    local_timezone,
    now,
    one_second,
    tomorrow,
    yesterday,
)

# pylint: disable=unused-variable,missing-function-docstring,fixme

year_2000 = datetime(year=2000, month=1, day=1, tzinfo=local_timezone)

default_work_start_time = time(hour=def_start_hour_inclusive, minute=0)
default_work_end_time = time(hour=def_end_hour_inclusive, minute=0)


def is_holiday(
    d: date,
    holidays: AbstractSet[tuple[int, int]] | None = None,
):
    """
    Is the month and day in an optional list of holidays.

    Args:

    - date: Ahe date to check.
    - holidays: An optional set of tuples with month-day integers that are holidays.

    Returns:

    True if a non-empty set of holidays is provided and the date falls on one of them, or False otherwise.
    """
    return holidays and (d.month, d.day) in holidays


def local_datetimes(
    min_value: datetime = local_datetime_min, max_value: datetime = local_datetime_max
) -> st.SearchStrategy[datetime]:
    # ty won't type check the following. I think the issue is that
    # st.just(local_timezone) types as SearchStrategy[tzinfo | None] and the
    # override declaration of st.datetimes that type-matches the *_value arguments
    # also expects SearchStrategy[tzinfo] for timezones.
    return st.datetimes(
        min_value=min_value, max_value=max_value, timezones=st.just(local_timezone)
    )  # ty: ignore[no-matching-overload]


def local_datetimes_2000(max_value: datetime = local_datetime_max):
    return local_datetimes(min_value=year_2000, max_value=max_value)


def dates_2000(max_value: date = date.max):
    return st.dates(min_value=year_2000.date(), max_value=max_value)


def future_dates(date_strategy=st.dates, min_value: date = date.min, max_value: date = date.max):
    """
    A Hypothesis strategy for generating dates in the future, using the
    input date_strategy (default st.dates) and min_value and max_value.

    We don't return today's date, because when constructing datetimes, we
    have to handle rejecting today's date when the hour and minutes are
    actually in the past. This often results in too much filtering of examples.

    Args:

    - date_strategy: the "generic" strategy to use to generate dates.
    - min_value: the earliest date.
      If the value is < tomorrow, then tomorrow is used.
    - max_value: the latest date.
      If the value is < min_value (after adjusting the min_value as required),
      then min_value is used.

    Returns:

    A strategy for generating dates that occur in the future, possibly
    including today, between the min_value and max_value, inclusive.
    """
    min_value = max(min_value, tomorrow)
    max_value = max(max_value, min_value)
    return date_strategy(min_value=min_value, max_value=max_value)


def past_dates(date_strategy=st.dates, min_value: date = date.min, max_value: date = date.max):
    """
    A Hypothesis strategy for generating dates in the past, meaning
    yesterday or earlier, using the input date_strategy (default st.dates)
    and min_value and max_value.

    We don't return today's date, because when constructing datetimes, we
    have to handle rejecting today's date when the hour and minutes are
    actually in the future. This often results in too much filtering of examples.

    Args:

    - date_strategy: the "generic" strategy to use to generate dates.
    - min_value: the earliest date.
      If the value is > max_value (after adjusting it as discussed next),
      then max_value is used.
    - max_value: the latest date.
      If the value is > yesterday, then yesterday is used.

    Returns:

    A strategy for generating dates that occur in the past, possibly
    including today, between the min_value and max_value, inclusive.
    """
    max_value = min(max_value, yesterday)
    min_value = min(min_value, max_value)
    return date_strategy(min_value=min_value, max_value=max_value)


def non_weekend_dates(
    date_strategy=future_dates,
    min_value: date = date.min,
    max_value: date = date.max,
    holidays: set[tuple[int, int]] | None = None,
):
    """
    A Hypothesis strategy for generating dates that fall on Monday through Friday.

    Args:

    - date_strategy: the strategy to use to generate candidate dates (defaults to future dates).
    - min_value: the earliest date. See the documentation for the passed-in date_strategy.
    - max_value: the latest date. See the documentation for the passed-in date_strategy.
    - holidays: A set of tuples with month-day integers that are holidays to exclude.

    Returns:

    A strategy for generating of valid week dates.
    """

    def allowed(d: date) -> bool:
        return is_week_day(d) and not is_holiday(d, holidays)

    return date_strategy(min_value=min_value, max_value=max_value).filter(allowed)


def weekend_dates(
    date_strategy=future_dates,
    min_value: date = date.min,
    max_value: date = date.max,
    holidays: AbstractSet[tuple[int, int]] | None = None,
):
    """
    A Hypothesis strategy for generating dates that fall on Saturday or Sunday, but
    aren't optional holidays.

    Args:

    - date_strategy: the strategy to use to generate candidate dates (defaults to future dates).
    - min_value: the earliest date. See the documentation for the passed-in date_strategy.
    - max_value: the latest date. See the documentation for the passed-in date_strategy.
    - holidays: An optional set of tuples with month-day integers that are holidays to exclude.

    Returns:

    A strategy for generating valid weekend dates, excluding optional holidays.
    """

    def allowed(d: date) -> bool:
        return is_weekend(d) and not is_holiday(d, holidays)

    return date_strategy(min_value=min_value, max_value=max_value).filter(allowed)


def work_dates(
    date_strategy=future_dates,
    min_value: date = date.min,
    max_value: date = date.max,
    weekdays_only: bool = True,
    holidays: AbstractSet[tuple[int, int]] | None = None,
):
    """
    A Hypothesis strategy for generating work dates.

    Args:

    - date_strategy: the strategy to use to generate candidate dates (defaults to future dates).
    - min_value: the earliest date. See the documentation for the passed-in date_strategy.
    - max_value: the latest date. See the documentation for the passed-in date_strategy.
    - weekdays_only: Only return dates that fall on M-F.
    - holidays: A set of tuples with month-day integers that are holidays to exclude.

    Returns:

    A strategy for generating of valid work dates.
    """

    def allowed(d: date) -> bool:
        if weekdays_only and not is_week_day(d):
            return False
        return not is_holiday(d, holidays)

    return date_strategy(min_value=min_value, max_value=max_value).filter(allowed)


def work_times(
    time_strategy=st.times,
    min_value: time = default_work_start_time,
    max_value: time = default_work_end_time,
):
    """
    A Hypothesis strategy for generating work times.

    Args:

    - time_strategy: the strategy to use to generate candidate times.
    - min_value: the earliest time of day. See the documentation for the passed-in time_strategy.
    - max_value: the latest time of the day. See the documentation for the passed-in time_strategy.

    Returns:

    A strategy for generating of valid work times.
    """
    return time_strategy(min_value=min_value, max_value=max_value)


def non_work_times(
    time_strategy=st.times,
    latest_morning_value: time = default_work_start_time,
    earliest_evening_value: time = default_work_end_time,
):
    """
    A Hypothesis strategy for generating times outside of work hours.

    Args:

    - time_strategy: the strategy to use to generate candidate times.
    - latest_morning_value: the latest time in the morning before which are considered non-work times.
    - earliest_evening_value: the earliest time in the afternoon or evening after which are considered non-work times.

    Returns:

    A strategy for generating of valid work times.
    """
    return st.one_of(
        time_strategy(min_value=time.min, max_value=latest_morning_value),
        time_strategy(min_value=earliest_evening_value, max_value=time.max),
    )


# TODO: Phase out these generators, replacing them with work_times, etc.
# This will also require changes to how appointments are implemented and tested,
# to work with times instead of handling hours and minutes specially.
def work_hours(start_hour_inclusive: int = 8, end_hour_inclusive: int = 17):
    """
    A Hypothesis strategy for generating valid work hours as integers between 0 and 23.

    Args:

    - start_hour_inclusive: The hour work starts; if < 0, 0 is used.
    - end_hour_inclusive: The hour work ends (or some other end-of-day limit, such as the last time slot for an appointment); if > 23, 23 is used.

    Returns:

    A strategy of integer hours.
    """
    start_hour_inclusive = max(start_hour_inclusive, 0)
    end_hour_inclusive = min(end_hour_inclusive, 23)
    return st.integers(min_value=start_hour_inclusive, max_value=end_hour_inclusive)


def non_work_hours(last_morning_hour_inclusive: int = 7, first_evening_hour_inclusive: int = 18):
    """
    A Hypothesis strategy for generating hours outside of the work hours.

    Args:

    last_morning_hour_inclusive: Hours between 0 (midnight) and this value, inclusive, can be returned; reset to 0 if < 0.
    end_hour_inclusive:  Hours between this value and 23 (11 PM), inclusive, can be returned; reset to min_value if < min_value or 23 if > 23.

    Returns:

    A strategy of integer hours.
    """
    last_morning_hour_inclusive = max(last_morning_hour_inclusive, 0)
    first_evening_hour_inclusive = min(first_evening_hour_inclusive, 23)
    first_evening_hour_inclusive = max(first_evening_hour_inclusive, last_morning_hour_inclusive)
    return st.one_of(
        st.integers(min_value=0, max_value=last_morning_hour_inclusive),
        st.integers(min_value=first_evening_hour_inclusive, max_value=23),
    )


def on_the_hour_minutes():
    """
    A Hypothesis strategy for generating minutes that always returns 0 minutes.

    Returns:

    A strategy of integer minutes.
    """
    return st.just(0)


def off_the_hour_minutes():
    """
    A Hypothesis strategy for generating minutes that always returns
    a minutes value between 1 and 59, but never 0.

    Returns:

    A strategy of integer minutes.
    """
    return st.integers(min_value=1, max_value=59)


def date_hour_minute_datetimes(date_strategy, hour_strategy, minute_strategy, future: bool):
    """
    A Hypothesis strategy for generating future or past datetimes, with the dates, hours, and minutes generated
    by the input strategies. This method could be called directly, but it is important to pass consistent
    date_strategy and future arguments (either both for the past or the future). Instead, try to use
    future_work_datetimes or past_work_datetimes, which are implemented with this method.

    Args:

    - date_strategy: for generating dates. If you pass a future date strategy, pass True for
      the future flag. If you pass a past date strategy, pass False for the future flag.
    - hour_strategy: for generating hours (defaults to work hours)
    - minute_strategy: for generating minutes (defaults to on the hour minutes - 0)
    - future: True if we should only allow the combined `datetime` to be `>= datetime.now(local_timezone)`.
      False if only past datetimes (`< datetime.now(local_timezone)`) should be returned.
      (Note that == is considered a future time.) This flag is useful because date_strategy
      can return today, and combined with the hour and minute, the resulting datetime could
      be outside the desired past or future constraint, contrary to goals of the date_strategy used.

    Returns:

    A strategy for datetime generation with the local timezone.
    """

    def tuple_to_datetime(t: tuple[date, int, int]) -> datetime:
        dte, hour, minute = t
        return datetime.combine(dte, time(hour, minute)).astimezone()

    def is_future_or_past(dt: datetime) -> bool:
        right_now = now()
        return dt >= right_now if future else dt < right_now

    return (
        st.tuples(date_strategy(), hour_strategy(), minute_strategy()).map(tuple_to_datetime).filter(is_future_or_past)
    )


def future_work_datetimes(
    date_strategy=lambda: work_dates(date_strategy=future_dates),
    hour_strategy=work_hours,
    minute_strategy=on_the_hour_minutes,
):
    """
    A Hypothesis strategy for generating future datetimes, with the dates, hours, and minutes generated
    by the input strategies.

    Args:

    - date_strategy: for generating dates. Defaults to future work dates.
      DO NOT pass a past dates strategy, as the filtering logic will fail for today's date!
    - hour_strategy: for generating hours (defaults to work hours)
    - minute_strategy: for generating minutes (defaults to on the hour minutes - 0)

    Returns:

    A strategy for future datetime generation.
    """
    return date_hour_minute_datetimes(date_strategy, hour_strategy, minute_strategy, True)


def past_work_datetimes(
    date_strategy=lambda: work_dates(date_strategy=past_dates),
    hour_strategy=work_hours,
    minute_strategy=on_the_hour_minutes,
):
    """
    A Hypothesis strategy for generating past datetimes, with the dates, hours, and minutes generated
    by the input strategies.

    Args:

    - date_strategy: for generating dates. Defaults to past work dates.
      DO NOT pass a future dates strategy, as the filtering logic will fail for today's date!
    - hour_strategy: for generating hours (defaults to work hours)
    - minute_strategy: for generating minutes (defaults to on the hour minutes - 0)

    Returns:

    A strategy for past datetime generation.
    """
    return date_hour_minute_datetimes(date_strategy, hour_strategy, minute_strategy, False)


def check_datetime_to_str_and_back(
    dt: datetime,
    datetime_format: str,
    str_to_datetime: Callable[[str, str], tuple[datetime | None, str]],
):
    """
    Helper function for several tests that, starting with a datetime,
    first convert it to a string, then parse the string with a specified
    format, and verify the result is the expected datetime. It must
    handle the case where the format might remove information, e.g., just
    return the date and not the time part.
    """
    assert dt.tzinfo == local_timezone
    dt_str = dt.strftime(datetime_format)
    actual, error = str_to_datetime(dt_str, datetime_format)
    assert (
        actual
    ), f'Failed to convert "{dt_str}" with format "{datetime_format}", original datetime "{dt}". Error: {error}'
    assert datetimes_approx_equal(
        dt, actual, one_second
    ), f"dt: {dt}, dt_str: {dt_str}, actual: {actual}, datetime_format: {datetime_format}"

    # We actually need to compare strings, not dts, because a returned datetime might have "missing"
    # hours, minutes, seconds, etc., depending on fmt.
    actual_str = actual.strftime(datetime_format)
    assert (
        dt_str == actual_str
    ), f"original datetime: {dt}, dt_str: {dt_str}, actual: {actual}, actual_str: {actual_str}, datetime_format: {datetime_format}"
    assert not error


def check_date_to_str_and_back(
    d: date,
    date_format: str,
    str_to_date: Callable[[str, str], tuple[date | None, str]],
):
    """
    Helper function for several tests that, starting with a date,
    first convert it to a string, then parse the string with a specified
    format, and verify the result is the expected date. It must
    handle the case where the format might remove some information.
    """
    d_str = d.strftime(date_format)
    actual, error = str_to_date(d_str, date_format)
    assert actual, f'Failed to convert "{d_str}" with format "{date_format}", original date "{d}". Error: {error}'

    # We actually need to compare strings, not ds, because a returned datetime might have "missing"
    # hours, minutes, seconds, etc., depending on fmt.
    actual_str = actual.strftime(date_format)
    assert (
        d_str == actual_str
    ), f"original date: {d}, d_str: {d_str}, actual: {actual}, actual_str: {actual_str}, date_format: {date_format}"
    assert not error
