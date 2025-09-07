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

Finally, could it be we are thinking about this all wrong? It is normal to attempt to _bend_ your current [Paradigm]({{site.glossaryurl}}/#paradigm) to meet a new reality, rather than rethink the situation from the fundamentals. With that in mind, should we _abandon_ the idea of testing, at least for the unavoidable, nondeterministic model [Behaviors]({{site.glossaryurl}}/#behavior), in favor of something entirely new?

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO

Our standard approach to software development involves writing software and _then_ testing that it works[^1]. Since models are [Tunable]({{site.glossaryurl}}/#tuning), what if instead our development cycle includes routine, incremental model tuning steps that run until satisfactory behavior is achieved? In other words, what if we go from _verifying_ desired behavior after the fact to _coercing_ the desired behavior as part of the &ldqou;building&rdqou; process? We will probably need some combination of _verification_ and _coercion_.

[^1]: The tests are written _before_ the code when doing [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development).

How would this work? What is needed that we don't already have? 

In a sense, this may not look all that different than the test-driven development cycle, where [_unit benchmarks_]({{site.baseurl}}/testing-strategies/unit-benchmarks) are written first for the desired behavior, but instead of writing code and running conventional tests, a tuning cycle is started that tunes the model until the benchmarks _pass_. As in normal TDD practice, all existing unit benchmarks would be executed regularly to catch behavior regressions.

## Ideas to Explore

Here are some ideas we are investigating.

### Reinforcement Finetuning

For some inspiration, consider slide 25 of [this NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} by [Nathan Lambert]({{site.baseurl}}/references/#nathan-lambert), where he discusses a recent evolution of _reinforcement learning_, called _reinforcement finetuning_:

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

Nathan also discusses this work in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}. It is based on [this OpenAI paper](https://openai.com/form/rft-research-program/){:target="openai-rf"}, which is entirely focused on conventional model tuning, but I think if you consider the bullets above, it also fits nicely with our goals of finding general ways to assure desired behavior. 

In particular, note that a _grader_ is used to verify outputs, a key component of any test framework! Hence, it is worth exploring what suite of graders would be useful for many AI-centric [Use Cases]({{site.glossaryurl}}/#use-case)? John Allard from OpenAI describes them in [this X post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2){:target="x"}. Graders may be useful for testing, as well as tuning.

Subsequent slides go into the tuning data format, how answers are analyzed for correctness, etc.

## The Impact on Architecture and Design

In [Architecture and Design]({{site.baseurl}}/arch-design), we discussed techniques with testing needs in mind. Making tuning an integral part of the software development process could impact the architecture and design, too, as we explore in this section.

TODO - how tuning becomes a part of the development lifecycle, how testing processes might change.

## Some Next Steps

* Explore _graders_.
* We need very fine-grained tuning techniques for use-case specific tuning. See
[Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks). Two technologies to investigate for organizing these tuning runs are the following:
	* [InstructLab](https://instructlab.ai){:target="instructlab"} (from RedHat). 
	* [Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} (from the Allen Institute of AI; mentioned by Nathan above)
* Projects like [OpenDXA with DANA](https://the-ai-alliance.github.io/#ai-powered-programming-language-for-agents){:target="dana"} are working to establish better control over model behaviors in part by automatically learning to be more effective.
* We still need regression "testing", so whatever we construct for fine-grained tuning should be reusable in automated, repeatable test runs.
* ...

## Appendix: How Science Changes Its Mind...

The idea of a complete reset is an established idea. [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="ssr"}, published in 1962, studied how scientists approach new evidence that appears to contradict an established theory. They don't immediately discard the established theory. Instead, they first attempt to accommodate the new evidence into the existing theory, making modifications as necessary.

Eventually, if the contradictions become too glaring and the modifications become too strained, some researchers will abandon the established theory and allow the evidence to lead them to a fundamentally new theory. Two examples from the history of Physics are the transition from Newtonian (&ldquo;Classical&rdquo;) Mechanics to Quantum Mechanics and the emergence of the Special and General Theories of Relativity, all of which emerged in the early decades of the twentieth century. In Astronomy, it took several _millennia_  for astronomers to discard the _geocentric_ view of the solar system, where the Earth was believed to be at the center and everything else revolves around it. Astronomers developed elaborate theories about orbital mechanics involving [_epicycles_](https://en.wikipedia.org/wiki/Deferent_and_epicycle){:target="wikipedia"}, nesting of circular orbits, that were needed to explain the observed _retrograde motion_ of planetary orbits. An important breakthrough for considering a _heliocentric_ solar system, where the Sun is at the center, was the way this model greatly simplified orbital mechanics, removing the need for epicycles.


## What's Next?

Review the [highlights](#highlights) summarized above, then see the [References]({{site.baseurl}}/references/) for more information.

---
