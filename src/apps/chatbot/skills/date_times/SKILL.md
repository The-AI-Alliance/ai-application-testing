---
name: date_time
description: Use this skill to determine the current date and time.
---

# Date Time Skill

This skill provides access to date-time facilities.

## When to Use This Skill

Use this skill when you need to know the current date and time or any part of that information, because:
- A patient refers to a day of the week, such as "next Tuesday", "this Tuesday", and "last Tuesday", and you need to determine which date is the Tuesday the patient is referring to.
- A patient refers to a month and day, but not the year, and you need to determine which year.

## Available Tools

### now
Determine the current year, month, day, hour, minute, second, and microsecond, returned as a Python `datetime.datetime` object.

**Parameters:**
_None_

**Returns:**
A Python `datetime.datetime` object with the current date and time.

### is_week_day
Does the input `datetime.datetime` object correspond to a week day (Monday through Friday) or not?

**Parameters:**
- `a_date_time`: A Python `datetime.datetime` object.

**Returns:**
`True` if the input `a_date_time` corresponds to a weekday (Monday through Friday) or `False`, otherwise.

### datetime_to_str
Format a `datetime.datetime` as a string.

**Parameters:**
- `a_date_time`: A Python `datetime.datetime` object.
- `output_format`: An optional format `str` to use to format a string from the input `a_date_time`. If not provided, the default value of `"%A, %B %d %Y, at %I:%m %p"` is used, corresponding to "day of the week, month day year, at hour time:minutes AM/PM", where the "hour" is based on a 12-hour clock.

**Returns:**
A string representing the input `a_date_time`, formatted using the `output_format` string.

### date_to_str

**Parameters:**
- `a_date`: A Python `datetime.date` object.
- `output_format`: An optional format `str` to use to format a string from the date part of the input `a_date_time`. If not provided, the default value of `"%A, %B %d %Y"` is used, corresponding to "day of the week, month day year".

**Returns:**
A string representing the input `datetime.date` object, formatted using the `output_format` string.

### time_to_str

**Parameters:**
- `a_time`: A Python `datetime.time` object.
- `output_format`: An optional format `str` to use to format a string from the time part of the input `a_time`. If not provided, the default value of `"%I:%m %p"` is used, corresponding to "hour time:minutes AM/PM", where the "hour" is based on a 12-hour clock.

**Returns:**
A string representing the input `datetime.time` object, formatted using the `output_format` string.

### str_to_datetime
Parse the input string using the specified format and return the corresponding Python `datetime.datetime` object.

**Parameters:**
- `a_date_time_str`: A string representing a date-time.
- `input_format`: An optional format `str` to use to parse the input `a_date_time_str` string to create and return Python `datetime.datetime` object. If not provided, different formats are tried, including `"%A, %B %d %Y, at %I:%m %p"`, corresponding to "day of the week, month day year, at hour time:minutes AM/PM", where the "hour" is based on a 12-hour clock, as well as variations of that format that remove some of the parts.

**Returns:**
A Python `datetime.datetime` object parsed from the input string.

### iso_format_str_to_datetime
Parse the input string that uses the ISO format and return the corresponding Python `datetime.datetime` object.

**Parameters:**
- `a_date_time_str`: A string representing a date-time in ISO format.

**Returns:**
A Python `datetime.datetime` object with the corresponding date and time.

## Example Interactions

**Patient:** "I would like to schedule an appointment for tomorrow."
**Action:** Use `now` to determine today's date and infer tomorrow's date, allowing other skills to use that information to manage appointments.

**Patient:** "I would like to schedule an appointment for next Tuesday."
**Action:** Use `now` to determine today's date and infer the date for next Tuesday, allowing other skills to use that information to manage appointments.

**Patient:** "I would like to schedule an appointment for this Tuesday."
**Action:** Use `now` to determine today's date and infer the date for next Tuesday, allowing other skills to use that information to manage appointments.

**Patient:** "I would like to schedule an appointment for April 10th."
**Action:** Use `now` to determine today's date and infer the full date for the next April 10th, allowing other skills to use that information to manage appointments.

**Patient:** "I would like to schedule an appointment for April 11th, 2027 at 1 PM."
**Action:** Use `is_week_day` to determine if April 11th, 2027 is a week day or not. If it is a week day, use other skills to manage appointments on that date.
