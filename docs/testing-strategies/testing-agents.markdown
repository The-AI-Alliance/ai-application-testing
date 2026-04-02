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

So far in this guide, we have focused on testing AI-enabled applications in a generic sense, not focusing on specific concerns for testing LLMs, agents, or other application patterns. This chapter discusses agent testing, which introduces new requirements for testing tools. Effective design patterns and development techniques for agents are also rapidly evolving topics, which we won't attempt to cover here. However, we offer a list of resources and tool kits for further investigation at the [end of this chapter](#agent-development-tools).

[Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} are a broad class of software components with behaviors that are complementary to the capabilities that models themselves provide. They range from relatively simple to very sophisticated. The healthcare ChatBot application is relatively simple. It adds context information to user queries to create prompts and it uses custom handling of the responses. For most use cases, instead of returning the generated text to the user, it presents a message from a limited set of predefined messages, so we have better control over potentially &ldquo;suboptimal&rdquo; generated responses. 

More sophisticated agents include planning, adjustment of the plan based on results (i.e., _course correction_), reasoning, and even autonomous action (when permitted). An example of a more sophisticated agent is the AI Alliance project [Deep Research Agent for Applications](https://the-ai-alliance.github.io/deep-research-agent-for-applications/){:target="_blank"}, which demonstrates an important agent design pattern, <em>Deep Research Agents</em>, with several example applications. (It is built on [LastMile AI's](https://www.lastmileai.dev/){:target="lastmile"} agent framework, [MCP Agent](https://github.com/lastmile-ai/mcp-agent){:target="mcp-agent"}.) An example of an even more advanced agent is [OpenClaw](https://openclaw.ai).

Agents are arguably the most rapidly evolving area of the AI ecosystem right now. While we believe the concepts discussed in this chapter will remain relevant for a long time, specific tools and services mentioned may not.
 
{: .todo}
> **TODO:** 
> 
> This chapter describes some of the unique considerations for implementing and evaluating [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"}. We intend to add a working example based on the work flow _managing appointments_ for the example ChatBot application. See [this issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/39){:target="_blank"} and [Contributing]({{site.baseurl}}/contributing) if you would like to help.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Agent testing can use the same tools and techniques (e.g., benchmarks) that have been used for models themselves, but more advanced agent workflows require additional tools beyond simple Q&A pairs.
> 1. The diversity of agent behaviors has led to an explosion of general-purpose and domain-specific benchmarks, as well as some new tools. This trend is driving interest in standardizing how benchmarks are written and executed.

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
* **How to think about non-determinism in evaluations for agents:** We summarize their discussion of _pass@k_ and _pass^k_ metrics in [Statistical Analysis of Data for Stochastic Systems]({{site.baseurl}}/testing-strategies/statistical-tests/#statistical-analysis-of-data-for-stochastic-systems).
* **Going from zero to one: a roadmap to great evals for agents:** The second half of this post provides a roadmap for building agent evaluations.
    * **Collect tasks for the initial eval dataset:**
        * **Step 0. Start early:** Translate early, detected failures into test scenarios. 20-50 is a good start. You don't need hundreds to build evaluations.
        * **Step 1. Start with what you already test manually:** Translate manual tests into automated evaluations.
        * **Step 2: Write unambiguous tasks with reference solutions:** Can human agents unambiguously perform a task, based on the specification for it? Do the graders check every outcome and other system change in the specification? Conversely, do the graders make any assumptions that aren't in the specification? A low _pass@k_ result may indicate ambiguities in the specification or graders.
        * **Step 3: Build balanced problem sets:** Test what should happen, but also what should _not_ happen. The post cites an example of testing that web searches are not done when the information required is already known by the model.
    * **Design the eval harness and graders:**
        * **Step 4: Build a robust eval harness with a stable environment:** Follow established software testing principles such as begin with a clean environment (to avoid contamination from left-over content - like files - from previous test runs), make the test environment as close to production as possible, etc.
        * **Step 5: Design graders thoughtfully:** Use deterministic graders wherever possible, LLM graders were necessary, and human graders strategically, but sparingly. Avoid brittle graders, like assuming step sequences that aren't required for successful outcomes and would penalize agent &ldquo;creativity&rdquo;. Consider partial credit, e.g., when an agent succeeds in some, but not all tasks. Have human graders calibrate LLM graders. Look for potential &ldquo;cheats&rdquo; in the graders that an agent could exploit to artificially improve its grade.
    * **Maintain and use the eval long-term:**
        * **Step 6: Check the transcripts** Use automated and human review of evaluation transcripts to look for evidence of bugs in the graders, etc. Are the evaluations working as expected.
        * **Step 7: Monitor for capability eval saturation:** Evaluation scores at 100% can be used for regression testing, but won't provide any signal that performance is improving. Often, high scores, but below 100%, will be slow to improve further, because the remaining failing tasks are the most difficult to implement successfully.
        * **Step 8: Keep evaluation suites healthy long-term through open contribution and maintenance:** Evaluations should be owned and maintained by the development team, just like the similar practice for long-term maintenance of unit tests. Proactively build evaluations for forthcoming features and drive their requirements from customer feedback as much as possible.
* **How evals fit with other methods for a holistic understanding of agents:** Evaluations before deployment aren't the end. Production monitoring, A/B testing, human log review, customer feedback, etc. help ensure the features work as desired.

Of course, many of these points apply to AI evaluation in general, not just for agents.
The post ends with an appendix of evaluation frameworks, which we include in [Other Tools for Testing Agents](#other-tools-for-testing-agents) below.

## Standardizing Evaluations

Agents may offer the same _de facto_ standard access APIs that LLMs use (like OpenAI API compatibility), promoting some uniformity for runtime use, as well as testing[^1]. However, the proliferation and greater diversity of agents, has led to an explosion of agent tool kits and benchmark suites, both for general-purpose and domain-specific purposes. This trend is driving efforts to standardize how benchmarks are defined and executed.

[^1]: The ChatBot [Working Example]({{site.baseurl}}/working-example) application does this. It provides an OpenAI-compatible API that supports invocation from almost all tools providing inference abstractions. The application also provides an MCP server.

Today, if you want to use a third-party benchmark, you often have to adopt a tool chain specific to that benchmark or somehow adapt the benchmark's core logic and data to whatever tool chain you want to use.

[CUBE Standard](https://github.com/The-AI-Alliance/cube-standard/){:target="cube-standard"} is a new AI Alliance project with the goal of standardizing wrapping of benchmarks so users can adopt and use otherwise-incompatible benchmarks in a uniform way. A companion project, [CUBE Harness](https://github.com/The-AI-Alliance/cube-harness){:target="cube-harness"}, is an evaluation runtime that runs agents against CUBE-compatible benchmarks. 

A key feature of CUBE Standard is support for tasks with multiple steps, which are required for testing agents.

A complementary project is [Every Eval Ever](https://github.com/evaleval/every_eval_ever){:target="eee-gh"} (see [references]({{site.baseurl}}/references/#evaleval-coalition)), which attempts to standardize how evaluation results are reported and catalog all relevant AI evaluations.

## The Role of Simulation

Agents interact with other agents, tools, and systems with often complex behaviors. Evaluation of agents can't always interact with real systems, so _digital twins_ or simulation of such systems is necessary.

Simulation of environments has been an important part of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning){:target="_glossary"} (RL) for a long time. [Gymnasium](https://github.com/Farama-Foundation/Gymnasium){:target="gymnasium"}, the successor to OpenAI's [Gym](https://github.com/openai/gym){:target="oai-gym"}, is a popular framework, for example.

The requirements for simulation environments have evolved as RL's use for model [Post-Training]({{site.glossaryurl}}/#post-Training){:target="_glossary"} has evolved.

The [PyTorch](https://pytorch.org){:target="pytorch"} community recently announced [OpenEnv](https://meta-pytorch.org/OpenEnv/){:target="openenv"}, &ldquo;an end-to-end framework designed to standardize how agents interact with execution environments during reinforcement learning (RL) training.&rdquo; (Other links: [GitHub](https://github.com/meta-pytorch/OpenEnv){:target="openenv-gh"}, [HuggingFace](https://huggingface.co/openenv){:target="hf"}), [HuggingFace blog post](https://huggingface.co/blog/openenv){:target="hf-blog"})

Some of the benefits of OpenEnv compared to other options include better type safety, Docker containers providing both sandbox execution and cluster deployments for scaling, not limited to Python users, and support for sharing environments. 

While oriented towards RL, OpenEnv can be used to build environment simulations for use by agent evaluations, especially where a task's step-by-step _state evolution_ needs to be observed and progress measured.

Similarly, [Patronus AI](https://www.patronus.ai){:target="patronus"} has described a technology they are working on called [Generative Simulators](https://www.patronus.ai/blog/introducing-generative-simulators){:target="patronus"} ([paper](https://patronus.ai/generative-simulators?_gl=1*94dbox*__gcl_au*MTg1ODg5MTQ0OC4xNzcxMzQ1MTg1) - PDF), an outgrowth of their work on various benchmarks, e.g., for the financial sector.

## Benchmarks, Registries, Competitions, and Leaderboards

Several agent benchmarks, registries, competitions, and leaderboards have emerged that are good resources for finding agents that work well, along with the evaluations used to assess them.

* [Agent Beats](https://agentbeats.dev/){:target="agent-beats"} is registry for agents, benchmarks, and a running competition organized by [Berkeley RDI](https://rdi.berkeley.edu/){:target="berkeley-rdi"} and their [Agentic AI MOOC](https://agenticai-learning.org/f25){:target="mooc"}.
* [Humanity's Last Exam](https://lastexam.ai/){:target="lastexam"} (HLE) is addressing the problem that state-of-the-art LLMs are now achieving over 90% accuracy on the most popular benchmarks, limiting informed measurement of capabilities. HLE is a multi-modal benchmark at the frontier of human knowledge, designed to be the _final_, closed-ended academic benchmark of its kind with broad subject coverage. The dataset consists of 2,500 challenging questions across over a hundred subjects. HLE is a global collaborative effort, with questions from nearly 1,000 subject expert contributors affiliated with over 500 institutions across 50 countries, comprised mostly of professors, researchers, and graduate degree holders.
* [Exgentic](https://www.exgentic.ai/){:target="exg"} ([ArXiv paper](https://arxiv.org/abs/2602.22953){:target="arxiv"}) is an open-source leaderboard for general agents. Based on their observations, they conclude that general-purpose agents often outperform specialized agents and the model choice has a bigger impact than the agent framework or patterns used. Model choice also has the biggest impact on the cost profile. 

<a id="other-tools"/>

## Other Tools for Testing Agents

The following tools meet various requirements for large-scale, enterprise development of agents.

### Arize Phoenix

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Arize Phoenix](https://arize.com/) is an open-source platform for LLM tracing, debugging, and offline or online evaluations. AX is their SaaS offering with additional scalability and other capabilities.

### AssetOpsBench

[AssetOpsBench](https://github.com/IBM/AssetOpsBench){:target="ibm-aob"} from IBM is a unified framework for developing, orchestrating, and evaluating domain-specific AI agents in industrial asset operations and maintenance. It is designed for maintenance engineers, reliability specialists, and facility planners, it allows reproducible evaluation of multi-step workflows in simulated industrial environments.

### Braintrust

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Braintrust](https://www.braintrust.dev/){:target="bt"} integrates offline evaluation with production traces, for example allowing interesting traces to be easily converted into evaluations.

### DoomArena

[DoomArena](https://servicenow.github.io/DoomArena/){:target="_blank"} from [ServiceNow](https://www.servicenow.com/){:target="_blank"} is a framework for testing AI Agents against evolving security threats. It offers a modular, configurable, plug-in framework for testing the security of AI agents across multiple attack scenarios.

DoomArena enables detailed threat modeling, adaptive testing, and fine-grained security evaluations through real-world case studies, such as τ-Bench and BrowserGym. These case studies showcase how DoomArena evaluates vulnerabilities in AI agents interacting in airline customer service and e-commerce contexts.

Furthermore, DoomArena serves as a laboratory for AI agent security research, revealing fascinating insights about agent vulnerabilities, defense effectiveness, and attack interactions.

### Harbor

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [Harbor](https://harborframework.com/){:target="harbor"} is a framework for evaluating and optimizing agents and models in container environments. It can run at scale in cloud environments.

### LangSmith

(Mentioned in the [Anthropic evaluation post](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"})) [LangSmith](https://docs.langchain.com/langsmith/evaluation){:target="ls"}, part of the [LangChain](https://docs.langchain.com/){:target="lc"} ecosystem, integrates offline and online evaluation.
[Langfuse](https://langfuse.com){:target="lf"} offers similar capabilities in an open-source package that support on-premise use.

### LastMile AI's MCP Eval

[MCP Eval](https://mcp-eval.ai/){:target="mcp-eval"} is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation. It is built on [MCP Agent](https://mcp-agent.com/){:target="mcp-agent"}, their agent framework that emphasizes MCP as the communication protocol.

<a id="agent-development-tools"></a>

## Agent Development Tools

There is a rapidly growing list of tools for developing agents. In addition to many of the tools mentioned above, Here, we list a few that offer &ldquo;non-trivial&rdquo; integrated support for evaluation.

* OpenAI's [AGENTS.md](https://agents.md/){:target="oaia"} ([GitHub](https://github.com/agentsmd/agents.md){:target="oaia-gh"} is a simple Markdown format for guiding coding agents. They describe it as a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on projects.
* [CUGA](https://cuga.dev/){:target="cuga"} (_ConfigUrable Generalist Agent_) ([GitHub](https://github.com/cuga-project/cuga-agent){:target="cuga-gh"}, [IBM blog post](https://research.ibm.com/blog/cuga-agent-framework){:target="ibm-blog"}, [HuggingFace blog post](https://huggingface.co/blog/ibm-research/cuga-on-hugging-face){:target="cuga-hf"}) is an agent framework from IBM Research that is purpose-built for enterprise automation. It integrates several popular agentic patterns, such as [ReAct](https://agent-patterns.readthedocs.io/en/stable/patterns/react.html){:target="agent-patterns"}, [CodeAct](https://machinelearning.apple.com/research/codeact){:target="codeact1"} (and [here](https://notes.muthu.co/2025/12/the-most-interesting-ai-agent-design-pattern-right-now/){:target="codeact2"}), and [Planner-Executor](https://medium.com/@jaouadi.mahdi1/separating-ai-agents-into-planner-and-executor-7705b58d79fd){:target="pe"}. CUGA provides a modular architecture enabling trustworthy, policy-aware, and composable automation across web interfaces, APIs, and custom enterprise systems. It also takes evaluation seriously, with built-in tools and examples.
    * A related, more recent project from the same team is [Agent Lifecycle Toolkit](https://agenttoolkit.github.io/agent-lifecycle-toolkit/){:target="altk"}, which helps agent builders create better performing agents by addressing errors, like failure to follow instructions, struggling to find the right tool to use, violating business rules.
* Google's [Agent Development Kit](https://google.github.io/adk-docs/){:target="adk"} has a chapter called [Why Evaluate Agents?](https://google.github.io/adk-docs/evaluate/){:target="adk"}, which provides tips for writing evaluations specifically tailored for agents.
* [Mozilla AI's](https://www.mozilla.ai){:target="mozilla"} [`any-agent`](https://github.com/mozilla-ai/any-agent){:target="mozilla"} ([blog post](https://www.mozilla.ai/open-tools/choice-first-stack/any-agent){:target="mozilla"}) abstracts over other agent frameworks, providing common services like observability with the ability to switch out agent frameworks as needed.
* [`weave-cli`](https://github.com/maximilien/weave-cli) is a tool for working with vector databases and related agents more easily. It has built-in features for running evaluations.

## Agent Skills

TODO: The concept of _skills_ is getting a lot of attention.

## Other References on Agent Development

The following resources offer useful guidance on various aspects of agent development.

* [Anthropic's](https://www.anthropic.com){:target="anthropic"} influential post, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system){:target="anthropic"}, offers useful tips for building effective agents.
* [Prioritizing Real-Time Failure Detection in AI Agents](https://partnershiponai.org/resource/prioritizing-real-time-failure-detection-in-ai-agents/){:target="poai"} from the [Partnership on AI](https://partnershiponai.org/){:target="poai"} offers guidance on accessing the potential impact of various failures and where to prioritize early detection and handling.
* [CoSAI](https://www.coalitionforsecureai.org/){:target="cosai"}, the Coalition for Secure AI, has published [The Future of Agentic Security: From ChatBots to Intelligent Swarms](https://github.com/cosai-oasis/cosai-tsc/blob/main/the-future-of-agentic-security.pdf){:target="cosai-pdf"}, a definitive guide of the potential security risks posed by agents and how to mitigate them.

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will complete this section once a working example is provided.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Advanced Techniques]({{site.baseurl}}/advanced-techniques/).

---
