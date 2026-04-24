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
> ---
> name: appointments
> description: Use this skill for managing patient appointments - creating, canceling, confirming, changing, and > listing appointments.
> ---
> 
> # Appointment Management Skill
> 
> This skill provides capabilities for managing patient appointments in the healthcare ChatBot.
> 
> ## When to Use This Skill
> 
> Use this skill when the patient wants to:
> - Schedule a new appointment
> - Cancel an existing appointment
> - Confirm an appointment
> - Change/reschedule an appointment
> - List their appointments
> - Check available appointment times
> 
> ## General Tips:
> 
> - If you don't know the patient's name, start by asking for the name. Don't ask for the appointment ID. The patient won't know what that is.
> - When the patient specifies a partial date, for example, April 10th, assume they mean the next possible matching date. For example, if a patient says "April 10th", then assume the patient means this year or, if we are already past April 10th of this year, then the patient means next year.
> - Similarly, if the patient says a day of the week, for example, "Thursday", assume the patient means the next Thursday in the calendar.
> 
> ## Available Tools
> 
> ### create_appointment
> Create a new appointment for a patient.
> 
> **Parameters:**
> - `patient_name` (str): Name of the patient
> - `appointment_time` (str): ISO format datetime string (e.g., "2026-04-15T10:00:00")
> - `reason` (str): Reason for the appointment
> 
> **Returns:**
> A JSON string using the format specified in the _system prompt_. It must include the following fields:
> 
> {
>     "label": "appointment", 
>     "text": "T",
>     "confidence": C
> }
> 
> Where:
> 
> - The `text` value `T` is replaced with either a success message with the appointment_id and details, or an error message if the time slot is unavailable or invalid.
> - The `confidence` value `C` is replaced with your confidence in the success of the operation, a number between 0.0 and 1.0, inclusive, where 0.0 means no confidence and 1.0 means complete confidence.
> 
> **Constraints:**
> - Appointments must be on the hour (10:00, 11:00, not 10:30)
> - Only weekdays (Monday-Friday)
> - No holidays
> - One patient per time slot
> 
> ### cancel_appointment
> Cancels an existing appointment.
> ...
> 
> 
> ## Example Interactions
> 
> **Patient:** "I'd like to schedule an appointment for next Monday at 2pm"
> **Action:** Use `create_appointment` with appropriate parameters
> 
> ...
> 
> ## Important Notes
> 
> - Always validate appointment times are during business hours (weekdays).
> ...
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
