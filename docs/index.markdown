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

We enterprise software developers know how to write [Repeatable]({{site.glossaryurl}}/#repeatable) and [Automatable]({{site.glossaryurl}}/#automatable) tests. In particular, we rely on [Deterministism]({{site.glossaryurl}}/#determinism) when we write tests to verify expected [Behavior]({{site.glossaryurl}}/#behavior) and to ensure that no [Regressions]({{site.glossaryurl}}/#regression) occur as our code base evolves. Why is determinism a key ingredient? We know that if we pass the same arguments repeatedly to _most_ [Functions]({{site.glossaryurl}}/#function) (with some exceptions), we will get the same answer back repeatedly. This property enables our core testing techniques, which give us essential _**confidence**_ that our applications meet our requirements, that they implement the use cases our customers expect. We are accustomed to _pass/fail_ answers!

Problems arise when we introduce [Generative AI Models]({{site.glossaryurl}}/#genenerative-ai-model), where generated output is inherently [Stochastic]({{site.glossaryurl}}/#stochastic) and hence _nondeterministic_. We can't write the same kinds of tests now, so what alternative approaches should we use instead?

In contrast, our AI-expert colleagues (researchers and data scientists) use the tools of [Probability and Statistics]({{site.glossaryurl}}/#probability-and-statistics) to analyze stochastic model responses and assess how well the models perform against particular objectives. For example, a model might score 85% on a [Benchmark]({{site.glossaryurl}}/#benchmark) for high school-level mathematical knowledge. Is that good enough? It depends on the application in mind! Rarely are _pass/fail_ answers available.

![Developer to AI Expert Spectrum]({{site.baseurl}}/assets/images/developer-to-AI-expert-spectrum.png "Developer to AI Expert Spectrum")

**Figure 1:** The spectrum between deterministic and stochastic behavior.

_**We have to bridge this divide.**_ As developers, we need to understand and adapt these data science tools for our needs. This will mean learning some probability and statistics concepts, but we shouldn't need to become experts. Similarly, our AI-expert colleagues need to better understand our needs, so they can help us take their work and use it to deliver reliable, trustworthy AI-enabled products.

## Project Goals

The goals of this project are two fold:

1. Develop and document strategies and techniques for testing Generative AI applications that eliminate nondeterminism, where feasible, and where not feasible, still allow us to write effective, repeatable and automatable tests. This work also impacts architecture and design decisions.
2. Publish detailed, reusable examples and guidance for developers and AI experts on these strategies and techniques.

## Overview of This Site

We start with a deeper dive into [The Problems of Testing Generative AI Applications]({{site.baseurl}}/testing-problems).

Then we discuss [Architecture and Design]({{site.baseurl}}/arch-design) concepts that are informed by the need for effective testing to ensure our AI applications are reliable and do what expect of them. We explore how tried and true principles still apply, but updates are often needed:
* [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/): TDD is really a _design_ methodology as much as a _testing_ discipline, despite the name, promoting incremental delivery and iterative development. What do AI-specific tests look like in a TDD context?
* [Component Design]({{site.baseurl}}/arch-design/component-design): How do classic principles of _coupling_ and _cohesion_ help us encapsulate generative AI behaviors in ways that make them easier to develop, test, and integrate into whole systems?

With this background on architecture and design principles, we move to the main focus of this site, [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies/) that ensure our confidence in AI-enabled applications:
* [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification): Cases where non-LLM tools can test our LLM results.
* [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing): Testing at the scale of large, complex systems is also less deterministic than in the context of [Unit Tests]({{site.glossaryurl}}/#unit-test), etc. What lessons can we learn here?
* [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks): Adapting [Benchmark]({{site.glossaryurl}}/#benchmark) techniques for unit testing and similarly for [Integration Testing]({{site.glossaryurl}}/#integration-testing) and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-testing).
* [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge): Using a &ldquo;smarter&rdquo; LLM to judge application behaviors.
* [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests): Embracing statistical analysis. What's the minimum you need to know? How do you use these techniques?
* [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning): Should we rethink testing as a strategy? If so, how would this change affect AI application architecture and design?

Finally, there is a [Glossary of Terms]({{site.glossaryurl}}) and [References]({{site.baseurl}}/references) for additional information.

## How to Use This Site

This site is primarily designed to be read from beginning to end, but who does that anymore?? We suggest you at least skim the content that way, then go to areas of particular interest. For example, if you already know [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development), you could read just the parts that discuss what's unique about TDD in the AI context, then follow links to other sections for more details.

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
