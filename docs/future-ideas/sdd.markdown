---
layout: default
title: Specification-Driven Development
nav_order: 410
parent: Future Ideas
has_children: false
---

# Specification-Driven Development

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

{: .note}
> Arguably, this chapter is less forward looking than the others in the [Future Ideas]({{site.baseurl}}/future-ideas/) section. However, we put it here because it is a new and emerging idea and using it will be more transformational to development processes than the changes we have discussed in [Architecture and Design]({{site.baseurl}}/arch-design) and [Testing Strategies]({{site.baseurl}}/testing-strategies), where we take a more &ldquo;incremental&rdquo; approach. However, we may move it elsewhere eventually.
<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. LLMs are literal minded (like all software). If we want the best results, we have to write precise prompts that are explicit in the details. 
> 1. The more we rely on LLMs to do our work, the more important good prompts become.
> 1. LLMs do best when they are asked to do small increments of work, rather than larger amounts of work all at once. Separating different process &ldquo;phases&rdquo; is an example.
> 1. Structured prompts and carefully-chosen support tools for each &ldquo;phase&rdquo; provide the best results.
> 1. For software development having [Coding Agents]({{site.glossaryurl}}/#coding-agent){:target="_glossary"} do all work as iteratively and incrementally as possible improves results. For example, using iterative prompting to build up complete requirements, one step at a time, results in better, more complete requirements than one-shot LLM generation or other approaches. Similarly, code should be implemented or modified one small [Unit]({{site.glossaryurl}}/#unit){:target="_glossary"} at a time with individual commits to `git`.
> 1. Carl Annaberg's AI Coding Workflow has two phases, **planning** and **execution**, while GitHub's Spec Kit adds a first step **specify** to create the specification, splits planning into two, more-granular phases, **plan** and **tasks**, then finishes with an **implement** phase that is similar to Annaberg's **execution** phase.

The more we rely on AI-powered [Coding Agents]({{site.glossaryurl}}/#coding-agent){:target="_glossary"}, the more crucial it becomes to write prompts that produce the results we need. Generative models are &ldquo;literal minded&rdquo; (just like all computing systems). We have to use very precise instructions to get the results we want.

Specification-driven development (SDD), also known as _spec-driven development_ and  _spec-driven coding_, attempts to impose more structure on prompts so models do a better job generating source code that we actually need. Similarly, it identifies different &ldquo;phases&rdquo; of software creation and customizes the prompts and tools used for each one. The ad hoc, free-form prompts we currently use for [Vibe Coding]({{site.glossaryurl}}/#vibe-coding){:target="_glossary"} and [Vibe Engineering]({{site.glossaryurl}}/#vibe-engineering){:target="_glossary"} are not adequate for our needs.

For an industry analyst's perspective on SDD, see [this RedMonk piece](https://redmonk.com/rstephens/2025/07/31/spec-vs-vibes/){:target="redmonk-spec"}.

Several different people and groups are exploring this idea in related ways. 

## Carl Annaberg's AI Coding Workflow

In June, 2025, [Carl Annaberg](https://carlrannaberg.medium.com/){:target="_blank"} wrote a blog post [My current AI coding workflow](https://carlrannaberg.medium.com/my-current-ai-coding-workflow-f6bdc449df7f){:target="_blank"} ([repo](https://github.com/carlrannaberg/ai-coding){:target="_blank"}) where he described a workflow he uses with [Cursor](https://cursor.com/){:target="_blank"}, one of the most popular coding agents.

He realized that Cursor produces better results if he uses separate **planning** and **execution** &ldquo;phases&rdquo;, implemented as Cursor _modes_, **plan** and **act**, respectively (but he uses these names interchangeably). The ideas were inspired by Harper Reed's blog post, [My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/){:target="_blank"}, by [Cline's](https://cline.bot/){:target="_blank"} _plan and act_ modes, and by [Windsurf's](https://windsurf.com/){:target="_blank"} _planning_ mode.

Each mode for a phase restricts the tools available. For example, no code modification or generation tools are allowed in the planning phase, to prevent &ldquo;premature&rdquo; activity during the planning process.

The blog post describes planning as follows:

{: .attention}
> I switch to Planner mode and add relevant files and folders to the context. Then I describe what I want to build or change. The planner asks clarifying questions, one at a time, building on previous answers. This iterative Q&A continues until we have a complete understanding of the requirements. This approach was inspired by Harper Reed’s [AI codegen workflow](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/){:target="_blank"}, where he uses a similar one-question-at-a-time method to develop thorough specs.

The output is a `plan.md` file, which is added to the execution's context, and then that mode is executed, performing the following steps (quoted from the blog post):

* **Reads** the plan and identifies the first unchecked task.
* **Implements** the specific changes required by the task.
* **Runs tests** to verify that the implementation works correctly.
* **Commits** the changes with a clear, descriptive message.
* **Marks** the task as completed in the plan.

Execution is repeated to move sequentially through the remaining tasks until the entire plan is complete. The final results have these benefits:

{: .attention}
> Instead of one massive, difficult-to-review change, this workflow gives me:
> * **A clean git history** with atomic, easy-to-follow commits.
> * **Each change** thoroughly tested and verified individually.
> * **Clear explanations** of what was implemented with each commit.
> * **Easy rollback capability** for any specific change if necessary.

In addition, the prompts and sessions used are saved and managed like other artifacts.

The blog post discusses details about the prompts for the two modes and ways they help ensure the best results.

Highlights of this approach include the following:

* Structured prompts and carefully-chosen support tools for each &ldquo;phase&rdquo; provide the best results. Coding agents that support &ldquo;modes&rdquo; make it easier to implement support for each phase.
* Recognizing that models do best when they are asked to do small increments of work, rather than larger amounts of work all at once. Separating planning from execution is an example.
* Iterative prompting to incrementally build up complete requirements, one step at a time.
* Iterative and incremental code changes and git commits.

## Andres Kull's Spec-Driven AI Coding

In July, 2025, Andres Kull adapted Annaberg's ideas for his take on [Spec-Driven AI Coding](https://finfluencers.trade/blog/2025/07/22/how-i-apply-spec-driven-ai-coding/){:target="_blank"} ([repo](https://github.com/andreskull/spec-driven-ai-coding){:target="_blank"}). 

He added portability to other _coding agents_ besides Cursor, including [Claude Code](https://www.anthropic.com/claude-code){:target="_blank"}, [AWS Kiro](https://kiro.dev/){:target="_blank"} (an AI IDE designed to support specification-driven development), and [Gemini CLI](https://github.com/google-gemini/gemini-cli){:target="_blank"}.

Kull uses the term _persona_ for modes, and he adds an additional persona, _Steering Architect_, used to analyze existing projects and generate the artifacts that would otherwise be generated from scratch in a greenfield project.

## GitHub's Spec Kit

In September, 2025, GitHub [announced](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/){:target="_blank"} their [Spec Kit](https://speckit.org/){:target="_blank"}, with similar capabilities. This [Microsoft blog post](https://developer.microsoft.com/blog/spec-driven-development-spec-kit){:target="_blank"}, published soon afterwards, provides more details on how to use Spec Kit and how it works.[^1] 

[^1]: Neither blog post mentions the earlier work by Annaberg, Kull, and Reed, but the similarities in the details suggest they were aware of this earlier work.

The GitHub blog post describes their take on SDD this way:

{: .attention}
> Instead of coding first and writing docs later, in spec-driven development, you start with a (you guessed it) spec. This is a contract for how your code should behave and becomes the source of truth your tools and AI agents use to generate, test, and validate code. The result is less guesswork, fewer surprises, and higher-quality code.

Of course, this philosophy of _specifications as code_ was introduced by [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development){:target="_glossary"} in the late 1990s. A variant of TDD, called [Behavior-Driven Development]({{site.glossaryurl}}/#behavior-driven-development){:target="_glossary"}, took TDD's emphasis on tests as living specifications to the logical limit, where the corresponding testing APIs expose constructs for defining _executable specifications_, so the tests read more like specifications than like conventional tests. A more Mathematics-oriented, but similar approach pioneered around the same time is [Property-Based Testing]({{site.glossaryurl}}/#property-based-testing){:target="_glossary"}.

The blog post argues that coding agents are already fully capable of generating the code we need, but because they behave like very literal-minded pair programmers, we have to give them unambiguous instructions, not unlike the way programming languages are designed to be as unambiguous as possible.

The post also says the following:

{: .attention}
> That’s why we’re rethinking specifications — not as static documents, but as living, executable artifacts that evolve with the project. Specs become the shared source of truth. When something doesn’t make sense, you go back to the spec; when a project grows complex, you refine it; when tasks feel too large, you break them down.

This is very much how TDD and its variants are designed to work. What's innovative about SDD is bringing this rigor to prompts.

### The Spec Kit Process

The [GitHub blog post](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/){:target="_blank"} outlines four phases, each with checkpoints that must be satisfied before moving to the next phase. Recall from above that Annaberg uses the term &ldquo;phase&rdquo;, too, and the term &ldquo;mode&rdquo; for how he implemented the phases with Cursor's _mode_ feature. Compared to Annaberg's approach, GitHub's Spec Kit adds a first **specify** phase to generate the specifications, while Annaberg relies more (but not completely) on pre-existing requirements information, fed into his **planning** phase. Spec Kit breaks down Annaberg's **planning** phase into two separate phases:

* **plan:** Add more technical details and generate a high-level plan for the project.
* **tasks:** Decompose the plan into fine-grained tasks.

Spec Kit's **implement** phase is similar to Annaberg's **execution** phase.

Both approaches deliver similar benefits; see the list above for Annaberg's approach.

Here is a summary of the blog post's description of the phases.

#### 1. Specify

In the first phase, we use our coding agent to generate a detailed specification. Quoting from the blog post:

{: .attention}
> You provide a high-level description of what you are building and why, and the coding agent generates a detailed specification. 

At this point, we aren't thinking about design, tool choices, etc. The focus is on user roles, their responsibilities, and their desired outcomes.

The output specification (like all the artifacts created during this process), is a living artifact that will be refined as we build and learn more about what the application needs to be. 

In fact, it is unlikely that the initial output will be sufficient. We will iteratively refine the prompt to improve the coding agent's output until we decide the specification is sufficiently good to proceed to the next phase.

#### 2. Plan

In the second phase, we specify technical details, some of which might include the following:

* Our target application stack and related tools
* Guidance on the architecture
* Required integrations with other systems
* Known constraints that must be satisfied, such as regulatory, compliance, and performance requirements. 

From this input, the coding agent generates a comprehensive technical plan. 
As for the first phase, we iterate until we are satisfied with the plan.

A variation of this phase is to ask for several plans that we can compare and pick the one which seems best. 

#### 3. Tasks

In the third phase, we ask the coding agent to use the specification and the plan to generate tasks to be done. Like we would during any software task planning exercise, we want the output tasks to be sufficiently fine-grained that estimation, tracking, sequencing of task execution, and code reviews and validation are all feasible, especially since humans are expected to validate all results. 

#### 4. Implement

In the last phase, the coding agent performs the tasks, which it is able to do because of the following:

{: .attention}
> The coding agent knows what it’s supposed to build because the specification told it. It knows how to build it because the plan told it. And it knows exactly what to work on because the task told it.

Furthermore, a good task breakdown will mean completing each task will produce fine-grained and focused changes, which are much easier for us to review and validate. We won't be forced to review huge code dumps, which is tedious and error prone.

## Using Spec Kit

While designed primarily for [Claude Code](https://www.anthropic.com/claude-code){:target="_blank"}, [GitHub Copilot](https://code.visualstudio.com/){:target="_blank"}, and [Gemini CLI](https://github.com/google-gemini/gemini-cli){:target="_blank"}, Spec Kit supports many more coding agents, [listed here](https://github.com/github/spec-kit?tab=readme-ov-file#-supported-ai-agents){:target="_blank"}.

{: .todo}
> **TODO:** 
> 
> Add an example using our running example application.

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> Expand this section once the example is provided.


## What's Next?

A list of resources about SDD, most of which were discussed here, can be found in the [References]({{site.baseurl}}/references/#specification-driven-development). See also [this list of coding agents]({{site.glossaryurl}}/#coding-agent){:target="_glossary"}.

Review the [highlights](#highlights) summarized above, then proceed to [Can We Eliminate Source Code?]({{site.baseurl}}/future-ideas/eliminate-source-code/).

---
