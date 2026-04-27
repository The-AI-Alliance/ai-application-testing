---
layout: default
title: Building Agents
nav_order: 3520
parent: Testing Agents
grand_parent: Testing Strategies and Techniques
has_children: false
---

# Building Agents

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

While we can't cover all tools and techniques for building agents, we have used a few of them for our ChatBot application, which we discuss in this chapter. The concepts discussed should remain useful for a long time, although the particular tools and techniques are evolving rapidly.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. [Agent Skills]({{site.glossaryurl}}/#agent-skills){:target="_glossary"} is a technique for adding new capabilities to agents in a modular way.
> 1. TBD - more will be added once the text below is complete. 

## An Agentic ChatBot

This chapter introduces an agent-based ChatBot implementation, [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"}, which uses [Langchain's _Deep Agents_](https://www.langchain.com/deep-agents){:target="lcda"} tools for more advanced behaviors, including [Agent Skills](#agent-skills), a modular way of defining agent behaviors. (Skills are one of those promising, new agent techniques that is worth investigation.) See [Run the ChatBot Example Application]({{site.baseurl}}/working-example/#run-the-chatbot-example-application) for details on running `ChatBotAgent`. For example, this implementation is used when you run `make chatbot`.[^1]

Of the many choices available to us, we picked Langchain's _Deep Agents_ toolkit for two reasons: LangChain is widely used and its _Deep Agents_ library supports [Agent Skills](#agent-skills). We also switched to `gemma4:e4b` as our default, open-weights model, when we started this implementation, because we found it worked better for this implementation than the other models we have used.

[^1]: The original, _simple_ ChatBot implementation, [`ChatBotSimple`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_simple.py){:target="cba-gh"}, which just uses LLM inference and a thin wrapper of application code, is still available and can be run with `make simple-chatbot`.

Let's begin by discussing _Agent Skills_.

## Agent Skills

Agent capabilities can be implemented in many ways. We chose to use the concept of [Agent Skills]({{site.glossaryurl}}/#agent-skills){:target="_glossary"}, which was recently introduced by [Anthropic](https://anthropic.com/){:target="anthropic"} as a way of specifying skills in a structured, modular format. 

Skills are designed to teach agents new capabilities without invasive modifications like tuning the underlying models. Skills has the potential to become a widely-used, standard approach. It is already supported in [LangChain Deep Agents](https://www.langchain.com/deep-agents){:target="lcda"} , which is one reason we chose this framework for our [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"} implementation.

The [Agent Skills](https://agentskills.io/){:target="agent-skills"} website provides details, including a [specification](https://agentskills.io/specification){:target="agent-skills"} for skills. Example skills are in Anthropic's [`skills` GitHub repo](https://github.com/anthropics/skills){:target="anthropic-skills-gh"} and a catalog of skills can be found at [`skills.sh`](https://skills.sh/){:target="skills-sh"}. See also the [`agentskills`](https://github.com/agentskills/agentskills){:target="agent-skills-gh"} repo. 

Quoting from [What are skills?](https://agentskills.io/what-are-skills){:target="agent-skills"}:

{: .attention}
> Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.
>
> At its core, a skill is a folder containing a `SKILL.md` file. This file includes metadata (name and description, at a minimum) and instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, templates, and reference materials. 

The additional, optional content is put in subdirectories:

* `scripts`: Executable code
* `references`: Documentation
* `assets`: Templates, resources

Because of context size limitations, skill implementations should use _progressive disclosure_ to manage context efficiently. Quoting again from [What are skills?](https://agentskills.io/what-are-skills){:target="agent-skills"}:

{: .attention}
> * **Discovery:** At startup, agents should load only the name and description of each available skill, just enough to know when it might be relevant.
> * **Activation:** When a task matches a skill’s description, the agent reads the full `SKILL.md` instructions into context.
> * **Execution:** The agent follows the instructions, optionally loading referenced files or executing bundled code as needed.

Appointment handling in [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"} is implemented this way. The [`src/apps/chatbot/skills/appointments`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/skills/appointments){:target="cba-gh"} directory contains a [`SKILL.md`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/skills/appointments/SKILL.md){:target="cba-gh"} file, which is effectively a system prompt explaining how to implement the skill, and a Python file, [`appointment_tools.py`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/skills/appointments/appointment_tools.py){:target="cba-gh"}, which implements the &ldquo;tools&rdquo; described in `SKILL.md`. These tools are Python functions with a `@tool` annotation and they delegate the work to a very simple class [`AppointmentManager`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/tools/appointments/appointment_manager.py){:target="cba-gh"}, which simulates managing a calendar of appointments for demonstration and test purposes.

Here are parts of the `SKILL.md` file for appointments, with some sections elided (`...`):

> ```markdown
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
- `after_datetime` (str for a ISO format datetime string, optional): Only include appointments with date times equal to or after this value

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
Retrieve the appointment ID for the specified patient name and date time.

**Parameters:**
- `patient_name` (str): The patient name for the appointment
- `appointment_date_time` (str for a ISO format datetime string): the date time for the appointment

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
**Action:** First use `gett_appointments` to find their appointment, then `cancel_appointment`

**Patient:** "I need to reschedule my appointment to Wednesday"
**Action:** Use `change_appointment` with the new time

## Important Notes

- Always validate appointment times are during business hours (weekdays).
- Provide clear feedback about appointment constraints.
- When listing appointments, show them in chronological order.
- For cancellations and changes, confirm the action with the patient first.

> ```

Most of this is self-explanatory. The `create_appointment` tool is implemented in the Python file, [`appointment_tools.py`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/skills/appointments/appointment_tools.py){:target="cba-gh"}. (We omit the comment block found in the definition):

```python
@tool
def create_appointment(patient_name: str, appointment_time: str, reason: str) -> dict[str, Any]:
    try:
        appt_time = datetime.fromisoformat(appointment_time)
        tool = get_appointment_manager()
        result = tool.create_appointment(patient_name, appt_time, reason)
        return result
    except AppointmentError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": f"Invalid datetime format: {e}"}
```

It calls a support function `get_appointment_manager` that retrieves a global instance of the `AppointmentManager` class mentioned above. That class just tracks appointments in a file, `output/applications.jsonl`, and makes several simplifying assumptions and constrains. Obviously a real ChatBot would use a real calendar manager.

In our experience using `gemma4:e4b` and the LangChain Deep Agents library, a user session to manage appointments with the ChatBot works &ldquo;okay&rdquo;. The experience is not production ready, but it illustrates possibilities.

Finally, see also this blog post, [I Still Prefer MCP Over Skills](https://david.coffee/i-still-prefer-mcp-over-skills/){:target="skills-mcp"}, which compares the pros and cons of using [MCP]({{site.glossaryurl}}/#model-context-protocol){:target="_glossary"} servers vs. skills for different purposes.

## ChatBotAgent

Let's discuss how we applied these concepts to the agent-based ChatBot implementation, [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"}. As we said above, we used [Langchain's _Deep Agents_](https://www.langchain.com/deep-agents){:target="lcda"} tools to provide more advanced behaviors, including [Agent Skills](#agent-skills). Recall that [Run the ChatBot Example Application]({{site.baseurl}}/working-example/#run-the-chatbot-example-application) explains how to run `ChatBotAgent`. For example, it is the default ChatBot implementation, so it is the one executed when you run `make chatbot`.

TBD

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will complete this section once a working example is provided.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Evaluating Agents](../evaluating-agents/).

---
