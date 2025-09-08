---
layout: default
title: External Tool Verification
nav_order: 330
parent: Testing Strategies and Techniques
has_children: false
---

# External Tool Verification

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

In [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/), we explored using LLMs to validate the quality of synthetic benchmark data and other purposes, like generative responses. For some applications, we can leverage non-AI tools to evaluate data and generative responses. 

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Many non-generative tools are much better than generative AI tools at doing particular kinds of work.
> 2. Not only can these tools be used as part of an [Agent]({{site.glossaryurl}}/#agent)-based architecture, then can also be used to support test data validation.

When generative AI kicked popularity exploded after the unveiling of ChatGPT, it become quickly apparently that LLMs are better at some tasks than others, and other tools designed for many tasks are superior choices. This led to application design patterns like [Retrieval-Augmented Generation]({{site.glossaryurl}}/#retrieval-augmented-generation) (RAG) and [Agents]({{site.glossaryurl}}/#agent). 

In RAG, knowledge relevant to a prompt is retrieved and sent to an LLM as part of the context, so the model generates more accurate responses. An example is sourcing information about news events that occurred after a model was trained to support related queries.

Agent systems extend this data-retrieval model to more general tool invocations, such as web searches, with LLMs performing the role of determining from the prompt what kinds of information to gather from tools, which tools to invoke to get the information, invoking those tools, and formulating a response based on the tool replies.

Here, we are interested in using such tools in a testing context, either to validate synthetic data in a particular domain or to evaluate model or system outputs during tests.


## Example Tools

Let's explore some example tools, then consider their roles in the testing process.

### A Variation of LLM as a Judge?

First, no matter what tools you might use, there is a practical consideration.

Using other tools for our purposes, especially for automation, may require an [Agent]({{site.glossaryurl}}/#agent)-based implementation where an LLM invokes the tools, interprets the results, and compares them with the synthetic data or other model responses being evaluated. Hence, in practical terms, external tool verification could be considered a variation of [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/). Instead of relying on the LLM's ability to judge quality by itself, we rely on its ability to orchestrate and interpret the use of other tools to determine quality.

### Code Generation

Generated code can be checked for quality and validity and, in some cases, modified into a more desirable form. For example:

* Use a parser or compiler to verify the syntax is valid. Optionally correct the errors.
* Execute the code (in a Use a parser or compiler to verify the syntax is valid. Optionally correct the errors.
* Scan for security vulnerabilities.
* Scan for conformance to project code formatting conventions. This is a case where transforming the code might occur.
* Check for excessive [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="cyclomatic-complexity"}
* Check that it uses only allowed versions of allowed third-party libraries, e.g., those approved by the organization and versions that have no known vulnerabilities.
* If tests already exist for the generated code (see [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development)), verify the generated code allows the tests to pass.

## Planning

Planning is a common technique used in industrial applications, like assembly lines, determining near-optimal deliver routes, etc.

Applications that use models to generate plans can be checked against digital simulations of these scenarios. Why not just use the digital simulation in the first place? In some cases the model might produce candidate results faster, while the simulation might provide fast verification. In other cases, limitations of the simulation might be compensated for by the model's abilities.

## Reasoning, Logic, and Other Mathematics

Various deterministic tools exist to verify logical arguments are sound, mathematical statements and proofs are valid, etc.

## Science

Models are sometimes used to generate new ideas for certain research problems, which can then be validated through traditional means.

For example, protein structure models can generate new, candidate molecules for various purposes. The results can be compared to experimental data and physical simulation models. Candidate molecules can be synthesized to verify the have the desired properties.

## Web Search

Search the web for details about a topic. This requires care to validate the veracity of the results or at least the trustworthiness of the source. 



## TODOs:

1. Add more examples where tools can be used.
1. Expand the details for some of them.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests/).

---
