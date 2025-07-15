---
layout: default
title: External Tool Verification
nav_order: 220
parent: Testing Strategies and Techniques
has_children: false
---

# External Tool Verification

For some applications, the utility and quality of model outputs can be verified using external, non-generative tools. Here are some examples.

## Code Generation

Generated code can be checked for quality and validity and, in some cases, modified into a more desirable form. For example:

* Use a parser or compiler to verify the syntax is valid.
* Scan for security vulnerabilities.
* Scan for conformance to project code formatting conventions. This is a case where transforming the code might occur.
* Check for excessive [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="cyclomatic-complexity"}
* Check that it uses only allowed versions of allowed third-party libraries, e.g., those approved by the organization and versions that have no known vulnerabilities.
* If tests already exist for the generated code (see [Test-Driven Development]({{site.baseurl}}/glossary/#test-driven-development)), verify the generated code allows the tests to pass.

## Planning

Planning is a common technique used in industrial applications, like assembly lines, determining near-optimal deliver routes, etc.

Applications that use models to generate plans can be checked against digital simulations of these scenarios. Why not just use the digital simulation in the first place? In some cases the model might produce candidate results faster, while the simulation might provide fast verification. In other cases, limitations of the simulation might be compensated for by the model's abilities.

## Reasoning, Logic, and Other Mathematics

Various deterministic tools exist to verify logical arguments are sound, mathematical statements and proofs are valid, etc.

## Science

Models are sometimes used to generate new ideas for certain research problems, which can then be validated through traditional means.

For example, protein structure models can generate new, candidate molecules for various purposes. The results can be compared to experimental data and physical simulation models. Candidate molecules can be synthesized to verify the have the desired properties.


TODOs:

1. Add more examples where tools can be used.
1. Expand the details for some of them.
