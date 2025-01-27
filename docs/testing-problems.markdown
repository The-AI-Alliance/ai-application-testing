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

In our automated tests, it is straightforward to test the deterministic application core logic by hiding the non-deterministic behaviors behind APIs and replacing them at test time with deterministic and repeatable [Test Doubles]({{site.baseurl}}/glossary/#test-double). Examples include techniques to replace multi-threading with single-threaded execution, using a &ldquo;fake&rdquo; database query API that returns pre-defined results, and a fake UUID generator that always returns a particular value. These techniques ensure that the module being tested behaves deterministically during the tests. [^1]

To recap, application developers expect the following:

* Relying on determinism for tests to verify expected behavior.
* Use of automated tests to ensure that no regressions occur as the application code base evolves.
* High productivity, because of the safety and confidence provided by robust tests.

## How Generative AI Changes This Picture

Generative AI models are famously nondeterministic. The same query to a model, for example, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such expected behavior? Introducing AI-generated content into an application makes it difficult to write deterministic tests that are repeatable and automatable. 

This nondeterminism isn't _peripheral_ either; we introduce generative AI, because we need it to be a central component of fundamentally new applications we are writing, which provide capabilities that were previously impossible.

It is not possible or even desirable to remove all nondeterminism from generative AI applications. However, enabling developers to write tests that are repeatable and automatable, and deterministic when feasible, is still essential. The rest of this documentation explores techniques developers can use.

[^1]: [Integration]({{site.baseurl}}/glossary/#integration-test) and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests also remove nondeterminisms, except where they focus on the real-world behavior in larger contexts, where the nondeterminisms are a crucial factor to be tested.

### Is This Really a New Problem?

Recently, one of us ([Dean Wampler]({{site.baseurl}}/references/#dean-wampler)) posted a link on [Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} to the slides for a talk, [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"}. [Adrian Cockcroft]({{site.baseurl}}/references/#adrian-cockcroft) replied that they encountered similar problems at Netflix around 2008 with their content recommendation systems; &ldquo;The content inventory (movies or products) changes constantly, and the recommendations are personalized so that everyone sees a different result. We had to build some novel practices and tools for our QA engineers.&rdquo; 

The specific tools and practices he mentioned are discussed in the corresponding [Test Strategies and Techniques]({{site.baseurl}}/testing-strategies/testing-strategies) pages, [here]({{site.baseurl}}/testing-strategies/coupling-cohesion/#test-doubles-at-netflix) and [here]({{site.baseurl}}/testing-strategies/statistical-tests/#use-of-statistics-at-netflix).

## Notes about Software Design for Generative AI Applications

The creators of [Test-Driven Development]({{site.baseurl}}/glossary/#test-driven-development) (TDD) made clear that it is really a _design_ discipline as much as a _testing_ discipline. When you write tests before code, you are in the frame of mind of specifying the expected behavior of what you are about to implement, expressed as tests. The iterative nature of TDD encourages you to make minimally-sufficient and incremental changes as you go.

During this process, the software design decisions you make reflect many perspectives, intuitions, and idioms, all built on years of experience. 

### The Paradigm Shift Required in Your Thinking 

Generative models force new perspectives, intuitions, and idioms, reflecting the unique characteristics of these inherently nondeterministic systems. 

The nondeterminism comes from the inherently probabilistic nature of models. Simplicistically, models generate the next most probably &ldquo;element&rdquo, with some randomness to support alternative outputs, such as the next token for language models or the next pixel for image models.

Unfortunately, truly effective testing of models requires some expertise with probabilities and statistics that software developers typically don't require. However, your intuitions are very helpful ...

TODO - more specific details.

### Scope Allowed Inputs and Outputs

Traditional software has well defined interfaces (e.g., APIs) that limit how users invoke services. It may seem paradoxical that constraints are better than no constraints, but this characteristic greatly reduces ambiguities and misunderstanding about behaviors and expectations between the user and the software. In a well-designed interface, the user knows exactly what inputs to provide and the software knows exactly what results to return for a given set of inputs. This greatly simplifies the implementation on both sides of the interface, as no effort is required to deal with ambiguities and poorly-constrained possibilities.

Generative AI Models are effectively _completely open ended_; you can input almost any text you want (often limited only by the length of the query) and you can get almost any response possible in return! From a robust software design perspective, _this is truly a bad idea_, but models have compensating virtues. When they work well, they do a good job interpreting ambiguous human speech, especially from a non-expert, and creating results that accomplish the user's goals. They are very good at generating lots of detailed content in response to relatively little input, especially image generation models.

A vision for [Agent]({{site.baseurl}}/glossary/#agent)-based (or _agentic_) AI is that models can determine for themselves what external services to invoke and how to invoke them, such as determining the weather forecast requested in a query. This also suggests that models have the potential of offering greater integration resiliency compared to conventional software. For example, if a breaking API change occurs in an external service, an _agentic_ system may be able to determine automatically how the behavior changed and how to compensate for it, freeing the developer of this tedium.

### Useful Techniques

Still, the open ended nature means you should consider ways of constraining allowed inputs and filtering results. 

* **Don't expose the model directly:** Hide the model behind an interface with clear constraints. In many applications, a model might be used as a _universal translator_ of sorts between systems with APIs. The user interface might provide a constrained experience, tailored to a particular use case, and the underlying prompts sent to the model might be carefully engineered (based on experimentation) to optimize the model's results.
* **Filter results heavily:** Make sure the user or downstream systems only see model results that are constrained appropriately. For chatbots, this obviously means filtering out objectionable content. For other systems, it might mean removal of _boilerplate_ text and formatting results in a concise, structured way.
