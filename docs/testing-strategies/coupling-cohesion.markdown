---
layout: default
title: Coupling and Cohesion
nav_order: 210
parent: Testing Strategies and Techniques
has_children: false
---

# The Venerable Principles of Coupling and Cohesion

Real applications, AI-enabled or not, combine many subsystems, usually including web pages for the user experience (UX), database and/or streaming systems for data retrieval and management, various libraries and modules, and calls to external services. Each of these [Components]({{site.baseurl}}/glossary/#component) can be tested in isolation and most are deterministic or can be made to behave in a deterministic way for testing.

An AI application adds one or more [Generative AI Models]({{site.baseurl}}/glossary/#generative-ai-model) invoked through libraries or services. _Everything else should be tested in the traditional, deterministic ways._ Invocations of the model should be hidden behind an API abstraction that can be replaced at test time with a [Test Double]({{site.baseurl}}/glossary/test-double). Even for some integration and acceptance tests, use a model test double for tests that _aren't_ exercising the behavior of the model itself.

## Possible &ldquo;Tactics&rdquo;

Let's consider ways our encapsulation APIs can be most effective.

### Test Doubles at Netflix

Adrian Cockcroft [told one of us]({{site.baseurl}}/testing-problems/#is-this-really-a-new-problem) that Netflix wrote model [Test Doubles]({{site.baseurl}}/glossary/test-double) that would &ldquo;... dynamically create similar input content for tests classified along the axes that mattered for the algorithm.&rdquo; In other words, while traditional test doubles usually hard-code deterministic outputs for specific inputs, make the test double for a probabilistic model generate nondeterministic outputs that are within the expected bounds of acceptability, so that tests using these test doubles can fully exercise the _unit_ under test with a full range of possible, but acceptable outputs.

However, this also suggests that test doubles are needed that deliberately write &ldquo;unacceptable&rdquo; output. These would be used to test component error handling for components that ingest and process model output.

Netflix also added extra hidden output that showed the workings of the algorithm (i.e., for [Explainability]({{site.baseurl}}/glossary/#explainability)) when running a test configuration. Details about model weights, algorithmic details, etc. were encoded as HTML comments, visible if you viewed the page source. This information helped them understand why a particular list of movies were chosen, for example, in a test scenario.

The generative AI equivalent of their approach might be to include in the prompt a clause that says something like, &ldquo;in a separate section explain how you came up with the answer&rdquo;. The output of that section is then hidden from end users, but visible to engineers through a page comment or logged somewhere.

### APIs in AI-based Applications

A hallmark of good software design is clear and unambiguous abstractions with API interfaces between modules that try to eliminate potential misunderstands and guide the user to do the correct things. Exchanging free form text between users and tools is the _worst possible interface_, from this perspective.

Tools like [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/), part of the [`pydantic`](https://ai.pydantic.dev) tools, is an agent framework (one of many...), which is appealing because of its use of type checking for values exchanged between tools, among other benefits.

### Abstractions Encapsulate Complexities

[Micheal Feathers](https://michaelfeathers.silvrback.com) gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ) at Codecamp Romania, 2024.  

Near the end, he discussed how the software industry has a history of introducing new levels of abstractions when complexity becomes a problem. For example, high-level programming languages removed most of the challenges of writing lower-level assembly code.

From this perspective, the nondeterministic nature of generative AI is a _complexity_. While it obviously provides benefits (e.g., new ideas, summarization, etc.), it also makes testing harder. What kinds of abstractions make sense for AI that would help us with this form of complexity?

## Is This Enough?

We still have the challenge of testing model behaviors themselves, especially for [Integration]({{site.baseurl}}/glossary/#integration-test), and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests that exercise how other parts of the application interact with models, both creating queries and processing results. The [rest of the strategies and techniques]({{site.baseurl}}/testing-strategies/testing-strategies/) explore these concerns, starting with [External Verification]({{site.baseurl}}/testing-strategies/external-verification/).

