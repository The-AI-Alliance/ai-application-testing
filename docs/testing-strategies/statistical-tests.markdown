---
layout: default
title: Statistical Evaluation
nav_order: 340
parent: Testing Strategies and Techniques
has_children: false
---

# Statistical Evaluation

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

So far, we have explored various techniques for testing the [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} behaviors of the application where generative AI is used. We found scenarios where we could enforce mostly-deterministic behavior, such as handling FAQs in our example ChatBot. However, in general, we need the ability to assess the non-deterministic behaviors, such as deciding on appropriate thresholds for when an AI-related test can be considered to pass or fail, and when a synthetic datum is acceptable or not.

{: .todo}
> **TODO:** This chapter needs contributions from experts in statistics. See [this issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/27){:target="_blank"} and [Contributing]({{site.baseurl}}/contributing) if you would like to help.

In the [Unit Benchmark's Experiments to Try]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try) and in various parts of [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge) chapter, we raised questions to begin thinking about these decisions. Now we will put the concepts on a more formal foundation. Specifically, we will apply [Statistical Analysis]({{site.glossaryurl}}/#statistical-analysis){:target="_glossary"} to test results and use that information to inform our thinking.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Statistical analysis helps us make sense of observed behaviors of stochastic processes, like generated AI responses.
> 1. Deciding on acceptable thresholds for pass/fail may be use case dependent. They will require consideration of acceptable tolerance for &ldquo;suboptimal&rdquo; responses, the risks at stake for the application, and overall intuition about acceptable use-case performance.

## Statistical Analysis of Data for Stochastic Systems

{: .todo}
> **TODO:** Provide a _very concise_ overview of the basics the reader needs to understand. This can't be an exhaustive treatment. Emphasize the tools used for particular purposes. Show the formulas, but de-emphasizing understanding them in detail, because they can be coded as reusable libraries. An intuitive understanding is the goal here.

This paper might be useful: [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640){:target="error-bars"} by [Evan Miller]({{site.baseurl}}/references/#evan-miller).

## Other Examples of Using Statistics in AI Testing Situations

### The Use of Statistics at Netflix
 
In [Testing Problems]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem), we mentioned that Netflix faced the same testing challenges back in 2008 for their recommendation systems. Part of their solution leveraged statistical analysis. They computed _plausibility_ scores that gave them sufficient confidence in the results.

{: .todo}
> **TODO:** Fill in more details.

### Plurai's Intellagent

More recently, a new open-source project called [Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} from [Plurai.ai](https://plurai.ai){:target="_blank"} brings together recent research on automated generation of test data, knowledge graphs based on the constraints and requirements for an application, and automated test generation to verify _alignment_ of the system to the requirements. 

{: .todo}
> **TODO:** Expand the explanation of what Intellagent does and show use of it in our example.

## Evaluating Our Synthetic Data and Healthcare ChatBot Test Results

In our healthcare ChatBot, we realized we could design our prompts to detect FAQs, like prescription refill requests, and return a deterministic response. However, we have left open the question of how to handle edge cases, such as messages that are ambiguous and may or may not be actual refill requests. Let's explore this issue now.

First, can we establish our confidence that we have a real refill request? We raised this question informally in the [Experiments to Try]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try) in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try).

For simplicity, we will continue to ignore the possibility of a prompt containing additional content in addition to a refill request.

{: .todo}
> **TODO:** Complete...

## Experiments to Try

{: .todo}
> **TODO:** Expand this section once more content is provided above.

## What's Next?
Review the [highlights](#highlights) summarized above, then proceed to the [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing/).

---
