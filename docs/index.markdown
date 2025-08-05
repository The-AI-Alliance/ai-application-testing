---
layout: default
title: Home
nav_order: 10
has_children: false
---

# Achieving Confidence in Enterprise AI Applications

(Previous Title: _AI Application Testing for Developers_)

## I'm an Enterprise Developer: How Do I Test my AI Applications??

_I know how to test my traditional software, which is **deterministic** (more or less...), but I don't know how to test my AI applications, which are uniquely **nondeterministic**._

Welcome to the **The AI Alliance** project to advance the state of the art for **Enterprise Testing of Generative AI (&ldquo;GenAI&rdquo;) Applications**. We are building the knowledge and tools you need to achieve the same testing confidence for your AI applications that you have for your traditional applications.

{% comment %}
> **Tips:**
>
> 1. Use the search box at the top of this page to find specific content.
> 2. _Italicized_ terms link to a [glossary of terms]({{site.glossaryurl}}).
{% endcomment %}

## The Challenge We Face

We enterprise software developers know how to write [Repeatable]({{site.glossaryurl}}/#repeatable) and [Automatable]({{site.glossaryurl}}/#automatable) tests. In particular, we rely on [Deterministism]({{site.glossaryurl}}/#determinism) when we write tests to verify expected behavior and to ensure that no [Regressions]({{site.glossaryurl}}/#regression) occur as our code base evolves. Why is determinism a key ingredient? We know that if we pass the same arguments repeatedly to a function, we will get the same answer back (with special exceptions). This property enables our core testing techniques, which give us essential _**confidence**_ that our applications meet our requirements, that they implement the use cases our customers expect. We are accustomed to _pass/fail_ answers!

Problems arise when we introduce [Generative AI Models]({{site.glossaryurl}}/#genenerative-ai-model), which are inherently [Probabilistic]({{site.glossaryurl}}/#probability-and-statistics) and hence _nondeterministic_. Can we write the same kinds of tests now? If not, what alternative approaches should we use instead?

In contrast, our AI-expert colleagues (model builders and data scientists) use different tools to build their _confidence_ in how their models perform. Specifically, [Probability and Statistics]({{site.glossaryurl}}/#probability-and-statistics), tools that predate Generative AI, are used to understand the _probabilities_ that possible outcomes will be seen, and to analyze and quantify these outcomes _statistically_. This information helps them decide how much to trust their models will be behave as desired. Rarely are _pass/fail_ answers available here.

![Developer to AI Expert Spectrum]({{site.baseurl}}/assets/images/developer-to-AI-expert-spectrum.png "Developer to AI Expert Spectrum")

**Figure 1:** The spectrum between deterministic and probabilitistic behavior.

_**We have to bridge this divide.**_ As developers, we need to understand and adapt these data science tools for our needs. This will mean learning some probability and statistics concepts, but we shouldn't need to become experts. Similarly, our AI-expert colleagues need to better understand our needs, so they can help us take their work and use it to deliver reliable, trustworthy AI-enabled products.

## Project Goals

The goals of this project are two fold:

1. Develop and document strategies and techniques for testing Generative AI applications that eliminate nondeterminism, where feasible, and where not feasible, still allow us to write effective, repeatable and automatable tests.
2. Publish detailed, reusable examples and guidance for developers and AI experts on these strategies and techniques.

The [strategies and techniques]({{site.baseurl}}/testing-strategies/testing-strategies) we will discuss are these:
* [Coupling and Cohesion]({{site.baseurl}}/testing-strategies/coupling-cohesion): We can still use these classic design principles.
* [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification): Cases where non-LLM tools can test our LLM outputs.
* [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing): Testing large, complex systems is also less deterministic. What lessons can we learn here?
* [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks): Adapting [Benchmarks]({{site.glossaryurl}}/#benchmark) as [Unit Tests]({{site.glossaryurl}}/#unit-test).
* [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge): Use a &ldquo;smarter&rdquo; LLM to judge our applications.
* [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests): Embracing statistical analysis.
* [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning): Should we rethink testing as a strategy?

> **NOTE:** This is very much a work in progress. This site will be updated frequently to reflect our current thinking, emerging recommendations, and reusable assets. Your [contributions]({{site.baseurl}}/contributing) are most welcome!

The website is organized into the following sections:

* [The Problems of Testing Generative AI Applications]({{site.baseurl}}/testing-problems) - An explanation of the problems in more detail.
* [Testing Strategies]({{site.baseurl}}/testing-strategies/testing-strategies) - A deeper dive into various techniques for doing effective testing of Generative AI Applications, despite the nondeterminism.
* [Glossary of Terms]({{site.glossaryurl}}) - To be precise in our concepts.
* [References]({{site.baseurl}}/references) - Useful sources of additional information, much of which motivated the ideas here.

## We Need Your Help!

See the [Contributing]({{site.baseurl}}/contributing) page for information on how you can get involved. See the [About Us]({{site.baseurl}}/about) page for more details about this project and the AI Alliance.

## Additional Links

* This project's [GitHub Repo](https://github.com/The-AI-Alliance/ai-application-testing){:target="repo"}
* Companion projects: 
	* <a href="https://the-ai-alliance.github.io/trust-safety-evals/" target="eie">Evaluation Is for Everyone</a>
	* <a href="https://the-ai-alliance.github.io/eval-ref-stack/" target="ers">Evaluation Reference Stack</a>
* The AI Alliance: 
	* [Website](https://thealliance.ai){:target="ai-alliance"}
	* [The Trust and Safety Work Group](https://thealliance.ai/focus-areas/trust-and-safety){:target="ai-alliance-tns"} 

| **Authors**     | The AI Alliance [Trust and Safety](https://thealliance.ai/focus-areas/trust-and-safety){:target="ai-alliance-tns"} and [Applications and Tools](https://thealliance.ai/focus-areas/applications-and-tools){:target="ai-alliance-apps"} work groups. (See the [Contributors]({{site.baseurl}}/contributing/#contributors)) |
| **Last Update**  | V0.1.0, 2025-07-16 |
