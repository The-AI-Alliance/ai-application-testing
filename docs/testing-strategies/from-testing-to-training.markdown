---
layout: default
title: From Testing to Training
nav_order: 260
parent: Testing Strategies and Techniques
has_children: false
---

# From Testing to Training

Finally, maybe we are thinking about this all wrong. It's normal to attempt to bend your current [_paradigm_](https://www.merriam-webster.com/dictionary/paradigm){:target="dict"} to meet a new reality, rather than rethink the situation from the fundamentals. Should we _abandon_ the idea of developer testing in favor of something entirely new?

This idea of resetting completely is not a new idea. For example, [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="dict"}, published in 1962, studied how scientists approach new evidence that appears to contradict established theories. They don't immediately discard the established theories, but first attempt to accommodate the new evidence into the existing theories, with modifications as required. However, eventually, the willingness of some researchers to consider abandoning the orthodoxy and the weight of the evidence lead to fundamentally new theories about reality. Examples from Physics include the transition from Newtonian Mechanics to Quantum Mechanics and the Special and General Theories of Relativity, all of which emerged in the early decades of the twentieth century. In Astronomy, it took centuries for astronomers to discard the _geocentric_ view of the solar system, where the Earth is at the center and everything else revolves around it. Astronomers developed elaborate theories about orbital mechanics involving _epicycles_, essentially smaller and smaller nested circles, which they needed to explain the observed _retrograde motion_ of orbits. An important clue for considering a _heliocentric_ solar system, where the Sun is at the center, was the greatly simplified orbital mechanics that resulted from this change.

Back to generative AI, various model-tuning techniques are established and necessary practices for ensuring that models perform as desired. So, what if we abandon the usual approach of writing software and testing that it works, and instead strive to continue tuning the model until satisfactory behavior is achieved? In other words, what if we go from _verifying_ desired behavior to _coercing_ desired behavior?

How would this work and what's needed that we don't already have? Should we actually strive for some combination of _verification_ and _coercion_?

For some inspiration, consider slide 25 of [this NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} by Nathan Lambert, where he discusses a recent evolution of _reinforcement learning_, called _reinforcement finetuning_:

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

Nathan also discusses this work in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning).

Nathan is talking about [this OpenAI paper](https://openai.com/form/rft-research-program/){:target="openai-rf"}, which is entirely focused on model tuning, but I think if you consider the bullets above, it also fits nicely with our goals of finding general ways to assure desired behavior. 

In particular, note that a _grader_ is used to verify outputs, a key component of any test framework! Hence, it is worth exploring what suite of graders would be useful for many AI-centric use cases? John Allard from OpenAI describes them in [X this post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2). Graders may be useful for testing, as well as tuning.

Subsequent slides go into the tuning data format, how answers are analyzed for correctness, etc.

## Next steps

(TODO: - this needs refinement)

* Explore _graders_.
* We need very fine-grained tuning techniques for use-case specific tuning. See
[Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks). Another technology to investigate for organizing these tuning runs is [InstructLab](https://instructlab.ai){:target="instructlab"}. [Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} From Allen Institute of AI has similar potential (and it is mentioned by Nathan above.)
* We still need regression "testing", so whatever we construct for fine-grained tuning should be reusable in some way for repeated test runs.
* ...
