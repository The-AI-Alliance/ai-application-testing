---
layout: default
title: Testing Problems
nav_order: 10
has_children: false
---

# Testing Problems Caused by Generative AI Nondeterminism 

Let's first review why [Determinism]({{site.glossaryurl}}/#determinism) is an important concept in software development, then discuss how the use of [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) makes this difficult.

## Why Determinism is an Important Tool for Software Development

We have learned from decades of experience that creating and maintaining reliable software requires deterministic [Behavior]({{site.glossaryurl}}/#behavior), whenever possible, and when it can't be avoided, principled handling of the nondeterminism. Simply stated, the more [Predictable]({{site.glossaryurl}}/#predictable) and [Repeatable]({{site.glossaryurl}}/#repeatable) the behavior, the easier it is to _reason_ about its [State]({{site.glossaryurl}}/#state) and [Behavior]({{site.glossaryurl}}/#behavior), including aspects of design, testing, and interactions with other software libraries.

To frame the following discussion, We will use the term [Unit]({{site.glossaryurl}}/#unit) for the lowest-granularity encapsulation of some sort of work done by code execution. (We will use [Component]({{site.glossaryurl}}/#component) for larger-granularity collections of units.) Depending on the context, a unit will be a [Function]({{site.glossaryurl}}/#function), a [Class]({{site.glossaryurl}}/#class), or even a distributed service we invoke. 

Furthermore, suppose a unit in question is [Immutable]({{site.glossaryurl}}/#immutable), meaning its [State]({{site.glossaryurl}}/#state) never changes, and it performs no [Side Effects]({{site.glossaryurl}}/#side-effect), meaning it doesn't modify the state of other units, like writing to files, or read state from [Mutable]({{site.glossaryurl}}/#mutable) units, like ask a service for the current weather. This unit will _always_ be deterministic, which means that if we invoke it with the same input repeatedly, we _must always_ receive the same value back. For example, the Mathematics equation `sin(π) == -1` will always be true, and a software implementation of it will always be true, as well (ignoring potential floating point round-off errors...). For such a unit, you can write an automated test that checks this result and it will never, ever fail, _unless_ some new bug, a [Regression]({{site.glossaryurl}}/#regression), causes its behavior to change. 

There are necessary exceptions to this deterministic behavior for real-world systems. Some units will have mutable state, like a stack data structure. Some units will prompt a user for inputs, so the value it returns will rarely be the same value from one invocation to the next. Finally, any distributed systems, including multi-threaded applications, cannot guarantee how events will be ordered, and many cases which events will occur. 

Fortunately, these forms of nondeterminism and side effects are well understood and the range of possible occurrences is usually bounded, allowing effective handling both in tests and in production deployments. We have effective techniques for handling them, which we will review in [Architecture and Design for Testing]({{site.baseurl}}/architecture-design/).

To summarize, application developers expect the following:

* Relying on determinism, _as much as possible_, to enable tests to verify expected behavior.
* Use of repeatable, automated tests to ensure that no regressions occur as the application code base evolves.
* High productivity, because robust, comprehensive test suites provide _confidence_ in the current safety and reliability of the application, and also catch regressions when they occur.

## How Generative AI Changes This Picture

Generative AI models produce inherently nondeterministic output. The same query to a model, for example, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such &ldquo;expected&rdquo; behavior? Introducing AI-generated content into an application makes it difficult, if not impossible, to write deterministic tests that are repeatable and automatable. 

This nondeterminism isn't _peripheral_, i.e., an implementation detail separate from the application logic. We introduce generative AI, because we need it to be a central part of the application logic, allowing us to build fundamentally new applications that provide capabilities that were previously impossible.

It is not possible or even desirable to remove all nondeterminism from generative AI applications. However, enabling developers to write tests that are repeatable and automatable, and deterministic when feasible, is still essential. Most of the rest of this guide explores techniques developers can use.

### This Is Not a New Problem

Recently, [one of us]({{site.baseurl}}/references/#dean-wampler) posted a link on [Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} to the slides for a talk, [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"}. In a private conversation afterwards, [Adrian Cockcroft]({{site.baseurl}}/references/#adrian-cockcroft) said that Netflix encountered similar problems around 2008 with their content recommendation systems: &ldquo;The content inventory (movies or products) changes constantly, and the recommendations are personalized so that everyone sees a different result. We had to build some novel practices and tools for our QA engineers.&rdquo; 

The specific tools and practices he mentioned are discussed in [Test Doubles at Netflix]({{site.baseurl}}/architecture-design/coupling-cohesion/#test-doubles-at-netflix) and [The Use of Statistics at Netflix]({{site.baseurl}}/testing-strategies/statistical-tests/#the-use-of-statistics-at-netflix)

--- 

Before we discuss [Testing Strategies]({{site.baseurl}}/testing-strategies), let's first discuss [Architecture and Design]({{site.baseurl}}/architecture-design), informed by our testing concerns.
