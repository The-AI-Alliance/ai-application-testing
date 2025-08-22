---
layout: default
title: Testing Problems
nav_order: 10
has_children: false
---

# Testing Problems Caused by Generative AI Nondeterminism 

Let's first review why [Determinism]({{site.glossaryurl}}/#determinism) is an important concept in software development, then discuss how use of [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) makes this difficult.

## Why Determinism is an Important Tool for Software Development

We have learned from decades of experience that creating and maintaining reliable software requires deterministic behavior, whenever possible, and when it can't be avoided, principled handling of the nondeterminism. Simply stated, the more [Predictable]({{site.glossaryurl}}/#predictable) and [Repeatable]({{site.glossaryurl}}/#repeatable) the behavior, the easier it is to _reason_ about it, including aspects of design, testing, and interactions with other software libraries.

To frame the following discussion, let's use the term [Unit]({{site.glossaryurl}}/#unit) for the lowest-granularity encapsulation of some sort of work done by code execution. Often, a unit is a [Function]({{site.glossaryurl}}/#), but it could be a distributed service we invoke. Furthermore, let's start with the constraint that the unit has no [Side Effects]({{site.glossaryurl}}/#side-effect), meaning it doesn't read or write _state_ (e.g., values of variables) shared with other units and it doesn't perform input or output with the &ldquo;world&rdquo;, such as writing a new file or checking the current weather...

So, to be specific, determinism of a unit like this means that if we invoke it with the same input repeatedly, we must always receive the same value back. For example, `sin(π) == -1` should always be true (ignoring potential floating point round-off errors...). For such a unit, you can write an automated test that checks this result and it will never, ever fail, _unless_ some new bug, a [Regression]({{site.glossaryurl}}/#regression), causes its behavior to change. 

There are necessary exceptions to deterministic behavior for real-world systems. A unit that prompts the user for something to do and returns the answer will rarely return the same value. A unit that fetches a database record may return a value that was changed in the database since the last time the record was retrieved. Distributed systems, including multi-threaded applications, also cannot guarantee how events will be ordered for many reasons. 

Fortunately, these forms of nondeterminism and side effects are well understood and the range of possible occurrences is usually bounded, allowing effective handling both in tests and in production deployments. Also, they are typically _peripheral_ to the core application logic, such as how things are _implemented_ to scale effectively, but not logically connected to the task itself. This separation makes testing much easier, which we'll discuss a bit more in [Coupling and Cohesion]({{site.baseurl}}/architecture-design/coupling-cohesion).

To recap, application developers expect the following:

* Relying on determinism for tests to verify expected behavior.
* Use of repeatable, automated tests to ensure that no regressions occur as the application code base evolves.
* High productivity, because robust, comprehensive test suites provide _confidence_ in the current safety and reliability of the application, and also catch regressions when they occur.

## How Generative AI Changes This Picture

Generative AI models produce inherently nondeterministic output. The same query to a model, for example, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such &ldquo;expected&rdquo; behavior? Introducing AI-generated content into an application makes it difficult to write deterministic tests that are repeatable and automatable. 

This nondeterminism behavior isn't _peripheral_ either; we introduce generative AI, because we need it to be a central part of the application logic, allowing us to build fundamentally new applications that provide capabilities that were previously impossible.

It is not possible or even desirable to remove all nondeterminism from generative AI applications. However, enabling developers to write tests that are repeatable and automatable, and deterministic when feasible, is still essential. Most of the rest of this website explores techniques developers can use.

[^1]: Even [Integration]({{site.glossaryurl}}/#integration-test) and [Acceptance]({{site.glossaryurl}}/#acceptance-test) tests sometimes remove nondeterministic behaviors, e.g., by artificially forcing the system to exhibit sequential behavior in parts that would normally run concurrently, when the test is covering other aspects of systemic behavior. Other tests will be needed to focus specifically on the real-world behavior of the system where the nondeterministic behaviors occur.

### This Is Not a New Problem

Recently, [one of us]({{site.baseurl}}/references/#dean-wampler) posted a link on [Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} to the slides for a talk, [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"}. In a private follow up, [Adrian Cockcroft]({{site.baseurl}}/references/#adrian-cockcroft) said that they encountered similar problems at Netflix around 2008 with their content recommendation systems. &ldquo;The content inventory (movies or products) changes constantly, and the recommendations are personalized so that everyone sees a different result. We had to build some novel practices and tools for our QA engineers.&rdquo; 

The specific tools and practices he mentioned are discussed in [Test Doubles at Netflix]({{site.baseurl}}/architecture-design/coupling-cohesion/#test-doubles-at-netflix) and [The Use of Statistics at Netflix]({{site.baseurl}}/testing-strategies/statistical-tests/#the-use-of-statistics-at-netflix)

--- 

Before we discuss [Testing Strategies]({{site.baseurl}}/testing-strategies), let's first discuss [Architecture and Design]({{site.baseurl}}/architecture-design), informed by our testing concerns.
