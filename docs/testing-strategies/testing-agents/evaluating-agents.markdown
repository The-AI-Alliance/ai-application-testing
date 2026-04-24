---
layout: default
title: Evaluating Agents
nav_order: 3530
parent: Testing Agents
grand_parent: Testing Strategies and Techniques
has_children: false
---

# Evaluating Agents

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>


We have already seen that testing, i.e., _evaluating_ LLM interactions is hard, because of the stochastic nature of responses. We designed our _simple_ ChatBot to restore determinism, where feasible. The complexity of agent behaviors adds new difficults, which we explore in this chapter.
<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Agent testing starts with the same tools and techniques (e.g., benchmarks) that have been used for models themselves, but more advanced agent workflows require additional tools beyond simple Q&A data pairs.
> 1. The diversity of agent behaviors has led to an explosion of general-purpose and domain-specific benchmarks, as well as some new tools. This trend is driving interest in standardizing how benchmarks are written and executed.

## The Challenges of Writing Agent Evaluations

Anthropic's post, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents){:target="anthropic-evals"}, provides valuable tips on testing complex agents, including new requirements for evaluations that didn't exist when we only focused on evaluating models. Here is a summary of the key points.

* **Agents are multi-turn:** Agents can make several invocations of models, tools, and other agents to accomplish their goals, including several round trips. Analysis of early responses can lead to refining the initial plan, including what work to do next. Most LLM evaluations assume a single invocation and response, like the Q&A pairs we have been using for unit benchmarks. The complexity of agent behaviors make this approach insufficient for agent workflows.
* **Automated evaluations are mandatory:** Software engineers have known for decades that without automated tests, productivity quickly grinds to a halt. Automation is essential for catching regressions and ensuring continued, acceptable performance as the system is evolved. The same argument is true for agent evaluations. Another benefit of automated evaluations is the ability to try new models, agents, and other services with quick evaluation of their efficacy.
* **Tools for agent evaluation:** Anthropic sees three kinds of _graders_ used in evaluations:
    * **Code-based graders:** Non-AI tools like string and regex matching, rules verification, static analysis like linting, typing, and security checks, and analysis of the _agent under test's_ log of activities. These tools are fast and cheap to use, deterministic and hence reproducible, and easy to write and debug. However, they are more brittle to small, but logically-insignificant differences compared to model-based graders and they aren't suitable for more &ldquo;nuanced&rdquo; tasks.
    * **Model-based graders:** Models (generative or not) can analyze results, for example, [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/). They provide greater flexibility, especially for tasks with more &ldquo;nuanced&rdquo; or open-ended behaviors. They can also handle more free-form inputs. However, they are non-deterministic, expensive to run, and require careful human calibration to ensure they work correctly.
    * **Human graders:** Subject matter experts, crowd sourcing, spot checks of samples, A/B testing, etc. They are considered the gold standards for quality, especially where expert-level performance for a domain is required. Often human experts are used to calibrate model-based graders, rather then used to grade agent outputs themselves. Downsides include the fact that humans make mistakes, especially when fatigued, they are expensive and slow, and subject-matter experts may be hard to find.
