---
layout: default
title: Unit Benchmarks
nav_order: 220
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

When testing applications with nondeterministic model output, an ad-hoc combination of [Benchmarks]({{site.baseurl}}/glossary/#benchmark) and &ldquo;playing around&rdquo; (manual testing) are typically done today.

Benchmarks are a popular tool for &ldquo;globally&rdquo; evaluating how well models perform categories of activities like code generation, Q&A (question and answer sessions), avoid hate speech, avoid hallucinations, etc. A typical benchmark attempts to provide a wide range of examples across the category and report a single number for the evaluation, usually scaled as a percentage of passing results between 0 and 100%). 

In contrast, good software tests are very specific, examining one specific behavior, while keeping everything else _invariant_.

Why not write focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused very narrowly?

Suppose we want to define unit tests that verify our application does a very good job generating SQL queries from human text. We have tuned a model to be very knowledgeable about the databases, schemas, and typical queries in our organization.

We can build a Q&A dataset for this purpose using logged queries in the past. Some human labeling will likely be required to create human text equivalents for the example queries, which would function as the expected answers. Each _unit benchmark_ could focus on one specific kind of common query for one specific table.

A related approach that is widely used is to leverage a separate model, one that is very smart and expensive to use, as a _judge_ to generate Q&A pairs for the benchmarks.

TODO - More details and specific examples.
