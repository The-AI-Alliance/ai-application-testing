---
layout: default
title: From Testing to Training
nav_order: 260
parent: Testing Strategies and Techniques
has_children: false
---

# From Testing to Training

Finally, maybe we are thinking about this all wrong. It's normal to attempt to bend your current [_paradigm_](https://www.merriam-webster.com/dictionary/paradigm){:target="dict"} to meet a new reality, rather than rethink it from the fundamentals. Should we _abandon_ the idea of developer testing in favor of something entirely new?

This idea of resetting completely is not a new idea. For example, [_The Structure of Scientific Revolutions_](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions){:target="dict"}, published in 1962, studied how scientists approach new evidence that appears to contradict established theories. They don't immediately discard the established theories, but first attempt to accommodate the new evidence into the existing theories, with modifications as required. However, eventually, the willingness of some researchers to consider abandoning the orthodoxy and the weight of the evidence lead to fundamentally new theories about reality. Examples from Physics include the transition from Newtonian mechanics to quantum mechanics and the special and general theories of relativity, all of which emerged in the early decades of the twentieth century.

Back to generative AI, various model-tuning techniques are established and necessary practices for ensuring that models perform as desired. So, what if we abandon the usual approach of writing software and testing that it works, and instead strive to continue tuning the model until satisfactory behavior is achieved? In other words, what if we go from verifying desired behavior to coercing desired behavior?

How would this work and what's needed that we don't already have?

TODO - more...

* We need very fine-grained tuning techniques for use-case specific tuning. See
[Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks). Another technology to investigate for organizing these tuning runs is [InstructLab](https://instructlab.ai){:target="instructlab"}.
* We still need regression "testing", so whatever we construct for fine-grained tuning should be reusable in some way for repeated test runs.
* ...


TODOs:

1. Examples, perhaps inspired by classifiers.
2. Use of standard deviations, ...
3. See [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"}.