---
layout: default
title: Advanced Techniques
nav_order: 40
has_children: true
---

# Advanced Techniques

In [Architecture and Design for Testing]({{site.baseurl}}/arch-design/), we discussed the impact of generative AI on conventional software architecture and design, including the long-standing practice of [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/). In [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies/), we explored the techniques based on probabilities and statistics to evaluate AI systems, and adapted those techniques to application testing needs.

However, both sections assumed that software development principles and practices won't change fundamentally with the introduction of AI. This section explores more advanced techniques, including ways that AI might stimulate more fundamental changes in software development, both generally and in the specific context of application testing. Because this section is more forward looking, it is also more speculative.

We consider the following topics:

* [Specification-Driven Development]({{site.baseurl}}/advanced-techniques/sdd/): As the scope and power of code generation improves, it becomes more and more important to structure effective prompts. How can we specify enough detail using human language (e.g., English) to allow models to generate and validate whole applications?
* [Can We Eliminate Source Code?]({{site.baseurl}}/advanced-techniques/eliminate-source-code/) Computer scientists have wondered for decades why we still program computers using structured text, i.e., programming languages. Attempts to switch to alternatives, such as graphical &ldquo;drag-and-drop&rdquo; environments, have failed (with a few exceptions). Could generative AI finally eliminate the need for source code?
* [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/): Our current approach to testing is to use tests to detect suboptimal behavior, fix it somehow, then repeat until we have the behavior we want. [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} processes already exist for improving various characteristics of models. Can we use them in iterative and incremental process of tuning process that adapts the model or application to the desired behavior? Put another way, can the system automatically learn to pass the tests?

There is currently also a chapter of [&ldquo;rough notes&rdquo;]({{site.baseurl}}/advanced-techniques/notes-on-tuning/) on tuning techniques. This content will eventually be refined and incorporated into other chapters, primarily [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/).

## What's Next?

Start with [Specification-Driven Development]({{site.baseurl}}/advanced-techniques/sdd/), which discusses one approach to making user prompts sufficiently detailed and precise enough that reliable application generation can occur. Refer to the [Glossary]({{site.glossaryurl}}/){:target="_glossary"} regularly for definitions of terms. See the [References]({{site.referencesurl}}/) for more information.

---