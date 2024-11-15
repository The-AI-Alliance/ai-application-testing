---
layout: default
title: Unit Benchmarks
nav_order: 220
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

When testing applications with non-deterministic model output, an ad-hoc combination of [Benchmarks]({{site.baseurl}}/glossary/#benchmark) and &ldquo;playing around&rdquo; (manual testing) are typically done today.

Benchmarks are usually very course grained, such as evaluating models at a global level for code generation, Q&A (question and answer), and other abilities. In contrast, good software tests are very specific, examining one specific behavior and keeping everything else _invariant_.

Why not write focused benchmarks? In other words, meet models where they live, not where we would like them to be? 

For example, define a Q&A dataset with very specific and detailed queries and precise answers. Run the queries through the model and use a &ldquo;judge&rdquo; model to examine how well the answers aline with the expected results.

Related: Model as judge.

TODO - More details and specific examples.
