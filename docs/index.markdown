---
layout: default
title: Home
nav_order: 10
has_children: false
---

# Achieving Confidence in Enterprise AI Applications

(Previous Title: _AI Application Testing for Developers_)

{: .highlight }
> **I am an Enterprise Developer: How Do I Test My AI Applications??**
>
> I know how to test my traditional software, which is **deterministic** (more or less...), but I don't know how to test my AI applications, which are uniquely **nondeterministic**.

Welcome to the **The AI Alliance** project to advance the state of the art for **Enterprise Testing of Generative AI (&ldquo;GenAI&rdquo;) Applications**. We are building the knowledge and tools you need to achieve the same testing confidence for your AI applications that you have for your traditional applications.

{: .tip}
> **Tips:**
>
> 1. Use the search box at the top of this page to find specific content.
> 2. [Capitalized Terms]({{site.glossaryurl}}/) link to glossary definitions.

## The Challenge We Face

We enterprise software developers know how to write [Repeatable]({{site.glossaryurl}}/#repeatable) and [Automatable]({{site.glossaryurl}}/#automatable) tests. In particular, we rely on [Deterministism]({{site.glossaryurl}}/#determinism) when we write tests to verify expected behavior and to ensure that no [Regressions]({{site.glossaryurl}}/#regression) occur as our code base evolves. Why is determinism a key ingredient? We know that if we pass the same arguments repeatedly to a [Unit]({{site.glossaryurl}}/#unit) (e.g., a [Function]({{site.glossaryurl}}/#function)), we will get the same answer back (with special exceptions). This property enables our core testing techniques, which give us essential _**confidence**_ that our applications meet our requirements, that they implement the use cases our customers expect. We are accustomed to _pass/fail_ answers!

Problems arise when we introduce [Generative AI Models]({{site.glossaryurl}}/#genenerative-ai-model), which are inherently [Probabilistic]({{site.glossaryurl}}/#probability-and-statistics) and hence _nondeterministic_. Can we write the same kinds of tests now? If not, what alternative approaches should we use instead?

In contrast, our AI-expert colleagues (model builders and data scientists) use different tools to build their _confidence_ in how their models perform. Specifically, [Probability and Statistics]({{site.glossaryurl}}/#probability-and-statistics), tools that predate Generative AI, are used to understand the _probabilities_ that possible outcomes will be seen, and to analyze and quantify these outcomes _statistically_. This information helps them decide how much to trust their models will be behave as desired. Rarely are _pass/fail_ answers available here.

![Developer to AI Expert Spectrum]({{site.baseurl}}/assets/images/developer-to-AI-expert-spectrum.png "Developer to AI Expert Spectrum")

**Figure 1:** The spectrum between deterministic and probabilitistic behavior.

_**We have to bridge this divide.**_ As developers, we need to understand and adapt these data science tools for our needs. This will mean learning some probability and statistics concepts, but we shouldn't need to become experts. Similarly, our AI-expert colleagues need to better understand our needs, so they can help us take their work and use it to deliver reliable, trustworthy AI-enabled products.

## Project Goals

The goals of this project are two fold:

1. Develop and document strategies and techniques for testing Generative AI applications that eliminate nondeterminism, where feasible, and where not feasible, still allow us to write effective, repeatable and automatable tests. This work also impacts architecture and design decisions.
2. Publish detailed, reusable examples and guidance for developers and AI experts on these strategies and techniques.

## Overview of This Site

We start with a deeper dive into [The Problems of Testing Generative AI Applications]({{site.baseurl}}/testing-problems).

Then we discuss [Architecture and Design]({{site.baseurl}}/architecture-design) concepts that are informed by the need for effective testing, which leads to AI applications that are reliable and serve their purposes:
* [Coupling and Cohesion]({{site.baseurl}}/architecture-design/coupling-cohesion): Remembering to use these classic design principles.
* [Tips and Tricks for AI Application Design]({{site.baseurl}}/testing-strategies/ai-specific-design): AI-specific ideas for building more effective applications.

Good design will make the main topic of this site, [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies/), easier to use and more effective:
* [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification): Cases where non-LLM tools can test our LLM results.
* [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing): Testing at the scale of large, complex systems is also less deterministic than in the context of [Unit Tests]({{site.glossaryurl}}/#unit-test), etc. What lessons can we learn here?
* [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks): Adapting [Benchmark]({{site.glossaryurl}}/#benchmark) techniques for [Unit Testing]({{site.glossaryurl}}/#unit-test) and similarly for [Integration Testing]({{site.glossaryurl}}/#integration-testing) and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-testing).
* [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge): Using a &ldquo;smarter&rdquo; LLM to judge application behaviors.
* [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests): Embracing statistical analysis. What's the minimum you need to know? How do you use these techniques?
* [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning): Should we rethink testing as a strategy? If so, how would this change affect AI application architecture and design?

Finally, there is a [Glossary of Terms]({{site.glossaryurl}}) and [References]({{site.baseurl}}/references) for additional information.


## Help Wanted!

This is very much a work in progress. This content will be updated frequently to reflect our current thinking, emerging recommendations, and reusable assets. Your [contributions]({{site.baseurl}}/contributing) are needed and most welcome!

See also [About Us]({{site.baseurl}}/about) for more details about this project and the AI Alliance.

## Additional Links

* This project's [GitHub Repo](https://github.com/The-AI-Alliance/ai-application-testing){:target="repo"}
* Companion projects: 
	* <a href="https://the-ai-alliance.github.io/trust-safety-evals/" target="eie">Evaluation Is for Everyone</a>
	* <a href="https://the-ai-alliance.github.io/eval-ref-stack/" target="ers">Evaluation Reference Stack</a>
	* <a href="https://the-ai-alliance.github.io/trust-safety-user-guide/" target="ers">The AI Trust and Safety User Guide</a>
* The AI Alliance: 
	* [Website](https://thealliance.ai){:target="ai-alliance"}
	* [The Trust and Safety Work Group](https://thealliance.ai/focus-areas/trust-and-safety){:target="ai-alliance-tns"} 

| **Authors**     | The AI Alliance [Trust and Safety](https://thealliance.ai/focus-areas/trust-and-safety){:target="ai-alliance-tns"} and [Applications and Tools](https://thealliance.ai/focus-areas/applications-and-tools){:target="ai-alliance-apps"} work groups. (See the [Contributors]({{site.baseurl}}/contributing/#contributors)) |
| **Last Update** | {{site.last_version}}, {{site.last_modified_timestamp}} |
