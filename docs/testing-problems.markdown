---
layout: default
title: Testing Problems
nav_order: 20
has_children: false
---

# Testing Problems: GenAI Non-determinism 

Generative AI is famously Non-[Deterministic]({{site.baseurl}}/glossary/#deterministic). The same query to a model, e.g., "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_.

In contrast, most software is expected to be deterministic{% fn %}. We'll use the term [Function]({{site.baseurl}}/glossary/#function) for any unit of execution. A function with no [Side Effects]({{site.baseurl}}/glossary/#side-effect), meaning it doesn't read or write state shared with other functions, must always return the same value, e.g, `sin(π) == -1`. You can write an automated test for this that will never fail, unless some [Regression]({{site.baseurl}}/glossary/#regression) causes it to fail. (For floating point results, you have to be careful about roundoff errors.)

However, a function that has side effects, i.e., it reads or writes global state, may return different values, e.g., a function to return a unique UUID or a function that fetches a database record, where that record may have been changed by other processes between function invocations. Distributed systems also do not gaurantee ordering of events, in general. Even in these cases, the indeterminism is well defined and tests can be written that use [Test Doubles]({{site.baseurl}}/glossary/#test-double) for the source of indeterminism (e.g., a fake query to a database), so that the module being tested behaves deterministically during the test.

So, introducing AI-generated content into an application makes it difficult to write deterministic tests that are repeatable and automatable, whether they are [Unit]({{site.baseurl}}/glossary/#unit-test), [Integration]({{site.baseurl}}/glossary/#integration-test), or [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests. This is a serious concern for application developers, who are accustomed to and rely on determinism when they write tests to verify expected behavior and ensure that no regressions occur as the application code base evolves.

It is not possible or even desirable to remove all non-determinism from GenAI applications. However, enabling developers to write deterministic, repeatable, and automatable tests is still feasible. The rest of this documentation explores techniques developers can use.

{% footnotes %}
   {% fnbody %}
      <p>salut</p>
   {% endfnbody %}
{% endfootnotes %}
