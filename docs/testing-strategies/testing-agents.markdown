---
layout: default
title: Testing Agents
nav_order: 350
parent: Testing Strategies and Techniques
has_children: false
---

# Testing Agents

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

So far in this guide, we have focused on testing AI-enabled applications in a generic sense, not focusing on specific concerns for testing LLMs, agents, or other application patterns. This chapter discusses agent testing.

[Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} are a broad class of software components with behaviors  that are complementary to the capabilities that models themselves provide. They range from relatively simple to very sophisticated. The healthcare ChatBot application is relatively simple. It adds context information to user queries to create prompts and it uses custom handling of the responses. For most use cases, instead of returning the generated text to the user, it presents a message from a limited set of predefined messages, so we have better control over potentially &ldquo;suboptimal&rdquo; generated responses. 

More sophisticated agents include planning, adjustment of the plan based on results (i.e., _course correction_), reasoning, and even autonomous action (when permitted). An example of a more sophisticated agent is the AI Alliance project [Deep Research Agent for Applications](https://the-ai-alliance.github.io/deep-research-agent-for-applications/){:target="_blank"}, which demonstrates an important agent design pattern, <em>Deep Research Agents</em>, with several example applications. (It is built on [LastMile AI's](https://www.lastmileai.dev/){:target="lastmile"} agent framework, [MCP Agent](https://github.com/lastmile-ai/mcp-agent){:target="mcp-agent"}.) An example of an even more advanced agent is [OpenClaw](https://openclaw.ai).

Agents use the same _de facto_ standard access APIs that LLMs use, promoting uniformity for runtime use, as well as testing[^1]. However, the proliferation and greater diversity of agents has led to an explosion of new benchmark suites, both for general-purpose and domain-specific evaluation. This trend is driving efforts to standardize how benchmarks are defined and executed.

[^1]: The ChatBot [Working Example]({{site.baseurl}}/working-example) application does this. It provides an OpenAI-compatible API that supports invocation from almost all tools providing inference abstractions. The application also provides an MCP server.

{: .todo}
> **TODO:** 
> 
> This chapter needs additional contributions. See [this issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/39){:target="_blank"} and [Contributing]({{site.baseurl}}/contributing) if you would like to help.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Agent testing can use the same tools and techniques (e.g., benchmarks) that have been used for models themselves, but more advanced agent workflows require additional tools beyond simple Q&A pairs.
> 1. The diversity of agent behaviors has led to an explosion of general-purpose and domain-specific benchmarks, as well as some new tools. This trend is driving interest in standardizing how benchmarks are written and executed.


{: .todo}
> **TODOs:**
>
> 1. Research the work of experts in this area. See the following list.
> 1. Catalog the unique requirements for agent testing.
> 1. Provide specific examples of how to use those concepts.

## The Challenges of Writing Agent Evaluations

Anthropic's post, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"}, provides valuable tips on testing complex agents, including new requirements for evaluations that didn't exist when we only focused on evaluating models. Here is a summary of the key points.

* **Agents are multi-turn:** Agents can make several invocations of models, tools, and other agents to accomplish their goals, including several round trips. Analysis of early responses can lead to refining the initial plan, including what work to do next. LLM evaluations assumed a single invocation and response. So far, we have relied on unit benchmarks with Q&A pairs, but the complexity of agent behaviors make this approach insufficient, as we mentioned in the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/#how-many-qa-pairs-do-we-need) chapter.
* **Automated evaluations are mandatory:** Software engineers have known for decades that without automated tests to catch regressions and ensure continued, acceptable performance as the system is evolved, progress will quickly grind to a halt. The same argument is true for agent evaluations. Another benefit of automated evaluations is the ability to try new versions of models or new model families with relative ease.
* **Tools for agent evaluation:** Anthropic sees three kinds of _graders_ used in evaluations:
    * **Code-based graders:** Non-AI tools like string and regex matching, rules verification, static analysis like linting, typing, and security checks, and analysis of the _agent under test's_ log of activities. These tools are fast and cheap to use, deterministic and hence reproducible, and easy to write and debug. However, they are more brittle to small, but insignificant differences compared to model-based graders and they aren't suitable for more &ldquo;nuanced&rdquo; tasks.
    * **Model-based graders:** Using models, generative or not, to analyze results. LLM as a Judge is an example. They provide greater flexibility, especially for &ldquo;nuanced&rdquo; tasks and tasks with more open-ended behaviors. They can also handle more free form inputs. However, they are non-deterministic, expensive to run, and require careful human calibration to ensure they work correctly.
    * **Human graders:** Subject matter experts, crowd sourcing, spot checks of samples, A/B testing, etc. They are considered the gold standard for quality, especially where expert-level performance for a domain is required. Often human experts are used to calibrate model-based graders, rather then used to grade agent outputs themselves. Downsides include the fact that humans make mistakes, especially when fatigued, they are expensive and slow, and experts may be hard to find.
* **Scoring:** Options include weighted scores that combine results of different graders, binary (all must pass), or a mixture.
* **Capability vs. regression evaluations:** _Capability_ (or _quality_) evaluations ask, "What does this agent do well?" A low pass rate can be expected in the early phases of development. _Regression_ evaluations ask, "Does the agent still handle all the tasks is handled previously?" A high pass rate is required, ideally 100%, but realistically something close to that. Once a capability evaluation has a high pass rate, it can be migrated to the regression evaluations.
* **Examples:** The post discusses evaluation examples for three use cases.
    * **Coding agents:** Agents that perform software development tasks. Deterministic evaluation of code is well established, e.g., unit tests, so deterministic graders can do much of the work evaluating coding agents. There are several, well-known coding-agent benchmarks, too.
    * **Conversational agents:** Our ChatBot application is an example. The quality of the interaction, as well as the outcomes, are important areas to evaluate. Often, a second LLM is used to represent the user of the agent in the conversation. The evaluation is often multidimensional. Was the desired end state reached (sometimes a deterministic state check, but other times a more subjective evaluation suitable for an LLM to perform)? Did it finish within a budget constraint (also deterministic)? Was the conversational tone appropriate (a subjective evaluation suitable for an LLM to perform)?
    * **Research agents:** Agents that gather, synthesize, and analyze information, then prepare a report for human consumption. There are partially subjective qualities, like &ldquo;comprehensiveness&rdquo;, &ldquo;well-sourced&rdquo;, and &ldquo;correct&rdquo;, as well as a mix of more objective outcomes, like were particular, essential facts retrieved? Frequent evaluation by human experts is necessary to ensure these agents work as desired.
    * **Computer use agents:** Agents that interact with computer systems the way a human would, such as through a GUI. Often, these agents can be evaluated with deterministic graders, but since they usually work with the DOM (domain object model) of web pages, which can be large and inefficient to process, techniques for optimizing performance are important.
* **How to think about non-determinism in evaluations for agents:**





### TODO: Incorporate Ideas from the Following Sources

* CUBE Standard and Harness
* https://evalevalai.com/infrastructure/2026/02/17/everyevalever-launch/
* PyTorch OpenEnv:
    * https://meta-pytorch.org/OpenEnv/
    * https://huggingface.co/blog/openenv
    * https://huggingface.co/openenv
    * https://github.com/meta-pytorch/OpenEnv
    * Agent Beats Competition:
        * https://www.linkedin.com/posts/jspisak_agentic-ai-weekly-berkeley-rdi-january-activity-7414721490018906112-UbpX
        * https://berkeleyrdi.substack.com/p/agentic-ai-weekly-berkeley-rdi-january
* https://research.ibm.com/blog/cuga-agent-framework
    * https://github.com/cuga-project/cuga-agent
    * https://huggingface.co/blog/ibm-research/cuga-on-hugging-face
* https://partnershiponai.org/resource/prioritizing-real-time-failure-detection-in-ai-agents/
* www.anthropic.com/engineering/multi-agent-research-system
* Mozilla's `any-agent`:
    * https://www.mozilla.ai/open-tools/choice-first-stack/any-agent
    * https://github.com/mozilla-ai/any-agent
* https://agenttoolkit.github.io/agent-lifecycle-toolkit/
* https://github.com/agentsmd/agents.md
* https://glaforge.dev/talks/2025/12/02/ai-agentic-patterns-and-anti-patterns/
* https://www.microsoft.com/en-us/research/blog/agent-lightning-adding-reinforcement-learning-to-ai-agents-without-code-rewrites/
* https://www.patronus.ai/blog/introducing-generative-simulators
* https://github.com/rustyoldrake/security_governance_compliance_ai_agentic
* https://mellea.ai/
* https://openagi.aiplanet.com/ - "OpenAGI"

<a id="other-tools"/>

## Other Tools for Testing Agents

### DoomArena

[DoomArena](https://servicenow.github.io/DoomArena/){:target="_blank"} from [ServiceNow](https://www.servicenow.com/){:target="_blank"} is a framework for testing AI Agents against evolving security threats. It offers a modular, configurable, plug-in framework for testing the security of AI agents across multiple attack scenarios.

DoomArena enables detailed threat modeling, adaptive testing, and fine-grained security evaluations through real-world case studies, such as τ-Bench and BrowserGym. These case studies showcase how DoomArena evaluates vulnerabilities in AI agents interacting in airline customer service and e-commerce contexts.

Furthermore, DoomArena serves as a laboratory for AI agent security research, revealing fascinating insights about agent vulnerabilities, defense effectiveness, and attack interactions.

### Google's Agent Development Kit

Google's [Agent Development Kit](https://google.github.io/adk-docs/){:target="adk"} has a chapter called [Why Evaluate Agents?](https://google.github.io/adk-docs/evaluate/){:target="adk"}, which provides tips for writing evaluations specifically tailored for agents.

### LastMile AI's MCP Eval

[MCP Eval](https://mcp-eval.ai/){:target="mcp-eval"} is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation. It is built on [MCP Agent](https://mcp-agent.com/){:target="mcp-agent"}, their agent framework that emphasizes MCP as the communication protocol.

### IBM's AssetOpsBench

[AssetOpsBench](https://github.com/IBM/AssetOpsBench){:target="ibm-aob"} is a unified framework for developing, orchestrating, and evaluating domain-specific AI agents in industrial asset operations and maintenance. It is designed for maintenance engineers, reliability specialists, and facility planners, it allows reproducible evaluation of multi-step workflows in simulated industrial environments.

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will expand this section once more content is provided above.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Advanced Techniques]({{site.baseurl}}/advanced-techniques/).

---
