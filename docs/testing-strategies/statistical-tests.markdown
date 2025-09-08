---
layout: default
title: Statistical Tests
nav_order: 340
parent: Testing Strategies and Techniques
has_children: false
---

# Statistical Tests

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Are there cases where the [Behavior]({{site.glossaryurl}}/#behavior) is nondeterministic, but reasonable bounds can be specified statistically? In other words, if the results fall within some measurable confidence window, they are considered acceptable, i.e., _passing_. 

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO

### The Use of Statistics at Netflix
 
In [Testing Problems]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem), we mentioned that Netflix dealt faced the same testing challenges back in 2008 for their recommendation systems. Part of their solution leveraged statistical analysis. They computed _plausibility_ scores that gave them sufficient confidence in the results.

TODO: more...

More recently, a new open-source project called [Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} from [Plurai.ai](https://plurai.ai){:target="_blank"} brings together recent research on automated generation of test data, knowledge graphs based on the constraints and requirements for an application, and automated test generation to verify _alignment_ of the system to the requirements. (We plan to update this site with more information about Intellagent soon.)

TODOs:

1. Examples, perhaps inspired by classifiers.
2. Use of standard deviations, ...
3. See [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"} a paper by [Evan Miller]({{site.baseurl}}/references/#evan-miller).
4. Deeper discussion of Intellagent.


## What's Next?
Review the [highlights](#highlights) summarized above, then proceed to the [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing/).

---