* **Scoring:** Options include weighted scores that combine results of different graders, binary (all must pass), or a mixture.
* **Capability vs. regression evaluations:** _Capability_ (or _quality_) evaluations ask, "What does this agent do well?" A low pass rate can be expected in the early phases of development. _Regression_ evaluations ask, "Does the agent still handle all the tasks is handled previously?" A high pass rate is required, ideally 100%, but realistically something close to that. Once a capability evaluation has a high pass rate, it can be migrated to the regression evaluations.
* **Examples:** The post discusses evaluation examples for three use cases.
    * **Coding agents:** Agents that perform software development tasks. Deterministic evaluation of code is well established, e.g., unit tests, so deterministic graders can do much of the work evaluating coding agents. There are several, well-known coding-agent benchmarks, too.
    * **Conversational agents:** Our ChatBot application is an example. The quality of the interaction, as well as the outcomes, are important areas to evaluate. Often, a second LLM is used to represent the user of the agent in the conversation. The evaluation is often multidimensional. Was the desired end state reached (sometimes a deterministic state check, but other times a more subjective evaluation suitable for an LLM to perform)? Did it finish within a budget constraint (deterministic)? Was the conversational tone appropriate (subjective - best evaluated by an LLM)?
    * **Research agents:** Agents that gather, synthesize, and analyze information, then prepare a report for human consumption (e.g., the [Deep Research Agent for Applications](https://the-ai-alliance.github.io/deep-research-agent-for-applications/){:target="_blank"} mentioned above). There are partially subjective qualities, like &ldquo;comprehensiveness&rdquo;, &ldquo;well-sourced&rdquo;, and &ldquo;correct&rdquo;, as well as a mix of more objective outcomes, like were particular, essential facts retrieved? Frequent evaluation by human experts is necessary to ensure these agents work as desired.
    * **Computer use agents:** Agents that interact with computer systems the way a human would, such as through a GUI. Often, these agents can be evaluated with deterministic graders, but since they usually work with the DOM (domain object model) of web pages, which can be large and inefficient to process, techniques for optimizing performance are important.
* **How to think about non-determinism in evaluations for agents:** We summarize their discussion of _pass@k_ and _pass^k_ metrics in [Statistical Analysis of Data for Stochastic Systems]({{site.baseurl}}/testing-strategies/statistical-evaluation/#statistical-analysis-of-data-for-stochastic-systems){:target="_blank"}.
* **Going from zero to one: a roadmap to great evals for agents:** The second half of this post provides a roadmap for building agent evaluations.
    * **Collect tasks for the initial eval dataset:**
        * **Step 0. Start early:** Translate early, detected failures into test scenarios. 20-50 examples is a good start. You don't need hundreds to build evaluations.
        * **Step 1. Start with what you already test manually:** Translate manual tests into automated evaluations.
        * **Step 2: Write unambiguous tasks with reference solutions:** Can human agents unambiguously perform a task, based on the specification for it? Do the graders check every outcome and other system change in the specification? Conversely, do the graders make any assumptions that aren't in the specification? A low _pass@k_ result may indicate ambiguities in the specification or graders.
        * **Step 3: Build balanced problem sets:** Test what should happen, but also what should _not_ happen. The post cites an example of testing to ensure that web searches are not done when the information required is already known by the model.
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

Agents may offer the same _de facto_ standard access APIs that LLMs use (like OpenAI API compatibility), promoting some uniformity for runtime use, as well as testing[^2]. However, the proliferation and greater diversity of agents, has led to an explosion of agent tool kits and benchmark suites, both for general-purpose and domain-specific purposes. This trend is driving efforts to standardize how benchmarks are defined and executed.

[^2]: The ChatBot [Working Example]({{site.baseurl}}/working-example) application does this. It provides an OpenAI-compatible API that supports invocation from almost all tools providing inference abstractions. The application also provides an MCP server.

Today, if you want to use a third-party benchmark, you often have to adopt a tool chain specific to that benchmark or somehow adapt the benchmark's core logic and data to whatever tool chain you want to use.

[CUBE Standard](https://github.com/The-AI-Alliance/cube-standard/){:target="cube-standard"} is a new AI Alliance project with the goal of standardizing wrapping of benchmarks so users can adopt and use otherwise-incompatible benchmarks in a uniform way. A companion project, [CUBE Harness](https://github.com/The-AI-Alliance/cube-harness){:target="cube-harness"}, is an evaluation runtime that runs agents against CUBE-compatible benchmarks. [CUBE Registry](https://github.com/The-AI-Alliance/cube-registry/){:target="_cube"} is a community-maintained index of benchmarks that implement the CUBE standard. Any CUBE-compliant evaluation platform or training harness can discover and run registered benchmarks without custom integration.

A key feature of CUBE Standard is support for tasks with multiple steps, which are required for testing agents.

A complementary project is [Every Eval Ever](https://github.com/evaleval/every_eval_ever){:target="eee-gh"} (see [references]({{site.baseurl}}/references/#evaleval-coalition)), which attempts to standardize how evaluation results are reported and catalog all relevant AI evaluations.

## The Role of Simulation

Agents interact with other agents, tools, and systems with often complex behaviors. Evaluation of agents can't always interact with real systems, so _digital twins_ or simulation of such systems is necessary.

Simulation of environments has been an important part of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning){:target="_glossary"} (RL) for a long time. [Gymnasium](https://github.com/Farama-Foundation/Gymnasium){:target="gymnasium"}, the successor to OpenAI's [Gym](https://github.com/openai/gym){:target="oai-gym"}, is a popular framework, for example.

The requirements for simulation environments have evolved as RL's use for model [Post-Training]({{site.glossaryurl}}/#post-Training){:target="_glossary"} has evolved.

The [PyTorch](https://pytorch.org){:target="pytorch"} community recently announced [OpenEnv](https://meta-pytorch.org/OpenEnv/){:target="openenv"}, &ldquo;an end-to-end framework designed to standardize how agents interact with execution environments during reinforcement learning (RL) training.&rdquo; (Other links: [GitHub](https://github.com/meta-pytorch/OpenEnv){:target="openenv-gh"}, [HuggingFace](https://huggingface.co/openenv){:target="hf"}), [HuggingFace blog post](https://huggingface.co/blog/openenv){:target="hf-blog"})

Some of the benefits of OpenEnv compared to other options include better type safety, Docker containers providing both sandbox execution and cluster deployments for scaling, not limited to Python users, and support for sharing environments. 

While oriented towards RL, OpenEnv can be used to build environment simulations for use by agent evaluations, especially where a task's step-by-step _state evolution_ needs to be observed and progress measured.

Similarly, [Patronus AI](https://www.patronus.ai){:target="patronus"} has described a technology they are working on called [Generative Simulators](https://www.patronus.ai/blog/introducing-generative-simulators){:target="patronus"} ([paper](https://patronus.ai/generative-simulators?_gl=1*94dbox*__gcl_au*MTg1ODg5MTQ0OC4xNzcxMzQ1MTg1){:target="patronus-pdf"} - PDF), an outgrowth of their work on various benchmarks, e.g., for the financial sector.

## Benchmarks, Registries, Competitions, and Leaderboards

Several agent benchmarks, registries, competitions, and leaderboards have emerged that are good resources for finding agents that work well, along with the evaluations used to assess them.

* [Agent Beats](https://agentbeats.dev/){:target="agent-beats"} is registry for agents, benchmarks, and a running competition organized by [Berkeley RDI](https://rdi.berkeley.edu/){:target="berkeley-rdi"} and their [Agentic AI MOOC](https://agenticai-learning.org/f25){:target="mooc"}.
* [Humanity's Last Exam](https://lastexam.ai/){:target="lastexam"} (HLE) is addressing the problem that state-of-the-art LLMs are now achieving over 90% accuracy on the most popular benchmarks, limiting informed measurement of capabilities. HLE is a multi-modal benchmark at the frontier of human knowledge, designed to be the _final_, closed-ended academic benchmark of its kind with broad subject coverage. The dataset consists of 2,500 challenging questions across over a hundred subjects. HLE is a global collaborative effort, with questions from nearly 1,000 subject expert contributors affiliated with over 500 institutions across 50 countries, comprised mostly of professors, researchers, and graduate degree holders.
* [Exgentic](https://www.exgentic.ai/){:target="exg"} ([ArXiv paper](https://arxiv.org/abs/2602.22953){:target="arxiv"}) is an open-source leaderboard for general agents. Based on their observations, they conclude that general-purpose agents often outperform specialized agents and the model choice has a bigger impact than the agent framework or patterns used. Model choice also has the biggest impact on the cost profile. 

## Evaluations for Agent Skills

We used [Agent Skills](../building-agents/#agent-skills) in part to implement our agent-based ChatBot, [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"}. Let's discuss how this modularization of functionality helps with evaluation.

TBD

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will complete this section once a working example is provided.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Tools for Agent Development and Testing](../agent-tools/).


---
