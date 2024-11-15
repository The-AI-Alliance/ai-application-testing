---
layout: default
title: External Tool Verification
nav_order: 220
parent: Testing Strategies and Techniques
has_children: false
---

# External Tool Verification

Some outputs can be verified through external tools. Some examples:

* **Code generation:** The output can be passed through a parser or compiler to verify the syntax is valid, it has no known security vulnerabilies, it is not too [complex](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="cyclomatic_complexity"}, it uses only allowed libraries, etc.
* **Planning:** A generated plan, e.g., for a new assembly line process, can be checked against a digital model of the assembly line to ensure physical contraints and various heuristics are satisfied.
* **Logic or Mathematics:** Various deterministic tools exist to verify logical arguments, mathematical statements and proofs, etc.

TODOs
1. More high-level examples
2. Details for some of them.

