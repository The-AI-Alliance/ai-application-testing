---
layout: default
title: Statistical Tests
nav_order: 250
parent: Testing Strategies and Techniques
has_children: false
---

# Statistical Tests

Are there cases where the behavior is nondeterministic, but reasonable bounds can be specified statistically? In other words, if the results fall within some measurable confidence window, they are considered acceptable, i.e., _passing_. 

### Use of Statistics at Netflix
 
Adrian Cockcroft [told one of us]({{site.baseurl}}/testing-problems/#is-this-really-a-new-problem) that Netflix took this approach for their recommendation systems, computing _plausibility_ scores that gave them sufficient confidence in the results.

More recently, a new open-source project called [Intellagent](https://github.com/plurai-ai/intellagent) from [Plurai.ai](https://plurai.ai) brings together recent research on automated generation of test data, knowledge graphs based on the constraints and requirements for an application, and automated test generation to verify _alignment_ of the system to the requirements. (We plan to update this site with more information about Intellagent soon.)

TODOs:

1. Examples, perhaps inspired by classifiers.
2. Use of standard deviations, ...
3. See [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"} a paper by [Evan Miller]({{site.baseurl}}/references/#evan-miller).
4. Deeper discussion of Intellagent.