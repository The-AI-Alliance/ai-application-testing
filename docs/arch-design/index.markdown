---
layout: default
title: Architecture and Design for Testing
nav_order: 20
has_children: true
---

# Architecture and Design for Testing

In [Testing Problems Caused by Generative AI Nondeterminism]({{site.baseurl}}/testing-problems/), we discussed how Generative AI introduces new forms of [Nondeterminism]({{site.glossaryurl}}/#determinism) into applications that break our traditional reliance on deterministic behavior, for reasoning about how the system behaves, for writing repeatable, automatable tests, etc.

Before we discuss [testing strategies]({{site.baseurl}}/testing-strategies/) for AI-enabled applications, let's revisit some tried and true principles of architecture and design that better enable testing, then consider how they apply in this AI era we are in.

This section is a reminder that the tools that worked well for us in the past are still very useful, but some adaptations are required.

* [Component Design]({{site.baseurl}}/component-design/): Adapting classic techniques for good component design, what is different about designing AI components? [Coupling and Cohesion]({{site.baseurl}}/arch-design/component-design/#coupling-cohesion) are classic principles for minimizing [Coupling]({{site.glossaryurl}}/#coupling) between [Components]({{site.glossaryurl}}/#component) and making them logically [Cohesive]({{site.glossaryurl}}/#cohesion). In particular, they help us keep the deterministic (non-AI) vs. nondeterministic (AI) components separate, limiting the scope of new handling required for nondeterminism. 
* [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/): TDD is especially good at encouraging iterative, incremental design and implementation of systems, including comprehensive tests for them. The core principles still apply, but generative AI nondeterminism requires some adaptations. We will also see our first example of a test written for AI. We will also discover a useful scenario where _frequently asked questions_ (FAQs) in a ChatBot can be mapped to deterministic responses and handling in more conventional ways.

The last section in [Testing Strategies]({{site.baseurl}}/testing-strategies), [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning), discusses how we might rethink the role of testing for AI applications and put more emphasis on [Tuning]({{site.glossaryurl}}#tuning) the behaviors to align with our goals, as opposed to a cycle of testing and _bug_ fixing. This idea would influence architecture and design, too, but we'll wait to discuss this influence until that section.

---

After exploring this section on architecture and design, [Component Design]({{site.baseurl}}/arch-design/component-design/) and [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/), proceed to [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies).
