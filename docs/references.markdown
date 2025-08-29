---
layout: default
title: References
nav_order: 80
---

# References

References for more details on testing, especially in the AI context. Note that outside references to particular tools are not shown here.

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Adrian Cockcroft

[Dean Wampler]({{site.baseurl}}/contributing/#contributors) and [Adrian Cockcroft](https://mastodon.social/@adrianco){:target="adrian"} exchanged [messages on Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} about lessons learned at Netflix, which are quoted in several sections of this website. See also [Dean Wampler](#dean-wampler)

## AI for Education

The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}

## Alignment Forum

The [Alignment Forum](https://www.alignmentforum.org/){:target="alignment-forum"} works on many aspects of alignment.

## CVS Health

[CVS](https://www.cvshealth.com){:target="_blank"}, the US-based retail pharmacy and healthcare services company, has a large data science team. They recently open-sourced [`uqlm`](https://github.com/cvs-health/uqlm){:target="_blank"}, where _UQLM_ stands for _Uncertainty Quantification for Language Models_. It is a Python package for UQ-based LLM hallucination detection.

Among the useful tools in this repo are:
* A [concise summary](https://github.com/meta-llama/synthetic-data-kit/blob/main/use-cases/awesome-synthetic-data-papers/ReadMe.MD){:target="_blank"} of best practices and tools for synthetic data generation.
* Tuning models to [improve Chain of Thought reasoning](https://github.com/meta-llama/synthetic-data-kit/blob/main/use-cases/adding_reasoning_to_llama_3/README.md){:target="_blank"}.

## Dean Wampler

In [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"} [Dean Wampler](http://deanwampler.com){:target="dw"} (one of this project's [contributors]({{site.baseurl}}/contributing/#contributors)) summarizes the work of this project. After posting the link to the slides, Dean and [Adrian Cockcroft](#adrian-cockcroft) discussed lessons learned at Netflix, which have informed this project's content.

### Ekimetrics

[ClairBot](https://clair.bot/){:target="clairbot"} from the Responsible AI Team at [Ekimetrics](https://ekimetrics.com/){:target="ekimetrics"} is a research project that compares several model responses for domain-specific questions, where each of the models has been tuned for a particular domain, in this case ad serving, laws and regulations, and social sciencies and ethics.

## EleutherAI

[EleutherAI's](https://www.eleuther.ai/){:target="eleuther"} definition of [Alignment](https://www.eleuther.ai/alignment){:target="eleuther"} is quoted in the glossary definition for it.

## Evan Miller

[Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"} is a research paper arguing that _evaluations_ (see the [Trust and Safety Evaluation Initiative](https://the-ai-alliance.github.io/trust-safety-evals/){:target="tsei"} for more details) should use proper statistical analysis of their results. It is discussed in [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests/).

## James Thomas

[James Thomas](https://bsky.app/profile/hiccupps.bsky.social){:target="jt"} is a QA engineer who [posted](https://bsky.app/profile/hiccupps.bsky.social/post/3lgms2z6zuk25){:target="bsky-jt"} a link to a blog post [How do I Test AI?](https://qahiccupps.blogspot.com/2025/01/how-do-i-test-ai.html){:target="blog-jt"} that lists criteria to consider when testing AI-enabled systems. While the post doesn't provide a lot of details behind the list items, the list is excellent for stimulating further investigation.

## Jiayi Yuan, et al.

_Give Me FP32 or Give Me Death? Challenges and Solutions for Reproducible Reasoning_ [paper](https://arxiv.org/abs/2506.09501){:target="_blank"} examines the influence of floating point precision on the reproducibility of inference results, even when randomness is restricted, such as using a low "temperature". Of course, the theme of our project is dealing with the inherent randomness of inference, but there are also times when limiting that randomness is important.

## John Snow Labs and Pacific.ai

John Snow Labs has created [langtest](https://langtest.org/){:target="_blank"}, a test generation and execution framework with &ldquo;60+ test types for comparing LLM & NLP models on accuracy, bias, fairness, robustness & more.&rdquo;

The affiliated company [Pacific.ai](https://pacific.ai/){:target="_blank"} offers a commercial [testing system](https://pacific.ai/testing/){:target="_blank"} with similar features.

## Merriam-Webster Dictionary

The [Merriam-Webster Dictionary](https://www.merriam-webster.com/dictionary/){:target="dict"}: is quoted in our [Glossary]({{site.glossaryurl}}) for several terms.

## Michael Feathers

[Michael Feathers](https://michaelfeathers.silvrback.com){:target="michael-feathers"} gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024, which is discussed in [Abstractions Encapsulate Complexities]({{site.baseurl}}/arch-design/component-design/#abstractions-encapsulate-complexities).

## MLCommons Glossary

The [MLCommons](https://mlcommons.org/){:target="mlcommons"} AI Safety v0.5 Benchmark Proof of Concept [Technical Glossary](https://drive.google.com/file/d/1X9Sy8eRiYgbeBBVMMqNrDEq4KzHZynpF/view?usp=sharing){:target="mlc-glossary"} is used to inform our [Glossary]({{site.glossaryurl}}).

## Nathan Lambert

[How to approach post-training for AI applications](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"}, a tutorial presented at [NeurIPS 2024](https://neurips.cc/Conferences/2024){:target="neurips"} by [Nathan Lambert](https://www.natolambert.com/){:target="nathan-lambert"}. It is discussed in [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning/). See also [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}.

## NIST Risk Management Framework

The U.S. National Institute of Science and Technology's ([NIST](https://www.nist.gov/){:target="nist"}) Artificial Intelligence [Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework){:target="nist-rmf"} (AI RMF 1.0) is used to inform our [Glossary]({{site.glossaryurl}}).

## OpenAI

An [OpenAI](https://openai.com){:target="openai"} [paper](https://openai.com/form/rft-research-program/){:target="openai-rf"} on _reinforcement fine tuning_ is discussed in [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning/).

## PlurAI

[Plurai.ai](https://plurai.ai){:target="_blank"} recently created an open-source project called [Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} that demonstrates how to exploit some recent research on automated generation of test data, knowledge graphs based on the constraints and requirements for an application, and automated test generation to verify alignment of the system to the requirements. These techniques are designed to provide more exhaustive test coverage of behaviors, including catching corner cases.

## Patronus

The Patronus guide, [LLM Testing: The Latest Techniques & Best Practices](https://www.patronus.ai/llm-testing){:target="patronus"}, discusses the unique testing challenges raised by generative AI and discusses various techniques for testing these systems.

## Wikipedia

Several [Wikipedia](https://en.wikipedia.org/wiki/){:target="wikipedia"} articles are used as references in our [Glossary]({{site.glossaryurl}}) and other places.
