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

But that still leaves the challenge of testing model behaviors, and for some [Integration]({{site.baseurl}}/glossary/#integration-test), and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests that exercise other parts of the application respond to model queries and results.
