---
layout: default
title: References
nav_order: 80
---

# References

References for more details on testing, especially in the AI context, and other topics. Note that outside references to particular tools that are mentioned in this web site are not repeated here. 

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Adrian Cockcroft

[Dean Wampler]({{site.baseurl}}/contributing/#contributors) and [Adrian Cockcroft](https://mastodon.social/@adrianco){:target="adrian"} exchanged [messages on Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} about lessons learned at Netflix, which are quoted in several sections of this website. See also [Dean Wampler](#dean-wampler) and the discussion in [Testing Problems Caused by Generative AI Nondeterminism]({{site.baseurl}}/testing-problems).

## AI for Education

The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}.

### Allen Institute of AI

[Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} from the Allen Institute of AI is discussed by [Nathan Lambert](#nathan-lambert) below. It tries to meet similar goals as [InstructLab](#redhat). See [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/) for more details.

## Alignment Forum

The [Alignment Forum](https://www.alignmentforum.org/){:target="alignment-forum"} works on many aspects of alignment.

## Babeş-Bolyai University

[Synthetic Data Generation Using Large Language Models: Advances in Text and Code](https://arxiv.org/abs/2503.14023){:target="_blank"} surveys techniques that use LLMs, like we are explore in the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter and elsewhere.

## CVS Health Data Science Team

[CVS](https://www.cvshealth.com){:target="_blank"}, the US-based retail pharmacy and healthcare services company, has a large data science team. They recently open-sourced [`uqlm`](https://github.com/cvs-health/uqlm){:target="_blank"}, where _UQLM_ stands for _Uncertainty Quantification for Language Models_. It is a Python package for UQ-based LLM hallucination detection.

Among the useful tools in this repository are:
* A [concise summary](https://github.com/meta-llama/synthetic-data-kit/blob/main/use-cases/awesome-synthetic-data-papers/ReadMe.MD){:target="_blank"} of best practices and tools for synthetic data generation.
* Tuning models to [improve Chain of Thought reasoning](https://github.com/meta-llama/synthetic-data-kit/blob/main/use-cases/adding_reasoning_to_llama_3/README.md){:target="_blank"}.

## Dean Wampler

In [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"} [Dean Wampler](http://deanwampler.com){:target="dw"} (one of this project's [contributors]({{site.baseurl}}/contributing/#contributors)) summarizes the work of this project. After posting the link to the slides, Dean and [Adrian Cockcroft](#adrian-cockcroft) discussed lessons learned at Netflix, which have informed this project's content.

### Ekimetrics

[ClairBot](https://clair.bot/){:target="clairbot"} from the Responsible AI Team at [Ekimetrics](https://ekimetrics.com/){:target="ekimetrics"} is a research project that compares several model responses for domain-specific questions, where each of the models has been tuned for a particular domain, in this case ad serving, laws and regulations, and social sciencies and ethics. See also the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter.

## EleutherAI

[EleutherAI's](https://www.eleuther.ai/){:target="eleuther"} definition of [Alignment](https://www.eleuther.ai/alignment){:target="eleuther"} is quoted in the glossary definition for it.

## Elvis Saravia

Elvis Saravia's [Prompt Engineering Guide](https://www.promptingguide.ai/){:target="_blank"}, part of his [DAIR.AI](https://www.dair.ai/){:target="_blank"} learning academy, provides in depth information on [Prompt Engineering]({{site.glossaryurl}}/#prompt-engineering){:target="_glossary"}.

## Evan Miller

[Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"} is a research paper arguing that _evaluations_ (see the [Trust and Safety Evaluation Initiative](https://the-ai-alliance.github.io/trust-safety-evals/){:target="tsei"} for more details) should use proper statistical analysis of their results. It is discussed in [Statistical Evaluation]({{site.baseurl}}/testing-strategies/statistical-tests/).

## Google

Google's [Agent Development Kit](https://google.github.io/adk-docs/){:target="adk"} has a chapter called [Why Evaluate Agents?](https://google.github.io/adk-docs/evaluate/){:target="adk"}, which provides tips for writing evaluations specifically tailored for agents. See the discussion in the [Testing Agents](({{site.baseurl}}/testing-strategies/testing-agents/) chapter.

## Hamel Husain

[Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/){:target="_blank"} is a long blog post that discusses testing of AI applications and makes many of the same points this user guide makes.

## IBM

### RAG

This IBM blog post, [What is retrieval-augmented generation?](https://research.ibm.com/blog/retrieval-augmented-generation-RAG){:target="ibm-rag"} provides a good overview of [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"}.

### Evaluation and Benchmark Tools

For the following tool, see the [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) chapter for more details:

* [EvalAssist](https://ibm.github.io/eval-assist/){:target="eval-assist"} ([paper](https://arxiv.org/abs/2410.00873v2){:target="_blank"}) is designed to make LLM as a Judge evaluations of data easier for users, including incremental refinement of the evaluation criteria using a web-based user experience. EvalAssist supports direct assessment (scoring) of data individually, which we used in our [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) chapter, or pair-wise comparisons, where the best of two answers is chosen. 

For the following tool, see the [Testing Agents](({{site.baseurl}}/testing-strategies/testing-agents/) chapter for more details:

* [AssetOpsBench](https://github.com/IBM/AssetOpsBench){:target="ibm-aob"} is a unified framework for developing, orchestrating, and evaluating domain-specific AI agents in industrial asset operations and maintenance. It is designed for maintenance engineers, reliability specialists, and facility planners, it allows reproducible evaluation of multi-step workflows in simulated industrial environments.

For the following tools, see the [Unit Benchmarks](({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter for more details:

* [FailureSensorIQ](https://github.com/IBM/FailureSensorIQ){:target="faiq"} is a data set for multiple aspects of reasoning through failure modes, sensor data, and the relationships between them across various industrial assets. 
* [FIBEN Benchmark](https://github.com/IBM/fiben-benchmark){:target="_blank"} is a finance data set benchmark for natural language queries.
* [HELM Enterprise Benchmark](https://github.com/IBM/helm-enterprise-benchmark){:target="heb"} is an enterprise benchmark framework for LLM evaluation. It extends [HELM](https://crfm.stanford.edu/helm/lite/latest/){:target="helm"}, an open-source benchmark framework developed by [Stanford CRFM](https://crfm.stanford.edu/helm/lite/latest/){:target="crfm"}, to enable users evaluate LLMs with domain-specific data sets such as finance, legal, climate, and cybersecurity. 

## James Thomas

[James Thomas](https://bsky.app/profile/hiccupps.bsky.social){:target="jt"} is a QA engineer who [posted](https://bsky.app/profile/hiccupps.bsky.social/post/3lgms2z6zuk25){:target="bsky-jt"} a link to a blog post [How do I Test AI?](https://qahiccupps.blogspot.com/2025/01/how-do-i-test-ai.html){:target="blog-jt"} that lists criteria to consider when testing AI-enabled systems. While the post doesn't provide a lot of details behind the list items, the list is excellent for stimulating further investigation.

## Jiayi Yuan, et al.

_Give Me FP32 or Give Me Death? Challenges and Solutions for Reproducible Reasoning_ [paper](https://arxiv.org/abs/2506.09501){:target="_blank"} examines the influence of floating point precision on the reproducibility of inference results, even when randomness is restricted, such as using a low "temperature". Of course, the theme of our project is dealing with the inherent randomness of inference, but there are also times when limiting that randomness is important.

## John Snow Labs and Pacific.ai

John Snow Labs has created [langtest](https://langtest.org/){:target="_blank"}, a test generation and execution framework with &ldquo;60+ test types for comparing LLM & NLP models on accuracy, bias, fairness, robustness & more.&rdquo;

The affiliated company [Pacific.ai](https://pacific.ai/){:target="_blank"} offers a commercial [testing system](https://pacific.ai/testing/){:target="_blank"} with similar features.

## LastMile AI

[MCP Eval](https://mcp-eval.ai/){:target="mcp-eval"} is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation. It is built on [MCP Agent](https://mcp-agent.com/){:target="mcp-agent"}, their agent framework that emphasizes MCP as the communication protocol. See the [Testing Agents](({{site.baseurl}}/testing-strategies/testing-agents/) chapter for more details.


## Merriam-Webster Dictionary

The [Merriam-Webster Dictionary](https://www.merriam-webster.com/dictionary/){:target="dict"}: is quoted in our [Glossary]({{site.glossaryurl}}){:target="_glossary"} for several terms.

## Meta

Meta's [`synthetic-data-kit`](https://github.com/meta-llama/synthetic-data-kit/){:target="_blank"} provides scalable support for larger-scale data synthesis and processing (such as translating between formats), especially for model [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} with Llama models. See the [Unit Benchmarks](({{site.baseurl}}/testing-strategies/unit-benchmarks/) and the [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning)) chapters for more details.

The [Llama Stack](https://github.com/llamastack/llama-stack/){:target="ls"} project provides a [Kubernetes Benchmark](https://github.com/llamastack/llama-stack/tree/main/benchmarking/k8s-benchmark){:target="ls-kb"} suite.

## Michael Feathers

[Michael Feathers](https://michaelfeathers.silvrback.com){:target="michael-feathers"} gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024, which is discussed in [Abstractions Encapsulate Complexities]({{site.baseurl}}/arch-design/component-design/#abstractions-encapsulate-complexities).

## MLCommons Glossary

The [MLCommons](https://mlcommons.org/){:target="mlcommons"} AI Safety v0.5 Benchmark Proof of Concept [Technical Glossary](https://drive.google.com/file/d/1X9Sy8eRiYgbeBBVMMqNrDEq4KzHZynpF/view?usp=sharing){:target="mlc-glossary"} is used to inform our [Glossary]({{site.glossaryurl}}){:target="_glossary"}.

## Nathan Lambert

[How to approach post-training for AI applications](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"}, a tutorial presented at [NeurIPS 2024](https://neurips.cc/Conferences/2024){:target="neurips"} by [Nathan Lambert](https://www.natolambert.com/){:target="nathan-lambert"}. The same content can be found in [this Interconnects blog post](https://www.interconnects.ai/p/frontier-model-post-training){:target="nl"}. [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/) discusses these ideas. See also [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}. See also the [Allen Institute of AI](#allen-institute-of-ai) entry above.

## NIST Risk Management Framework

The U.S. National Institute of Science and Technology's ([NIST](https://www.nist.gov/){:target="nist"}) Artificial Intelligence [Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework){:target="nist-rmf"} (AI RMF 1.0) is used to inform our [Glossary]({{site.glossaryurl}}){:target="_glossary"}.

## OpenAI

An [OpenAI](https://openai.com){:target="openai"} [paper](https://openai.com/form/rft-research-program/){:target="openai-rf"} on _reinforcement fine tuning_ is discussed in [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/).

[Announcing OpenAI Pioneers Program](https://openai.com/index/openai-pioneers-program/){:target="_blank"} announced _OpenAI Pioneers Program_, an effort designed to help application developers optimize model performance in their domains.

## Open Data Science

[Nine Open-Source Tools to Generate Synthetic Data](https://opendatascience.com/9-open-source-tools-to-generate-synthetic-data/){:target="_blank"} lists several tools that use different approaches for data generation. See the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks) chapter for more details.

## Patronus

The Patronus guide, [LLM Testing: The Latest Techniques & Best Practices](https://www.patronus.ai/llm-testing){:target="patronus"}, discusses the unique testing challenges raised by generative AI and discusses various techniques for testing these systems.

[FinanceBench](https://github.com/patronus-ai/financebench){:target="finance-bench"} is their benchmark for finance applications. See the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks) chapter for more details.

[Evaluating Copyright Violations in LLMs](https://github.com/patronus-ai/copyright-evals){:target="ecvil"} has data and tools for detecting examples of responses that violate one or more copyrights. (This work isn't discussed elsewhere in this user guide.)

## PlurAI

[Plurai.ai](https://plurai.ai){:target="_blank"} recently created an open-source project called [Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} that demonstrates how to exploit some recent research on automated generation of test data, knowledge graphs based on the constraints and requirements for an application, and automated test generation to verify alignment of the system to the requirements. These techniques are designed to provide more exhaustive test coverage of behaviors, including catching corner cases. See the [Statistical Evaluation]({{site.baseurl}}/testing-strategies/statistical-evaluation/) chapter for more details.

## RedHat

[InstructLab](https://instructlab.ai){:target="instructlab"} is a project started by [IBM Research](https://research.ibm.com){:target="ibm"} and developed by [RedHat](https://redhat.com){:target="redhat"}. InstructLab provides conventions for organizing specific, manually-created examples into a domain hierarchy, along with tools to perform model tuning, including synthetic data generation. Hence, InstructLab is an alternative way to generate synthetic data for [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks). See also [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/).

## RedMonk

The analyst firm [RedMonk](https://redmonk.com/){:target="redmonk"} posted [this interesting piece](https://redmonk.com/rstephens/2025/07/31/spec-vs-vibes/){:target="redmonk-spec"} on [Specification-Driven Development]({{site.baseurl}}/future-ideas/sdd/).

## ServiceNow

[DoomArena](https://servicenow.github.io/DoomArena/){:target="_blank"} is a framework for testing AI Agents against evolving security threats. It offers a modular, configurable, plug-in framework for testing the security of AI agents across multiple attack scenarios.

DoomArena enables detailed threat modeling, adaptive testing, and fine-grained security evaluations through real-world case studies, such as τ-Bench and BrowserGym. These case studies showcase how DoomArena evaluates vulnerabilities in AI agents interacting in airline customer service and e-commerce contexts.

Furthermore, DoomArena serves as a laboratory for AI agent security research, revealing fascinating insights about agent vulnerabilities, defense effectiveness, and attack interactions. See the [Testing Agents](({{site.baseurl}}/testing-strategies/testing-agents/) chapter for more details.

## Specification-Driven Development

SDD is a more structured approach to prompting LLMs and doing explicit &ldquo;phases&rdquo; like planning vs. task execution, so LLMs can do a better job generating production-quality code that meets our requirements. Here we list many references. See the discussion in the [Specification-Driven Development]({{site.baseurl}}/future-ideas/sdd/) chapter, where we explore them.

* [How I Apply Spec-Driven AI Coding](https://finfluencers.trade/blog/2025/07/22/how-i-apply-spec-driven-ai-coding/){:target="_blank"}
  * [`spec-driven-ai-coding` repo](https://github.com/andreskull/spec-driven-ai-coding){:target="_blank"}
  * Inspirations:
    * [My current AI coding workflow](https://carlrannaberg.medium.com/my-current-ai-coding-workflow-f6bdc449df7f){:target="_blank"}
    * [My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/){:target="_blank"}
* Spec Kit
  * [Spec-driven development with AI: Get started with a new open source toolkit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/){:target="_blank"}
  * [Diving Into Spec-Driven Development With GitHub Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit){:target="_blank"}
  * [Spec Kit website](https://speckit.org/){:target="_blank"}
  * [Spec Kit repo](https://github.com/github/spec-kit){:target="_blank"}
* [AWS Kiro](https://kiro.dev/){:target="_blank"}, an AI IDE designed to support specification-driven development.

## University of Tübingen

[Beyond Benchmarks: A Novel Framework for Domain-Specific LLM Evaluation and Knowledge Mapping](https://arxiv.org/abs/2506.07658){:target="_blank"} is a research effort that explores an alternative approach to knowledge representations, like the Q&A pairs we use in this guide for benchmarks, without using LLMs for generating data. See the [Unit Benchmarks](({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter for more details.

## Unsloth

[Unsloth](https://unsloth.ai/){:target="unsloth"} is an OSS tool suite for model training and tuning. Their documentation includes guides for the following:
* [Fine-tuning LLMs](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide){:target="unsloth-ft"}
* [Reinforcement Learning](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide){:target="unsloth-rl"}

## Wikipedia

Many [Wikipedia](https://en.wikipedia.org/wiki/){:target="wikipedia"} articles are used as references in our [Glossary]({{site.glossaryurl}}){:target="_glossary"} and other locations.

* [Bertrand Meyer](https://en.wikipedia.org/wiki/Bertrand_Meyer){:target="_wikipedia"}
* [Cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="_wikipedia"}
* [Design by contract](https://en.wikipedia.org/wiki/Design_by_contract){:target="_wikipedia"}
* [DevOps](https://en.wikipedia.org/wiki/DevOps){:target="_wikipedia"}
* [Eiffel (programming language)](https://en.wikipedia.org/wiki/Eiffel_(programming_language)){:target="_wikipedia"}
* [Deferent and epicycle](https://en.wikipedia.org/wiki/Deferent_and_epicycle){:target="_wikipedia"}
* [Generative adversarial network](https://en.wikipedia.org/wiki/Generative_adversarial_network){:target="_wikipedia"}
* [SQL injection](https://en.wikipedia.org/wiki/SQL_injection){:target="_wikipedia"}
* [Test-driven development](https://en.wikipedia.org/wiki/Test-driven_development){:target="_wikipedia"} 
* [Transmission Control Protocol](https://en.wikipedia.org/wiki/Transmission_Control_Protocol){:target="_wikipedia"}
