"""
Test utilities, e.g., strategy generators for Hypothesis.
"""
from hypothesis import given, strategies as st
from datetime import datetime, timedelta, date, time

one_day   = timedelta(days=1)
today     = date.today()
yesterday = today - one_day
tomorrow  = today + one_day

def is_work_hours(
    dt: datetime, 
    weekdays_only: bool           = True,
    start_hour_inclusive: int     = 8,
    end_hour_inclusive: int       = 17,
    holidays: set[tuple[int,int]] = set()) -> bool:
    """
    Returns True if the input datetime is falls within work hours,
    including if it is a weekday (when weekdays_only is True), the hours
    fall within start_hour_inclusive and end_hour_inclusive, and the date
    isn't a holiday.
    """
    if (dt.month, dt.day) in holidays:
        return False
    elif weekdays_only and dt.weekday() > 4:
        return False
    elif dt.hour < start_hour_inclusive or dt.hour > end_hour_inclusive:
        return False
    return True

def future_dates(
    date_strategy   = st.dates,
    min_value: date = date.min,
    max_value: date = date.max):
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
    if min_value < tomorrow:
        min_value = tomorrow
    if max_value < min_value:
        max_value = min_value
    return date_strategy(min_value = min_value, max_value = max_value)

def past_dates(
    date_strategy   = st.dates,
    min_value: date = date.min,
    max_value: date = date.max):
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
    if max_value > yesterday:
        max_value = yesterday
    if min_value > max_value:
        min_value = max_value
    return date_strategy(min_value = min_value, max_value = max_value)

def non_weekend_dates(
    date_strategy                 = future_dates,
    min_value: date               = date.min,
    max_value: date               = date.max,
    holidays: set[tuple[int,int]] = set()):
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
    def allowed(dt: date) -> bool:
        if dt.weekday() >= 5:
            return False
        if holidays and (dt.month, dt.day) in holidays:
            return False
        return True

    return date_strategy(min_value=min_value, max_value=max_value).filter(
        lambda dt: allowed(dt))

def weekend_dates(
    date_strategy                 = future_dates,
    min_value: date               = date.min,
    max_value: date               = date.max,
    holidays: set[tuple[int,int]] = set()):
    """
    A Hypothesis strategy for generating dates that fall on Saturday or Sunday.

    Args:

    - date_strategy: the strategy to use to generate candidate dates (defaults to future dates).
    - min_value: the earliest date. See the documentation for the passed-in date_strategy.
    - max_value: the latest date. See the documentation for the passed-in date_strategy.
    - holidays: A set of tuples with month-day integers that are holidays to exclude.

    Returns:

    A strategy for generating of valid weekend dates.
    """    
    def allowed(dt: date) -> bool:
        if dt.weekday() < 5:
            return False
        if holidays and (dt.month, dt.day) in holidays:
            return False
        return True

    return date_strategy(min_value=min_value, max_value=max_value).filter(
        lambda dt: allowed(dt))

def work_dates(
    date_strategy                 = future_dates,
    min_value: date               = date.min,
    max_value: date               = date.max,
    weekdays_only: bool           = True,
    holidays: set[tuple[int,int]] = set()):
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
    def allowed(dt: date) -> bool:
        if weekdays_only and dt.weekday() >= 5:
            return False
        if holidays and (dt.month, dt.day) in holidays:
            return False
        return True

    return date_strategy(min_value=min_value, max_value=max_value).filter(
        lambda dt: allowed(dt))

def work_hours(
    start_hour_inclusive: int = 8,
    end_hour_inclusive: int   = 17):
    """
    A Hypothesis strategy for generating valid work hours as integers between 0 and 23.

    Args:

    - start_hour_inclusive: The hour work starts; if < 0, 0 is used.
    - end_hour_inclusive: The hour work ends (or some other end-of-day limit, such as the last time slot for an appointment); if > 23, 23 is used.

    Returns:

    A strategy of integer hours.
    """
    if start_hour_inclusive < 0:
        start_hour_inclusive = 0
    if end_hour_inclusive > 23:
        end_hour_inclusive = 23
    return st.integers(min_value = start_hour_inclusive, max_value = end_hour_inclusive)

def non_work_hours(
    last_morning_hour_inclusive: int  = 7,
    first_evening_hour_inclusive: int = 18):
    """
    A Hypothesis strategy for generating hours outside of the work hours.

    Args:

    last_morning_hour_inclusive: Hours between 0 (midnight) and this value, inclusive, can be returned; reset to 0 if < 0.
    end_hour_inclusive:  Hours between this value and 23 (11 PM), inclusive, can be returned; reset to min_value if < min_value or 23 if > 23.

    Returns:

    A strategy of integer hours.
    """
    if last_morning_hour_inclusive < 0:
        last_morning_hour_inclusive = 0
    if first_evening_hour_inclusive > 23:
        first_evening_hour_inclusive = 23
    if first_evening_hour_inclusive < last_morning_hour_inclusive:
        first_evening_hour_inclusive = last_morning_hour_inclusive
    return st.one_of(
        st.integers(min_value = 0, max_value = last_morning_hour_inclusive),
        st.integers(min_value = first_evening_hour_inclusive, max_value = 23))

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

def date_hour_minute_datetimes(
    date_strategy,
    hour_strategy,
    minute_strategy,
    future: bool):
    """
    A Hypothesis strategy for generating future or datetimes, with the dates, hours, and minutes generated
    by the input strategies. This method could be called directly, but it is important to pass consistent
    date_strategy and future arguments (either both for the past or the future). Instead, try to use
    future_work_datetimes or past_work_datetimes, which are implemented with this method.

    Args:

    - date_strategy: for generating dates. If you pass a future date strategy, pass True for
      the future flag. If you pass a past date strategy, pass False for the future flag.
    - hour_strategy: for generating hours (defaults to work hours)
    - minute_strategy: for generating minutes (defaults to on the hour minutes - 0)
    - future: True if we should only allow the combined datetime to be >= datetime.now().
      False if only past datetimes (< datetime.now()) should be returned. (Note that == is 
      considered a future time.) This flag is useful because date_strategy can return today,
      and combined with the hour and minute, the resulting datetime could be outside the
      desired past or future constraint, contrary to goals of the date_strategy used.

    Returns:

    A strategy for datetime generation.
    """
    def tuple_to_datetime(t: tuple[date,int,int]) -> datetime:
        (dte, hour, minute) = t
        return datetime.combine(dte, time(hour, minute))
    def is_future_or_past(dt: datetime) -> bool:
        now = datetime.now()
        return dt >= now if future else dt < now
    return st.tuples(date_strategy(), hour_strategy(), minute_strategy()).map(
        lambda  t: tuple_to_datetime(t)).filter(
        lambda dt: is_future_or_past(dt))

def future_work_datetimes(
    date_strategy   = lambda: work_dates(date_strategy = future_dates),
    hour_strategy   = work_hours,
    minute_strategy = on_the_hour_minutes):
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
    return date_hour_minute_datetimes(
        date_strategy, hour_strategy, minute_strategy, True)

def past_work_datetimes(
    date_strategy   = lambda: work_dates(date_strategy = past_dates),
    hour_strategy   = work_hours,
    minute_strategy = on_the_hour_minutes):
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
    return date_hour_minute_datetimes(
        date_strategy, hour_strategy, minute_strategy, False)
