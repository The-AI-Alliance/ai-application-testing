---
layout: default
title: Testing Problems
nav_order: 20
has_children: false
---

# Testing Problems Caused by Generative AI Nondeterminism 

Let's first review why [Determinism]({{site.baseurl}}/glossary/#determinism) is an important concept in software development, then discuss how use of [Generative AI Models](#generative-ai-model) makes this difficult.

## Why Determinism is an Important Tool for Software Development

We have learned from decades of experience that creating and maintaining reliable software requires deterministic behavior, whenever possible. We'll use the term [Function]({{site.baseurl}}/glossary/#function) for any unit of execution, even distributed services we invoke. Determinism means that a function with no [Side Effects]({{site.baseurl}}/glossary/#side-effect), meaning it doesn't read or write state shared with other functions, must always return the same value for the same input, e.g, `sin(π) == -1`. You can write an automated test for this that will never fail, unless some [Regression]({{site.baseurl}}/glossary/#regression) causes it to fail. (For floating point results, you have to be careful about roundoff errors, of course.)

There are necessary exceptions to deterministic behavior for real-world systems. A function that has side effects, may return different values, e.g., a function to return a new UUID or a function that fetches a database record, where that record may have been changed by other services between function invocations. Distributed systems, including multi-threaded applications, also usually do not guarantee ordering of events for performance and other reasons. 

Note that these forms of nondeterminism and their side effects are well understood. Their behaviors are easy to reason about and manage. They are usually _peripheral_ to the core application logic. Examples include multi-threading and cluster computing for better scalability and performance, fetching data from a database, and generating UUIDs. 

In our automated tests, it is straightforward to test the deterministic application core logic by hiding the non-deterministic behaviors behind APIs and replacing them at test time with deterministic and repeatable [Test Doubles]({{site.baseurl}}/glossary/#test-double). Examples include techniques to replace multi-threading with single-threaded execution, using a &ldquo;fake&rdquo; database query API that returns pre-defined results, and a fake UUID generator that always returns a particular value. These techniques ensure that the module being tested behaves deterministically during the tests<sup>1</sup>.

To recap, application developers expect the following:

* Relying on determinism for tests to verify expected behavior.
* Use of automated tests to ensure that no regressions occur as the application code base evolves.
* High productivity, because of the safety and confidence provided by robust tests.

## How Generative AI Changes This Picture

Generative AI models are famously nondeterministic. The same query to a model, for example, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such expected behavior? Introducing AI-generated content into an application makes it difficult to write deterministic tests that are repeatable and automatable. 

This nondeterminism isn't _peripheral_ either; we introduce generative AI, because we need it to be a central component of fundamentally new applications we are writing, which provide capabilities that were previously impossible.

It is not possible or even desirable to remove all nondeterminism from generative AI applications. However, enabling developers to write tests that are repeatable and automatable, and deterministic when feasible, is still essential. The rest of this documentation explores techniques developers can use.

<sup>1</sup> [Integration]({{site.baseurl}}/glossary/#integration-test) and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests also remove nondeterminisms, except where they focus on the real-world behavior in larger contexts, where the indeterminisms are a crucial factor to be tested.

