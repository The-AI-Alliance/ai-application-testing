---
layout: default
title: Tools for Agent Development and Testing
nav_order: 3590
parent: Testing Agents
grand_parent: Testing Strategies and Techniques
has_children: false
---

# Tools for Agent Development and Testing

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

The previous chapters discussed several agent implementation and testing tools we used, specifically [Langchain's _Deep Agents_](https://www.langchain.com/deep-agents){:target="lcda"} library and [Agent Skills](#agent-skills). 

TBD - evaluation tools...

This chapter lists some other tools for implementation and evaluation that may be of interest. You can skip this chapter if you aren't interested in exploring additional tools.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. What tools have you used? Feedback is welcome on the list hear, especially experiences with any of the tools mentioned. What tools should we add?

<a id="other-tools"/>

<a id="agent-development-tools"></a>

We group these tools into development and testing categories, although there is some overlap. Each category is listed in alphabetical order.

## Agent Development Tools

There is a rapidly growing list of tools for developing agents. In addition to many of the tools mentioned above, Here, are some additional for consideration, all of which offer integrated support for evaluation, in one form or another.

### Agent Development Kit

Google's [Agent Development Kit](https://google.github.io/adk-docs/){:target="adk"} provides general guidance on building agents. It also has a chapter called [Why Evaluate Agents?](https://google.github.io/adk-docs/evaluate/){:target="adk"}, which provides tips for writing evaluations specifically tailored for agents.

### `AGENTS.md`

Similar in spirit to [Skills]({{site.baseurl}}/testing-strategies/testing-agents/building-agents/#agent-skills), OpenAI's [AGENTS.md](https://agents.md/){:target="oaia"} ([GitHub](https://github.com/agentsmd/agents.md){:target="oaia-gh"} is a simple Markdown format for guiding coding agents. They describe it as a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on projects.

### Any Agent

[Mozilla AI's](https://www.mozilla.ai){:target="mozilla"} [`any-agent`](https://github.com/mozilla-ai/any-agent){:target="mozilla"} ([blog post](https://www.mozilla.ai/open-tools/choice-first-stack/any-agent){:target="mozilla"}) abstracts over other agent frameworks, providing common services like observability with the ability to switch out agent frameworks as needed.

### CUGA - ConfigUrable Generalist Agent

[CUGA](https://cuga.dev/){:target="cuga"} (_ConfigUrable Generalist Agent_) ([GitHub](https://github.com/cuga-project/cuga-agent){:target="cuga-gh"}, [IBM blog post](https://research.ibm.com/blog/cuga-agent-framework){:target="ibm-blog"}, [HuggingFace blog post](https://huggingface.co/blog/ibm-research/cuga-on-hugging-face){:target="cuga-hf"}) is an agent framework from IBM Research that is purpose-built for enterprise automation.

CUGA integrates several popular agentic patterns, such as [ReAct](https://agent-patterns.readthedocs.io/en/stable/patterns/react.html){:target="agent-patterns"}, [CodeAct](https://machinelearning.apple.com/research/codeact){:target="codeact1"} (and [here](https://notes.muthu.co/2025/12/the-most-interesting-ai-agent-design-pattern-right-now/){:target="codeact2"}), and [Planner-Executor](https://medium.com/@jaouadi.mahdi1/separating-ai-agents-into-planner-and-executor-7705b58d79fd){:target="pe"}. 

CUGA provides a modular architecture enabling trustworthy, policy-aware, and composable automation across web interfaces, APIs, and custom enterprise systems. It also takes evaluation seriously, with built-in tools and examples.

A related, more recent project from the same team is [Agent Lifecycle Toolkit](https://agenttoolkit.github.io/agent-lifecycle-toolkit/){:target="altk"}, which helps agent builders create better performing agents by addressing errors, like failure to follow instructions, struggling to find the right tool to use, violating business rules.

### Weave CLI

[`weave-cli`](https://github.com/maximilien/weave-cli){:target="weave-cli"} is a tool for working with vector databases and related agents more easily. It has built-in features for running evaluations.

### Other References on Agent Development

The following resources offer useful guidance on various aspects of agent development.

* [Anthropic's](https://www.anthropic.com){:target="anthropic"} influential post, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system){:target="anthropic"}, offers useful tips for building effective agents.
* [Prioritizing Real-Time Failure Detection in AI Agents](https://partnershiponai.org/resource/prioritizing-real-time-failure-detection-in-ai-agents/){:target="poai"} from the [Partnership on AI](https://partnershiponai.org/){:target="poai"} offers guidance on accessing the potential impact of various failures and where to prioritize early detection and handling.
* [CoSAI](https://www.coalitionforsecureai.org/){:target="cosai"}, the Coalition for Secure AI, has published [The Future of Agentic Security: From ChatBots to Intelligent Swarms](https://github.com/cosai-oasis/cosai-tsc/blob/main/the-future-of-agentic-security.pdf){:target="cosai-pdf"}, a definitive guide of the potential security risks posed by agents and how to mitigate them.

## Agent Evaluation and Testing Tools

Some of the tools listed above also support evaluation and testing, e.g., Google's [Agent Development Kit](#agent-development-kit).

### Arize Phoenix

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Arize Phoenix](https://arize.com/){:target="arize"} is an open-source platform for LLM tracing, debugging, and offline or online evaluations. AX is their SaaS offering with additional scalability and other capabilities.

### AssetOpsBench

[AssetOpsBench](https://github.com/IBM/AssetOpsBench){:target="ibm-aob"} from IBM is a unified framework for developing, orchestrating, and evaluating domain-specific AI agents in industrial asset operations and maintenance. It is designed for maintenance engineers, reliability specialists, and facility planners, it allows reproducible evaluation of multi-step workflows in simulated industrial environments.

### Braintrust

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Braintrust](https://www.braintrust.dev/){:target="bt"} integrates offline evaluation with production traces, for example allowing interesting traces to be easily converted into evaluations.

### Benchmarks, Registries, Competitions, and Leaderboards

Several agent benchmarks, registries, competitions, and leaderboards have emerged that are good resources for finding agents that work well, along with the evaluations used to assess them.

* [Agent Beats](https://agentbeats.dev/){:target="agent-beats"} is registry for agents, benchmarks, and a running competition organized by [Berkeley RDI](https://rdi.berkeley.edu/){:target="berkeley-rdi"} and their [Agentic AI MOOC](https://agenticai-learning.org/f25){:target="mooc"}.
* [Humanity's Last Exam](https://lastexam.ai/){:target="lastexam"} (HLE) is addressing the problem that state-of-the-art LLMs are now achieving over 90% accuracy on the most popular benchmarks, limiting informed measurement of capabilities. HLE is a multi-modal benchmark at the frontier of human knowledge, designed to be the _final_, closed-ended academic benchmark of its kind with broad subject coverage. The dataset consists of 2,500 challenging questions across over a hundred subjects. HLE is a global collaborative effort, with questions from nearly 1,000 subject expert contributors affiliated with over 500 institutions across 50 countries, comprised mostly of professors, researchers, and graduate degree holders.
* [Exgentic](https://www.exgentic.ai/){:target="exg"} ([ArXiv paper](https://arxiv.org/abs/2602.22953){:target="arxiv"}) is an open-source leaderboard for general agents. Based on their observations, they conclude that general-purpose agents often outperform specialized agents and the model choice has a bigger impact than the agent framework or patterns used. Model choice also has the biggest impact on the cost profile. 

### CUBE 

The _CUBE_ (Common Unified Benchmark Environment) projects were discussed in See the [Testing Agents](({{site.baseurl}}/testing-strategies/testing-agents/evaluating-agents/) chapter for more details on these projects, as well as the [References]({{site.baseurl}}/references/#servicenow). In short, they attempt to standardize techniques for building agent evaluations, along with an effort to build and catalog evaluations built to the standard.

### DoomArena

[DoomArena](https://servicenow.github.io/DoomArena/){:target="_blank"} is a framework for testing AI Agents against evolving security threats. It offers a modular, configurable, plug-in framework for threat modeling and testing the security of AI agents across multiple attack scenarios. See the [References]({{site.baseurl}}/references/#servicenow) for more details.

### Harbor

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Harbor](https://harborframework.com/){:target="harbor"} is a framework for evaluating and optimizing agents and models in container environments. It can run at scale in cloud environments.

### LangSmith

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [LangSmith](https://docs.langchain.com/langsmith/evaluation){:target="ls"}, part of the [LangChain](https://docs.langchain.com/){:target="lc"} ecosystem, integrates offline and online evaluation.
[Langfuse](https://langfuse.com){:target="lf"} offers similar capabilities in an open-source package that support on-premise use.

### LastMile AI's MCP Eval

[MCP Eval](https://mcp-eval.ai/){:target="mcp-eval"} is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation. It is built on [MCP Agent](https://mcp-agent.com/){:target="mcp-agent"}, their agent framework that emphasizes MCP as the communication protocol.

### Simulation Tools

Agents interact with other agents, tools, and systems with often complex behaviors. Evaluation of agents can't always interact with real systems, so _digital twins_ or simulation of such systems is necessary.

Simulation of environments has been an important part of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning){:target="_glossary"} (RL) for a long time. [Gymnasium](https://github.com/Farama-Foundation/Gymnasium){:target="gymnasium"}, the successor to OpenAI's [Gym](https://github.com/openai/gym){:target="oai-gym"}, is a popular framework, for example.

The requirements for simulation environments have evolved as RL's use for model [Post-Training]({{site.glossaryurl}}/#post-Training){:target="_glossary"} has evolved.

The [PyTorch](https://pytorch.org){:target="pytorch"} community recently announced [OpenEnv](https://meta-pytorch.org/OpenEnv/){:target="openenv"}, &ldquo;an end-to-end framework designed to standardize how agents interact with execution environments during reinforcement learning (RL) training.&rdquo; (Other links: [GitHub](https://github.com/meta-pytorch/OpenEnv){:target="openenv-gh"}, [HuggingFace](https://huggingface.co/openenv){:target="hf"}), [HuggingFace blog post](https://huggingface.co/blog/openenv){:target="hf-blog"})

Some of the benefits of OpenEnv compared to other options include better type safety, Docker containers providing both sandbox execution and cluster deployments for scaling, not limited to Python users, and support for sharing environments. 

While oriented towards RL, OpenEnv can be used to build environment simulations for use by agent evaluations, especially where a task's step-by-step _state evolution_ needs to be observed and progress measured.

Similarly, [Patronus AI](https://www.patronus.ai){:target="patronus"} has described a technology they are working on called [Generative Simulators](https://www.patronus.ai/blog/introducing-generative-simulators){:target="patronus"} ([paper](https://patronus.ai/generative-simulators?_gl=1*94dbox*__gcl_au*MTg1ODg5MTQ0OC4xNzcxMzQ1MTg1){:target="patronus-pdf"} - PDF), an outgrowth of their work on various benchmarks, e.g., for the financial sector.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to the [Advanced Techniques]({{site.baseurl}}/advanced-techniques/) section of chapters.

---
