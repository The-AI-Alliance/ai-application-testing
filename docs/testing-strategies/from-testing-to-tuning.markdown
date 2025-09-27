---
layout: default
title: From Testing to Tuning
nav_order: 360
parent: Testing Strategies and Techniques
has_children: false
---

# From Testing to Tuning

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Finally, could it be we are thinking about this all wrong? It is normal to attempt to _bend_ our current [Paradigm]({{site.glossaryurl}}/#paradigm) (see also the [Appendix](appendix-how-science-changes-its-mind)) to meet a new reality, rather than rethink the situation from first principles. We are still early in the generative AI &ldquo;revolution&rdquo;. We don't really know what radically-different approaches will emerge for any aspect of our use of AI, including how to perform sufficiently-reliable testing.

With that in mind, are there more AI-native alternatives to our conventional ideas about testing, ideas that work better for the [Stochastic]({{site.glossaryurl}}/#stochastic) generative AI [Behaviors]({{site.glossaryurl}}/#behavior) of the AI components? This chapter speculates on one possibility.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. It is still early in the generative AI &ldquo;revolution&rdquo;.
> 1. We tend to apply our traditional approaches to new problems. Often this works well.
> 1. However, we should expect completely new AI-driven approaches to problem solving to emerge, especially for new AI-driven challenges.
> 1. One possible new approach is to shift attention from the traditional cycle of evolving code and tests together, where we use the tests to ensure compliance, to a more &ldquo;active&rdquo; process of continuous [Tuning]({{site.glossaryurl}}/#tuning) of models to meet evolving requirements.

Our standard approach to software development involves writing software and _then_ testing that it works[^1]. Since models are [Tunable]({{site.glossaryurl}}/#tuning), what if instead our development cycle includes routine, incremental model tuning steps that run until satisfactory behavior is achieved? In other words, what if we go from _verifying_ desired behavior after the fact to _coercing_ the desired behavior as part of the &ldquo;building&rdquo; process? 

[^1]: The tests are written _before_ the code, in part to drive thinking about the design, when doing [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development).

The _verification_ role is still required for measuring when tuning is needed and how well it worked, so we will still need to write tests, i.e., [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark) of some kind. 

Of course, tuning is already used by model builders to improve their models' performance in various categories, such as safety, question and answering, etc. Domain-specific models are also tuned from popular &ldquo;foundation&rdquo; models to provide more effective behavior in the use cases for the domain. Tuning is still considered a specialized skill and not widely used, but we anticipate that tuning technology will become easier to use and more efficient, with the result that more organizations will tune their own models for their specific domains and use cases.

What's still missing is an _active_ integration of tuning into iterative and incremental development processes, which will be necessary to do incremental tuning for each new use case or feature implemented. 

This kind of fine-grained tuning of models is still a research and development topic, in part because each incremental improvement needs to be automatically evaluated to detect regressions in behavior, as well as improved performance in the area where tuning is focused. This continuous verification is exactly how tests are used for traditional software in organizations with mature testing practices; it is integral to [DevOps](https://en.wikipedia.org/wiki/DevOps){:target="_wikipedia"}, specifically. Our hope is that AI benchmarking and testing practices will evolve similarly so that rapid, targeted, and automatic execution of these tools can similarly be performed when doing incremental tuning.

## Tuning Ideas for Further Exploration

Here are some ideas we are investigating.

### Reinforcement Finetuning

For some inspiration, consider slide 25 of [this NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} by [Nathan Lambert]({{site.baseurl}}/references/#nathan-lambert), where he discusses a recent evolution of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning), called _reinforcement finetuning_:

{: .highlight }
> **What is reinforcement finetuning?**
>
> Reinforcement finetuning uses repeated passes over the data with reinforcement learning (RL) to encourage the model to figure out more robust behaviors in domains.
> 
> Requires:
> 
> 1. Training data with explicitly correct answers.
> 1. A grader (or extraction program) for verifying outputs.
> 1. A model that can sometimes generate a correct solution. _Otherwise, no signal for RL to learn from._
>
> Key innovation: 
> 
> **Improving targeted skills reliably without degradation on other tasks.**

Nathan also discusses this work in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}. It is based on [this OpenAI paper](https://openai.com/form/rft-research-program/){:target="openai-rf"}, which is entirely focused on conventional model tuning, but if you consider the bullets quoted here, reinforcement finetuning also fits nicely with our goals of finding general ways to assure desired behavior. 

For example, a _grader_ is used to verify outputs, analogous to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge). Hence, it is worth exploring what suite of graders would be useful for many AI-centric [Use Cases]({{site.glossaryurl}}/#use-case)? John Allard from OpenAI describes them in [this X post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2){:target="x"}. Graders may be useful for testing, as well as tuning.

Subsequent slides go into the tuning data format, how answers are analyzed for correctness, etc.

{: .todo}
> **TODO:** More investigation and summarization here, especially the concept of _graders_. Provide an example??

## The Impact on Architecture and Design

In [Architecture and Design]({{site.baseurl}}/arch-design), we discussed techniques with testing needs in mind. Making tuning an integral part of the software development process could impact the architecture and design, too, as we explore in this section.

{: .todo}
> **TODO:** How tuning becomes a part of the development lifecycle, how testing processes might change.


<a id="other-tools"/>

## Other Tools for Model Tuning

Model tuning requires domain-specific datasets. In [Other Tools]({{site.baseurl}}/testing-strategies/unit-benchmarks/#other-tools) in the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter, we discussed tools like Meta's [`synthetic-data-kit`](https://github.com/meta-llama/synthetic-data-kit/){:target="_blank"} for data synthesis. We mentioned its scalable support for larger-scale data synthesis and processing, such as translating between formats, especially for model [Tuning]({{site.glossaryurl}}/#tuning) with Llama models. Similarly [Other Tools]({{site.baseurl}}/testing-strategies/llm-as-a-judge/#other-tools) in the [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) chapter explored tools for validation of synthetic data.

Here are some other tools for model tuning. 

{: .todo}
> **TODO:** Expand discussion, show example of use.

### InstructLab

[InstructLab](https://instructlab.ai){:target="instructlab"} is project started by [IBM Research](https://research.ibm.com){:target="ibm"} and developed by [RedHat](https://redhat.com){:target="redhat"}. InstructLab provides conventions for organizing specific, manually-created examples into a domain hierarchy, along with tools to perform model tuning, including synthetic data generation. Hence, InstructLab is an alternative way to generate synthetic data for [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks).

### Open Instruct

[Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} from the Allen Institute of AI tries to meet similar goals as InstructLab. It is mentioned by Nathan Lambert in the [Reinforcement Finetuning](#reinforcement-finetuning) content discussed above.

## Experiments to Try

{: .todo}
> **TODO:** We will provide some examples to try along with suggestions for further experimentation.

## What's Next?

Review the [highlights](#highlights) summarized above and optionally the [Appendix](#appendix-how-science-changes-its-mind) below, then review the [Glossary terms]({{site.glossaryurl}}/) see the [References]({{site.baseurl}}/references/) for more information.

## Appendix: How Science Changes Its Mind...

The idea of a complete reset is an established idea. [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="ssr"}, published in 1962, studied how scientists approach new evidence that appears to contradict an established theory. They don't immediately discard the established theory. Instead, they first attempt to accommodate the new evidence into the existing theory, making modifications as necessary.

Eventually, if the contradictions become too glaring and the modifications become too strained, some researchers will abandon the established theory and allow the evidence to lead them to a fundamentally new theory. Two examples from the history of Physics are the transition from Newtonian (&ldquo;Classical&rdquo;) Mechanics to Quantum Mechanics and the emergence of the Special and General Theories of Relativity, all of which emerged in the early decades of the twentieth century. In Astronomy, it took several _millennia_  for astronomers to discard the _geocentric_ view of the solar system, where the Earth was believed to be at the center and everything else revolves around it. Astronomers developed elaborate theories about orbital mechanics involving [_epicycles_](https://en.wikipedia.org/wiki/Deferent_and_epicycle){:target="_wikipedia"}, nesting of circular orbits, that were needed to explain the observed _retrograde motion_ of planetary orbits. An important breakthrough for considering a _heliocentric_ solar system, where the Sun is at the center, was the way this model greatly simplified orbital mechanics, removing the need for epicycles.

---
