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
> 1. Agent testing uses the same tools and techniques (e.g., benchmarks) that have been used for models themselves.
> 1. The diversity of agent behaviors has led to an explosion of general-purpose and domain-specific benchmarks, as well as some new tools. This trend is driving interest in standardizing how benchmarks are written and executed.


{: .todo}
> **TODOs:**
>
> 1. Research the work of experts in this area. See the following list.
> 1. Catalog the unique requirements for agent testing.
> 1. Provide specific examples of how to use those concepts.

## The Challenges of Writing Agent Evaluations

Anthropic's post, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"}, provides valuable tips on testing complex agents, including new requirements for evaluations that didn't exist when we only focused on evaluating models. Here is a summary of the key ideas.

* **Agents are multi-turn:** They can make several invocations of models, tools, and other agents to accomplish their goals. Analysis of early responses can lead to refining the initial plan, including what work to do next. LLM evaluations assumed a single invocation and response. So far, we have relied on unit benchmarks with Q&A pairs, but the complexity of agent behaviors make this approach insufficient, as mentioned in the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/#how-many-qa-pairs-do-we-need) chapter.
* **Automated Evaluations are mandatory:** They make the same argument that software engineers have known for decades, that without automated tests to catch regressions and ensure continued, acceptable performance as the system is evolved, progress will quickly grind to a halt.

MORE TODO...




### TODO: Incorporate Ideas from the Following Sources

* Anthropic's post, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"}, provides valuable tips on testing complex agents.

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
