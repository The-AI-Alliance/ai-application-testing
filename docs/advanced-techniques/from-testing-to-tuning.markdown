---
layout: default
title: From Testing to Tuning
nav_order: 420
parent: Advanced Techniques
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

Finally, could it be we are thinking about this all wrong? It is normal to attempt to _bend_ our current [Paradigm]({{site.glossaryurl}}/#paradigm){:target="_glossary"} (see also the [Appendix](appendix-how-science-changes-its-mind)) to meet a new reality, rather than rethink the situation from first principles. We are still early in the generative AI &ldquo;revolution&rdquo;. We don't really know what radically-different approaches will emerge for any aspect of our use of AI, including how to perform sufficiently-reliable testing.

With that in mind, are there more AI-native alternatives to our conventional ideas about testing, ideas that work better for the [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} generative AI [Behaviors]({{site.glossaryurl}}/#behavior){:target="_glossary"} of the AI components? This chapter speculates on one possibility.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. It is still early in the generative AI &ldquo;revolution&rdquo;.
> 1. We tend to apply our traditional approaches to new problems. Often this works well.
> 1. However, we should expect completely new AI-driven approaches to problem solving to emerge, especially for new AI-driven challenges.
> 1. One possible new approach is to shift attention from the traditional cycle of evolving code and tests together, where we use the tests to ensure compliance, to a more &ldquo;active&rdquo; process of continuous [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} of models to meet evolving requirements.

Our standard approach to software development involves writing software and _then_ testing that it works[^1]. Since models are [Tunable]({{site.glossaryurl}}/#tuning){:target="_glossary"}, what if instead our development cycle includes routine, incremental model tuning steps that run until satisfactory behavior is achieved? In other words, what if we go from _verifying_ desired behavior after the fact to _coercing_ the desired behavior as part of the &ldquo;building&rdquo; process? Tuning is already a standard technique used to improve models in some way. Will we arrive at a set of practices that combine incremental tuning with testing as applications evolve? 

[^1]: The tests are written _before_ the code, in part to drive thinking about the design, when doing [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development){:target="_glossary"}.

The _verification_ role is still required for measuring when tuning is needed and how well it worked, so we will still need to write tests, i.e., [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark){:target="_glossary"} of some kind. 

Tuning is one of the important tools we have for building systems that perform as designed, better than model inference on its own. While techniques like [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"} improve inference importance by &ldquo;enhancing&rdquo; prompts with supplemental data, tuning improves a model itself. Tuning is used by model builders to improve model performance in various categories, such as better conformance to social norms (i.e., safety), better instruction following (i.e., answering questions), better reasoning and planning skills, etc. Domain-specific models are also being tuned from more generic models to provide more-effective behavior for the domain's use cases. 

Tuning techniques are still considered too advanced or difficult to use by many application development teams, but approachable open source and commercial tools are emerging, which will make tuning more pervasive over time. In fact, we expect this to be one of the big AI trends in 2026.

Besides easy-to-use tools, what is also required for our purposes is the integration of tuning into iterative and incremental development processes. Tuning itself will need to be done iteratively and incrementally for each new use case or feature implemented, an additional practice to those already used. 

Even among teams that already tune models, incremental tuning is not commonly practiced. Instead, these teams treat tuning as a one-time process. However, this in part reflects the fact that most teams doing tuning today are model builders who perform big, sophisticated tuning processes after the initial [Pre-Training]({{site.glossaryurl}}/#pre-training){:target="_glossary"} of models, in order to improve general abilities in safety, instruction following, etc. 

In contrast, teams that adopt tuning as part of the application development process will need incremental tuning capabilities. This will drive the evolution of the necessary incremental techniques. Hence, this kind of fine-grained tuning of models is still a research and development topic, in part. A requirement with be automatic evaluation after each iteration to detect regressions in behavior, as well as verification of improved performance in the focus area of the tuning. This continuous verification is exactly how tests are used for traditional software in organizations with mature testing practices; it is integral to [DevOps](https://en.wikipedia.org/wiki/DevOps){:target="_wikipedia"}, specifically. 

Our goal is for AI benchmarking and testing practices to evolve similarly so that rapid, targeted, and automatic execution of these tools can similarly be performed when doing incremental tuning.

## Tuning Ideas for Further Exploration

Here are some ideas we are investigating. See also the [&ldquo;rough notes&rdquo;]({{site.baseurl}}/advanced-techniques/notes-on-tuning/) on tuning techniques, which will eventually be refined and incorporated into other chapters, especially this one.

### Reinforcement Fine Tuning

For some inspiration, consider slide 25 of [this NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} by [Nathan Lambert]({{site.referencesurl}}/#nathan-lambert), where he discusses a recent evolution of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning){:target="_glossary"}, called _reinforcement fine tuning_[^2]:

{: .attention }
> **What Is Reinforcement Fine Tuning?**
>
> Reinforcement fine tuning uses repeated passes over the data with reinforcement learning (RL) to encourage the model to figure out more robust behaviors in domains.
> 
> It requires:
> 
> 1. Training data with explicitly correct answers.
> 1. A grader (or extraction program) for verifying outputs.
> 1. A model that can sometimes generate a correct solution. _Otherwise, no signal for RL to learn from._
>
> Key innovation: 
> 
> **Improving targeted skills reliably without degradation on other tasks.**

[^2]: Nathan spells it _finetuning_, but we spell it as two words.

Nathan also discusses this work in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-fine-tuning){:target="openai-rf"}. It is based on [this OpenAI paper](https://openai.com/form/rft-research-program/){:target="openai-rf"}, which is entirely focused on conventional model tuning, but if you consider the bullets quoted here, reinforcement fine tuning also fits nicely with our goals of finding general ways to assure desired behavior. 

For example, a _grader_ is used to verify outputs, analogous to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge). Hence, it is worth exploring what suite of graders would be useful for many AI-centric [Use Cases]({{site.glossaryurl}}/#use-case){:target="_glossary"}. John Allard from OpenAI describes them in [this X post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2){:target="x"}. Graders may be useful for testing, as well as tuning.

Subsequent slides go into the tuning data format, how answers are analyzed for correctness, etc.

{: .todo}
> **TODO:** 
> 
> More investigation and summarization here, especially the concept of _graders_. Provide an example??

## The Impact on Architecture and Design

In [Architecture and Design]({{site.baseurl}}/arch-design), we discussed techniques with testing needs in mind. Making tuning an integral part of the software development process could impact the architecture and design, too, as we explore in this section.

{: .todo}
> **TODO:** 
> 
> How tuning becomes a part of the development lifecycle, how testing processes might change.


<a id="other-tools"/>

## Other Tools for Model Tuning

Model tuning requires domain-specific data sets. In [Other Tools]({{site.baseurl}}/testing-strategies/unit-benchmarks/#other-tools) in the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter, we discussed tools like Meta's [`synthetic-data-kit`](https://github.com/meta-llama/synthetic-data-kit/){:target="_blank"} for data synthesis. We mentioned its scalable support for larger-scale data synthesis and processing, such as translating between formats, especially for model [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} with Llama models. Similarly [Other Tools]({{site.baseurl}}/testing-strategies/llm-as-a-judge/#other-tools) in the [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) chapter explored tools for validation of synthetic data.

Here are some other tools for model tuning. 

{: .todo}
> **TODO:** 
> 
> Revamp this list with newer tools. Expand the discussion and show one or more examples of use.

### Open Instruct

[Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} from the Allen Institute of AI is a tool suite for instruction tuning of models. It is mentioned by Nathan Lambert in the [Reinforcement Fine Tuning](#reinforcement-fine-tuning) content discussed above. See also [InstructLab](#instructlab).

### Unsloth

Unsloth is an OSS tool suite for model training and tuning, with useful guides on the following topics:

* [Fine-tuning LLMs](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide){:target="u-ft"}
* [Reinforcement Learning](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide){:target="u-rl"}

### InstructLab

[InstructLab](https://instructlab.ai){:target="instructlab"} is a project started by [IBM Research](https://research.ibm.com){:target="ibm"} and developed by [RedHat](https://redhat.com){:target="redhat"}. InstructLab has similar goals compared to [Open Instruct](#open-instruct). It provides conventions for organizing specific, manually-created examples into a domain hierarchy, along with tools to perform model tuning, including synthetic data generation. Hence, InstructLab provides an alternative way to generate synthetic data for [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks).

## Examples of Domain-specific Tuned Models

### Law

* [Enhancing Legal Research with Domain-Adapted Semantic Search](https://free.law/2025/03/11/semantic-search){:target="_blank"}. 
  * Enhanced legal semantic search: an embedding generation tool and the underlying machine learning model that we will be used in their new semantic search engine.
  * Also discussed in this [LinkedIn post](https://www.linkedin.com/posts/free-law-project_free-law-project-just-released-an-open-source-activity-7394404189549813760-HCSe/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAADMuwBhUpKJry9e_Cx6_WejpcA-DcEN6o){:target="_blank"}

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will provide some examples to try along with suggestions for further experimentation.

## What's Next?

Review the [highlights](#highlights) summarized above and optionally the [Appendix](#appendix-how-science-changes-its-mind) below, then see the [References]({{site.referencesurl}}/) for more information. Refer to the separate [Glossary website]({{site.glossaryurl}}/){:target="_glossary"} for definitions.

## Appendix: How Science Changes Its Mind...

The idea of a complete reset is an established idea. [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="ssr"}, published in 1962, studied how scientists approach new evidence that appears to contradict an established theory. They don't immediately discard the established theory. Instead, they first attempt to accommodate the new evidence into the existing theory, making modifications as necessary.

Eventually, if the contradictions become too glaring and the modifications become too strained, some researchers will abandon the established theory and allow the evidence to lead them to a fundamentally new theory. Two examples from the history of Physics are the transition from Newtonian (&ldquo;Classical&rdquo;) Mechanics to Quantum Mechanics and the emergence of the Special and General Theories of Relativity, all of which emerged in the early decades of the twentieth century. In Astronomy, it took several _millennia_  for astronomers to discard the _geocentric_ view of the solar system, where the Earth was believed to be at the center and everything else revolves around it. Astronomers developed elaborate theories about orbital mechanics involving [_epicycles_](https://en.wikipedia.org/wiki/Deferent_and_epicycle){:target="_wikipedia"}, nesting of circular orbits, that were needed to explain the observed _retrograde motion_ of planetary orbits. An important breakthrough for considering a _heliocentric_ solar system, where the Sun is at the center, was the way this model greatly simplified orbital mechanics, removing the need for epicycles.

---
