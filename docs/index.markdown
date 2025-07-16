---
layout: default
title: Home
nav_order: 10
has_children: false
---

# Achieving Confidence in Enterprise AI Applications

(Previous Title: _AI Application Testing for Developers_)

## How to Test AI Applications, for Enterprise Developers

_If you are an enterprise developer, you know how to test your traditional software applications, but you may not know how to test your AI-powered applications, which are uniquely **nondeterministic**. This project is building the knowledge and tools you need to achieve the same confidence for your AI applications that you have for your traditional applications._

Welcome to the **The AI Alliance** project to advance the state of the art for **Enterprise Testing of Generative AI (&ldquo;GenAI&rdquo;) Applications**.

> **Tips:**
>
> 1. Use the search box at the top of this page to find specific content.
> 2. Capitalized terms link to a [glossary of terms]({{site.baseurl}}/glossary).

We enterprise software developers know how to write [Repeatable]({{site.baseurl}}/glossary/#repeatable) and [Automatable]({{site.baseurl}}/glossary/#automatable) tests. In particular, we rely on [Deterministism]({{site.baseurl}}/glossary/#determinism) when we write [Unit]({{site.baseurl}}/glossary/#unit-test), [Integration]({{site.baseurl}}/glossary/#integration-test), and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests to verify expected behavior and to ensure that no [Regressions]({{site.baseurl}}/glossary/#regression) occur as our code base evolves. These are core skills in our profession. They give us essential _**confidence**_ that are applications meet our requirements and implement the use cases our customers expect.

Problems arise when we introduce [Genenerative AI Models]({{site.baseurl}}/glossary/#genenerative-ai-model), which are inherently _nondeterministic_,  into our applications. Can we write the same kinds of tests now? If not, what alternative approaches should we use instead?

In contrast, AI experts (model builders and data scientists) use different tools to build their _confidence_ in how their models perform. Specifically, [Probability and Statistics]({{site.baseurl}}/glossary/#probability-and-statistics), tools that were developed long before Generative AI came along, are used to understand the probabilities of possible outcomes, analyze the actual behaviors, and to quantity their confidence in these models. 

![Developer to AI Expert Spectrum]({{site.baseurl}}/assets/images/developer-to-AI-expert-spectrum.png "Developer to AI Expert Spectrum")

**Figure 1:** The spectrum between deterministic and probabilitistic behavior.

_**We have to bridge this divide.**_ As developers, we need to be able to adapt these data science tools to meet our needs. We will need to learn some probability and statistics concepts, but we shouldn't need to become experts. Similarly, our AI expert colleagues need to better understand our needs, in order for us to take their work and deliver reliable, trustworthy products that use AI and use it confidently.

## Project Goals

The goals of this project are two fold:

1. Develop and document strategies and techniques for testing Generative AI applications that eliminate nondeterminism, where feasible, and where not feasible, still allow us to write effective, repeatable and automatable tests.
2. Publish detailed, reusable examples and guidance for developers and AI experts on these strategies and techniques.

> **NOTE:** This is very much a work in progress. This site will be updated frequently to reflect our current thinking, emerging recommendations, and reusable assets. Your [contributions]({{site.baseurl}}/contributing) are most welcome!

The website is organized into the following sections:

* [The Problems of Testing Generative AI Applications]({{site.baseurl}}/testing-problems) - An explanation of the problems in detail.
* [Testing Strategies]({{site.baseurl}}/testing-strategies/testing-strategies) - How to do effective testing of Generative AI Applications, despite the nondeterminancy.
* [Glossary of Terms]({{site.baseurl}}/glossary) - Definitions of terms.
* [References]({{site.baseurl}}/references) - Useful sources of additional information, some of which motivated the ideas here.

Additional links:

* [Contributing]({{site.baseurl}}/contributing): We welcome your contributions! Here's how you can contribute.
* [About Us]({{site.baseurl}}/about): More about the AI Alliance and this project.
* [The AI Alliance](https://thealliance.ai){:target="ai-alliance"}: The AI Alliance website.
* This project's [GitHub Repo](https://github.com/The-AI-Alliance/ai-application-testing){:target="repo"}

| **Authors**     | The AI Alliance [Trust and Safety](https://thealliance.ai/focus-areas/trust-and-safety){:target="ai-alliance-tns"} and [Applications and Tools](https://thealliance.ai/focus-areas/applications-and-tools){:target="ai-alliance-apps"} work groups. (See the [Contributors]({{site.baseurl}}/contributing/#contributors)) |
| **Last Update**  | V0.1.0, 2025-07-16 |
