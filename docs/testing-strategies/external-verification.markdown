---
layout: default
title: External Tool Verification
nav_order: 220
parent: Testing Strategies and Techniques
has_children: false
---

# External Tool Verification

Some outputs can be verified through external tools. Here are some examples.

## Code Generation

Generated code can be checked with several tools for quality and validity. For example:

* Use a parser or compiler to verify the syntax is valid
* Scan for security vulnerabilies
* Check for excessive [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="cyclomatic_complexity"}
* Check it uses only allowed third-party libraries.
* If tests already exist for the generated code (see [Test-Driven Development]({{site.baseurl}}/glossary/#test-driven-development)), does the generated code allow the tests to pass?

## Planning

Applications that use models to generate plans, like delivery routes and assembly line processes, can be checked against digital simulations of these scenarios.

## Logic or Mathematics

Various deterministic tools exist to verify logical arguments, mathematical statements and proofs.

## Science

Models are now being used to model protein structure and generate new, candidate molecules for various purposes. The results can be compared to experimental data and physical models. Candidate molecules can be synthesized to verify the have the desired properties.


TODOs:

1. More high-level examples
2. Details for some of them.

