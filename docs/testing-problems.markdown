---
layout: default
title: Testing Problems
nav_order: 20
has_children: false
---

# Testing Problems: GenAI Non-determinism 

Generative AI is famously [Non-Deterministic]({{site.baseurl}}/glossary/#deterministic). The same query to a model, e.g., "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_.

In contrast, most software is expected to be deterministic. We'll use the term [Function]({{site.baseurl}}/glossary/#function) for any unit of execution. A function with no [Side Effects]({{site.baseurl}}/glossary/#side-effect), meaning it doesn't read or write state shared with other functions, must always return the same value, e.g, `sin(π) == -1`. You can write an automated test for this that will never fail, unless some [Regression]({{site.baseurl}}/glossary/#regression) causes it to fail. (For floating point results, you have to be careful about roundoff errors, of course.)

There are exceptions to deterministic behavior. A function that has side effects, may return different values, e.g., a function to return a unique UUID or a function that fetches a database record, where that record may have been changed by other processes between function invocations. Distributed systems, including multi-threaded applications, also do not guarantee ordering of events for similar reasons. However, even in all these cases, the indeterminism is well understood. Tests can be written using techniques like special-purpose [Test Doubles]({{site.baseurl}}/glossary/#test-double) to ensure determinism during the test, such as using a &ldquo;fake&rdquo; database query to a database. These techniques ensure that the module being tested behaves deterministically during the test<sup>1</sup>.

So, introducing AI-generated content into an application makes it difficult to write deterministic tests that are repeatable and automatable. This is a serious concern for application developers:

* They are accustomed to and rely on determinism when they write tests to verify expected behavior, 
* They use automated tests to ensure that no regressions occur as the application code base evolves,
* They expect to high producitivity, because of the safety provided by robust tests.

It is not possible or even desirable to remove all non-determinism from GenAI applications. However, enabling developers to write tests that are repeatable and automatable, and deterministic when feasible, is still essential. The rest of this documentation explores techniques developers can use.

<sup>1</sup> [Integration]({{site.baseurl}}/glossary/#integration-test) and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests also remove these indeterminisms, except where they focus on the real-world behavior in larger contexts, where the indeterminisms are a crucial factor.

