---
layout: default
title: Home
nav_order: 10
has_children: false
---

# Developer Testing for GenAI Applications

[GitHub Repo](https://github.com/The-AI-Alliance/developer-testing-guide){:target="repo" .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 .no-glyph}
[The AI Alliance](https://thealliance.ai){:target="ai-alliance" .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 .no-glyph} 

| **Authors** | [FA3: Applications and Tools](https://thealliance.ai/focus-areas/applications-and-tools){:target="ai-alliance-wg"} (See the [Contributors]({{site.baseurl}}/contributing/#contributors)) |
| **History** | V0.0.1, 2024-10-25 16:13 -0500 |

> **Tip:** Use the search box at the top of this page to find specific content.

Welcome to the **The AI Alliance** project to advance the state of the art for **Developer Testing for Generative AI (&ldquo;GenAI&rdquo;) Applications**.  

Using non-deterministic, GenAI [Models]({{site.baseurl}}/glossary/#model) in an application makes it difficult to write [Deterministic]({{site.baseurl}}/glossary/#deterministic), repeatable, and automatable tests. This is a serious concern for application developers, who are accustomed to and rely on determinism when they write [Unit]({{site.baseurl}}/glossary/#unit-test), [Integration]({{site.baseurl}}/glossary/#integration-test), and [Acceptance]({{site.baseurl}}/glossary/#acceptance-test) tests to verify expected behavior and ensure that no [Regressions]({{site.baseurl}}/glossary/#regression) occur as the application code base evolves. 

What can be done about this problem?

## Project Goals

The goals of this project are two fold:

1. Research strategies and techniques for testing GenAI applications that eliminate non-determinism, where feasible, and enable effective testing, where not feasible.
2. Publish guidance for developers on these strategies and techniques, both here and possibly other &ldquo;venues&rdquo;.

This site will be updated regularly to reflect our current thinking and recommendations.

The content is organized into the following sections:

* [The Problems of Testing GenAI Applications]({{site.baseurl}}/testing-problems) - An explanation of the problems in detail.
* [Testing Strategies]({{site.baseurl}}/testing-strategies/testing-strategies) - How to do effective testing of GenAI Applications, despite the non-determinancy.
* [Glossary of Terms]({{site.baseurl}}/glossary) - Definitions of terms. 

Additional links:

* [Contributing]({{site.baseurl}}/contributing): We welcome your contributions! Here's how you can contribute.
* [About Us]({{site.baseurl}}/about): More about the AI Alliance and this project.
* [The AI Alliance](https://thealliance.ai){:target="ai-alliance"}: The AI Alliance website.
* [Project GitHub Repo](https://github.com/The-AI-Alliance/developer-testing-guide){:target="repo"}

