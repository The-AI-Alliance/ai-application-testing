---
name: appointments
description: Use this skill for managing patient appointments - creating, canceling, confirming, changing, and listing appointments.
---

# Appointment Management Skill

This skill provides capabilities for managing patient appointments in the healthcare ChatBot.

## When to Use This Skill

Use this skill when the patient wants to:
- Schedule a new appointment
- Cancel an existing appointment
- Confirm an appointment
- Change/reschedule an appointment
- List their appointments
- Check available appointment times

## General Tips:

- If you don't know the patient's name, start by asking for the name. Don't ask for the appointment ID. The patient won't know what that is.
- When the patient specifies a partial date, for example, April 10th, assume they mean the next possible matching date. For example, if a patient says "April 10th", then assume the patient means this year or, if we are already past April 10th of this year, then the patient means next year.
- Similarly, if the patient says a day of the week, for example, "Thursday", assume the patient means the next Thursday in the calendar.

## Available Tools

### create_appointment
Create a new appointment for a patient.

**Parameters:**
- `patient_name` (str): Name of the patient
- `appointment_date_time` (str): ISO format datetime string (e.g., "2026-04-15T10:00:00")
- `reason` (str): Reason for the appointment

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message with the appointment_id and details, or an error message if the time slot is unavailable or invalid.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

**Constraints:**
- Appointments must be on the hour (10:00, 11:00, not 10:30)
- Only weekdays (Monday-Friday)
- No holidays
- One patient per time slot

### cancel_appointment
Cancels an existing appointment, specified by the appointment ID. Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name and appointment date and time, if necessary.

**Parameters:**
- `appointment_id` (str): ID of the appointment to cancel

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message with the cancellation confirmation, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

### change_appointment
Changes an appointment to a new time, specified by the appointment ID. Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name and appointment date and time, if necessary.

**Parameters:**
- `appointment_id` (str): ID of the appointment to change
- `new_date_time` (str): New ISO format datetime string

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message with the old and new time confirmation, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

### list_appointments
Lists all active appointments, with optional filtering.

**Parameters:**
- `patient_name` (str, optional): Whether to include past appointments (default: False)
- `after_datetime` (str for a ISO format datetime string, optional): Only include appointments with date times equal to or after this value

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message that is a JSON array with all the appointments found, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

### get_appointments_count
Return the number of appointments currently scheduled.

**Parameters:**

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message that contains the count, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

### get_appointment_by_id
Return a specific appointment for the specified ID. Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name and appointment date and time, if necessary.

**Parameters:**
- `appointment_id` (str): ID of the appointment to change

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message with the details for the appointment, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

### get_appointment_id_for_name_and_date_time
Retrieve the appointment ID for the specified patient name and date time.

**Parameters:**
- `patient_name` (str): The patient name for the appointment
- `appointment_date_time` (str for a ISO format datetime string): the date time for the appointment

**Returns:**
A JSON string using the format specified in the _system prompt_. It must include the following fields:

```json
{
    "label": "appointment", 
    "text": "T",
    "confidence": C
}
```

Where:

- The `text` value `T` is replaced with either a success message that is a string with the found appointment, or an error message if a failure occurs.
- The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.

## Example Interactions

**Patient:** "I'd like to schedule an appointment for next Monday at 2pm"
**Action:** Use `create_appointment` with appropriate parameters

**Patient:** "I'd like to schedule an appointment in the next few weeks"
**Action:** Show the patient several available times, ask the patient to pick one and use `create_appointment` with the appropriate parameters.

**Patient:** "Can I cancel my appointment?"
**Action:** First use `list_appointments` to find their appointment, then `cancel_appointment`

**Patient:** "I need to reschedule my appointment to Wednesday"
**Action:** Use `change_appointment` with the new time

## Important Notes

- Always validate appointment times are during business hours (weekdays).
- Provide clear feedback about appointment constraints.
- When listing appointments, show them in chronological order.
- For cancellations and changes, confirm the action with the patient first.
