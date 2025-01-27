---
layout: default
title: From Testing to Training
nav_order: 260
parent: Testing Strategies and Techniques
has_children: false
---

# From Testing to Training

Finally, could it be we are thinking about this all wrong? It is normal to attempt to _bend_ your current [Paradigm]({{site.baseurl}}/glossary/#paradigm) to meet a new reality, rather than rethink the situation from the fundamentals. Should we _abandon_ the idea of deterministic testing, at least for nondeterministic model behaviors, in favor of something entirely new?

This idea of a complete reset is an established idea. [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="ssr"}, published in 1962, studied how scientists approach new evidence that appears to contradict an established theory. They don't immediately discard the established theory. Instead, they first attempt to accommodate the new evidence into the existing theory, making small modifications, as necessary.

However, eventually, the willingness of some researchers to consider abandoning the orthodoxy and the weight of the evidence lead to the emergence of a fundamentally new theory to explain the data. Examples from Physics include the transition from Newtonian Mechanics to Quantum Mechanics and the Special and General Theories of Relativity, all of which emerged in the early decades of the twentieth century. In Astronomy, it took several _millennia_  for astronomers to discard the _geocentric_ view of the solar system, where the Earth was believed to be at the center and everything else revolved around it. Astronomers developed elaborate theories about orbital mechanics involving [_epicycles_](https://en.wikipedia.org/wiki/Deferent_and_epicycle){:target="wikipedia"}, nesting of circular orbits, which were needed to explain the observed _retrograde motion_ of planetary orbits. An important breakthrough for considering a _heliocentric_ solar system, where the Sun is at the center, was the way this model greatly simplified orbital mechanics, removing the need for epicycles.

Back to generative AI, what if we relax the usual approach of writing software and _then_ testing that it works? Since models are tunable, what if instead our development cycle includes routine, incremental model tuning steps that run until satisfactory behavior is achieved? In other words, what if we go from _verifying_ desired behavior to _coercing_ desired behavior? How would this work and what's needed that we don't already have? Should we actually strive for some combination of _verification_ and _coercion_?

In practical terms, this may not look all that different than a typical [TDD]({{site.baseurl}}/glossary/#test-driven-development) cycle, where [unit benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks) are written first for the desired behavior, but instead of writing code and running conventional tests, a tuning cycle is started that tunes the model until the benchmarks _pass_. As in normal TDD practice, the existing unit benchmarks would be executed to catch regressions in behavior.

## For More Information

For some inspiration, consider slide 25 of [this NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} by [Nathan Lambert]({{site.baseurl}}/references/#nathan-lambert), where he discusses a recent evolution of _reinforcement learning_, called _reinforcement finetuning_:

> **What is reinforcement finetuning?**
>
> Uses repeated passes over the data with RL to encourage model to figure out more robust behaviors in domains.
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

Nathan also discusses this work in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}.

Nathan is talking about [this OpenAI paper](https://openai.com/form/rft-research-program/){:target="openai-rf"}, which is entirely focused on model tuning, but I think if you consider the bullets above, it also fits nicely with our goals of finding general ways to assure desired behavior. 

In particular, note that a _grader_ is used to verify outputs, a key component of any test framework! Hence, it is worth exploring what suite of graders would be useful for many AI-centric use cases? John Allard from OpenAI describes them in [X this post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2){:target="x"}. Graders may be useful for testing, as well as tuning.

Subsequent slides go into the tuning data format, how answers are analyzed for correctness, etc.

## Next steps

(TODO: - this needs refinement)

* Explore _graders_.
* We need very fine-grained tuning techniques for use-case specific tuning. See
[Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks). Another technology to investigate for organizing these tuning runs is [InstructLab](https://instructlab.ai){:target="instructlab"}. [Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} From Allen Institute of AI has similar potential (and it is mentioned by Nathan above.)
* We still need regression "testing", so whatever we construct for fine-grained tuning should be reusable in some way for repeated test runs.
* ...
