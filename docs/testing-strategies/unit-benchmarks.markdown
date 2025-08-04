---
layout: default
title: Unit Benchmarks
nav_order: 240
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

When testing applications with nondeterministic model output, an ad-hoc combination of [_benchmarks_]({{site.glossaryurl}}/#benchmark) and &ldquo;playing around&rdquo; (manual testing) are typically done today.

Benchmarks are a popular tool for &ldquo;globally&rdquo; evaluating how well models perform categories of activities like code generation, Q&A (question and answer sessions), avoid hate speech, avoid hallucinations, etc. A typical benchmark attempts to provide a wide range of examples across the category and report a single number for the evaluation, usually scaled as a percentage of passing results between 0 and 100%). 

In contrast, good software tests are very specific, examining one specific behavior, while keeping everything else _invariant_.

Why not write focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused very narrowly?

Suppose we want to define unit tests that verify our application does a very good job generating SQL queries from human text. We have tuned a model to be very knowledgeable about the databases, schemas, and typical queries in our organization.

We can build a Q&A dataset for this purpose using logged queries in the past. Some human labeling will likely be required to create human text equivalents for the example queries, which would function as the expected answers. Each _unit benchmark_ could focus on one specific kind of common query for one specific table.

What about the cost of running lots of examples through your LLM? Say you have 100 examples in each fine-grained unit benchmark and yo have 100 of those benchmarks. How long with each full test run take for those 10,000 invocations and how expensive will they be? 

For traditional unit testing, your development environment might only invoke the tests associated with the source files that have just changed, saving a full run for occasional purposes, like before saving changes to version control. Can you develop a similar strategy here, where only a subset of your unit benchmarks are invoked for incremental updates, while the full suite is only invoked occasionally? 

To reduce testing time and costs, could you use a version of your production model that is quantized or a version with fewer parameters? Will the results during unit testing be good enough that running against the production model can be saved for periodic integration test runs? The smaller model may allow you to do inference on your development machine, rather than calling a service for every invocation, which is slow and expensive!

A related approach that is widely used is to leverage a separate model, one that is very smart and expensive to use, as a _judge_ to generate Q&A pairs for the benchmarks. See [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge).

TODO - More details and specific examples.
