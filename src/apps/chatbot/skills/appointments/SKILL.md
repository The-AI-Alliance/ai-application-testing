---
name: appointments
description: Use this skill for managing patient appointments - creating, canceling, confirming, changing, and listing appointments.
---

# Appointment Management Skill

This skill provides capabilities for managing patient appointments in the healthcare ChatBot.

## When to Use This Skill

Use this skill when the patient asks about doing one of the following _scenarios_:

- Schedule a new appointment
- Change/reschedule an appointment
- Cancel an appointment
- Get information about one or more upcoming appointments
- Ask about available times for a new appointment
- Ask about scheduling an appointment for a health issue or getting a referral

The details for each of these scenarios is discussed next.

### Schedule a new appointment

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Patient name** - The name of the patient for the appointment.
* **Appointment date and time** - The date and time when the patient can come in for an appointment and which is open in the schedule.
    * **Possible dates and times** - To determine the **Appointment date and time**, discuss with the user the dates and times that work for the patient and are also available in the schedule.
* **Reason** - Purpose of the appointment.

#### Success outcome

A new appointment is created for the patient at the date-time.

### Change/reschedule an appointment

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Patient name** - The name of the patient for the appointment.
* **Appointment date and time** - The current date-time for the appointment.
* **New appointment date and time** - A new date-time for the appointment that works for the patient and is open in the schedule.
    * **Possible dates and times** - To determine the **New appointment date and time**, discuss with the user the dates and times that work for the patient and are also available in the schedule.

#### Success outcome

The existing appointment is changed to the new date-time.

### Cancel an appointment

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Patient name** - The name of the patient for the appointment.
* **Appointment date and time** - The current date-time for the appointment.

#### Success outcome

The existing appointment is canceled and the appointment's date-time
is made free in the schedule.

### Get information about one or more upcoming appointments

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Patient name** - The name of the patient for the appointment.

#### Success outcome

Zero or more appointments for the patient are shown to the patient.

### Ask about available times for a new appointment

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Appointment dates and times** - discuss with the user the dates and times that work for the patient and are also available in the schedule.

#### Success outcome

Zero or more dates and times available for appointments that also work for the patient.

### Ask about scheduling an appointment for a health issue or getting a referral

#### Information you need

Obtain the following information from the user if you don't already have it, i.e., it was part of the user query: 

* **Patient name** - The name of the patient for the appointment.
* **Problem** - The issue the patient is experiencing.

#### Success outcome

A healthcare provider will respond as soon as possible. Do not create a new appointment.

## General Tips:

- If you don't know the patient's name, start by asking for the name. Don't ask for the appointment ID. The patient won't know what that is.
- When the patient specifies a partial date, for example, April 10th, assume they mean the next possible matching date. For example, if a patient says "April 10th", then assume the patient means this year, unless we are already past April 10th of this year, then assume the patient means next year.
- Similarly, if the patient says a day of the week, for example, "Thursday", assume the patient means the next Thursday in the calendar.

## Available Tools

Use the following tools to implement the scenarios described above.

### create_appointment
Create a new appointment for a patient.

**Parameters:**
- `patient_name` (str): Name of the patient
- `appointment_date_time` (str): ISO format datetime string (e.g., "2026-04-15T10:00:00")
- `reason` (str): Reason for the appointment

**Returns:**
The tool returns a `tuple[str,str]`. If the appointment was successfully created, the first tuple element is the non-empty `appointment_id` for the created appointment and the second tuple element is a success message. If the appointment was not successfully created, the first tuple element is the empty string '' and the second tuple element is an error message. 

Return this information as JSON:

```json
{
    "appointment_id": appointment_id, 
    "message": message
}
```

Where:

- The `appointment_id` value is the first tuple element returned.
- The `message` value is the second tuple element returned.

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
The tool returns a `tuple[bool,str]`. If the appointment was successfully cancelled, the first tuple element is `True` and the second tuple element is a success message. If the appointment was not successfully cancelled, the first tuple element is `False` and the second tuple element is an error message. 

Return this information as JSON:

```json
{
    "success": True | False, 
    "message": message
}
```

Where:

- The `success` value is the first tuple element returned, i.e., `True` or `False`.
- The `message` value is the second tuple element returned.

### change_appointment
Changes an appointment to a new time, specified by the appointment ID. Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name and appointment date and time, if necessary.

**Parameters:**
- `appointment_id` (str): ID of the appointment to change
- `new_date_time` (str): New ISO format datetime string

**Returns:**
The tool returns a `tuple[bool,str]`. If the appointment was successfully changed, the first tuple element is `True` and the second tuple element is a success message. If the appointment was not successfully changed, the first tuple element is `False` and the second tuple element is an error message. 

Return this information as JSON:

```json
{
    "success": True | False, 
    "message": message
}
```

Where:

- The `success` value is the first tuple element returned, i.e., `True` or `False`.
- The `message` value is the second tuple element returned.

### get_appointments
Get all active appointments, with optional filtering.

**Parameters:**
- `patient_name` (str, optional): Whether to include past appointments (default: False)
- `after_datetime` (str for a ISO format datetime string, optional): Only include appointments with date-times equal to or after this value

**Returns:**
The tool returns a `list[dict[str,Any]]`, containing a dictionary for each appointment. The list will be empty if there are no appointments that match the filter criteria (if any).

Return this information as JSON:

```json
{
    "appointments": appointment_list
}
```

Where:

- The `appointments` value is the list returned, which will be `[]`, if empty.

### get_appointments_count
Return the number of appointments currently scheduled.

**Parameters:**

**Returns:**
The tool returns an integer count of all the appointments, which may be zero.

Return this information as JSON:

```json
{
    "count": count
}
```

Where:

- The `count` is the number of appointments returned.

### get_appointment_by_id
Return a specific appointment for the specified ID. Use "get_appointment_id_for_name_and_date_time" to get the ID for a patient name and appointment date and time, if necessary.

**Parameters:**
- `appointment_id` (str): ID of the appointment to change

**Returns:**
The tool returns a `dict[str, Any]` with the appointment details, or `{}` if no appointment was found for the input `appointment_id`. 

Return this information as JSON:

```json
{
    "appointment" : dictionary_as_json 
}
```

Where:

- The `dictionary_as_json` value is the appointment dictionary converted to JSON.

### get_appointment_id_for_name_and_date_time
Retrieve the appointment ID for the specified patient name and date-time.

**Parameters:**
- `patient_name` (str): The patient name for the appointment
- `appointment_date_time` (str for a ISO format datetime string): the date-time for the appointment

**Returns:**
The tool returns a `str` with the appointment ID or '' if no matching appointment was found.

Return this information as JSON:

```json
{
    "appointment_id": appointment_id
}
```

Where:

- The `appointment_id` value is the returned appointment ID, which may be ''.

## Example Interactions

**Patient:** "I'd like to schedule an appointment for next Monday at 2pm"
**Action:** Use `create_appointment` with appropriate parameters

**Patient:** "I'd like to schedule an appointment in the next few weeks"
**Action:** Show the patient several available times, ask the patient to pick one and use `create_appointment` with the appropriate parameters.

**Patient:** "Can I cancel my appointment?"
**Action:** First use `get_appointments` to find their appointment, then `cancel_appointment`

**Patient:** "I need to reschedule my appointment to Wednesday"
**Action:** Use `change_appointment` with the new time

## Important Notes

- Always validate appointment times are during business hours (weekdays).
- Provide clear feedback about appointment constraints.
- When listing appointments, show them in chronological order.
- For cancellations and changes, confirm the action with the patient first.
