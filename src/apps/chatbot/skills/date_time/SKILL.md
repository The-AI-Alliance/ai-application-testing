---
name: date_time
description: Use this skill to determine the current date and time.
---

# Date Time Skill

This skill provides access to date-time facilities.

## When to Use This Skill

Use this skill when you need to know:
- The current date and time or any part of that information

## Available Tools

### now
Determine the current year, month, day, hour, minute, second, and microsecond, returned as a Python `datetime.datetime` object.

**Parameters:**

**Returns:**
A Python `datetime.datetime` object with the current date and time.

### now_str
Determine the current year, month, day, hour, minute, second, and microsecond, returned as a formatted string.

**Parameters:**

**Returns:**
A string representing the current date and time.

## Example Interactions

**Patient:** "I would like to schedule an appointment for tomorrow."
**Action:** Use `now` or `now_str` to determine today's date and infer tomorrow's date, allowing other skills to use that information to manage appointments.

**Patient:** "I would like to schedule an appointment for next Tuesday."
**Action:** Use `now` or `now_str` to determine today's date and infer the date for next Tuesday, allowing other skills to use that information to manage appointments.
