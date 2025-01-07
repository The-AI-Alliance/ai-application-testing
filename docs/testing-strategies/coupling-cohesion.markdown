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

But that still leaves the challenge of testing model behaviors, and for [Integration]({{site.baseurl}}/glossary/#integration-test), and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests that exercise how other parts of the application interact with models, both creating queries and processing results. The rest of the strategies and techniques explore these concerns.

## Possible &ldquo;Tactics&rdquo;

### APIs in AI-based Applications

A hallmark of good software design is clear and unambiguous abstractions with API interfaces between modules that try to eliminate potential misunderstands and guide the user to do the correct things. Exchanging free form text between users and tools is the _worst possible interface_, from this perspective.

Tools like [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/), part of the [`pydantic`](https://ai.pydantic.dev) tools, is an agent framework (one of many...), which is appealing because of its use of type checking for values exchanged between tools, among other benefits.
