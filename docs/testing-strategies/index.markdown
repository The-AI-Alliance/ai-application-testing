---
layout: default
title: Testing Strategies and Techniques
nav_order: 30
has_children: true
---

# Testing Strategies and Techniques

After discussing [architecture and design considerations]({{site.baseurl}}/arch-design/), we turn to testing strategies and techniques that can be used to create reliable, repeatable tests for generative AI applications. 

This is a work in progress, so each page has a list of ideas we are exploring as _TODO_ items. See also the project [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues){:target="issues"}.

For educational purposes, we demonstrate techniques using relatively simple tools that are easy for you to try, then we describe more sophisticated tools that are available for more &ldquo;advanced&rdquo; research and development scenarios.

{% comment %}
{% endcomment %}
{: .note }
> **NOTE:** Using a [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model) can mean it is managed by the application itself, behind library APIs, or it is accessed as a remote service, such as ChatGPT, or through a protocol like [MCP]({{site.glossaryurl}}/#model-context-protocol). It can be part of more advanced design patterns like [Agents]({{site.glossaryurl}}/#agent) and [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation). Furthermore, evaluating just models is not sufficient since these other tools can modify prompts and responses. So, just as classic [Unit Tests]({{site.glossaryurl}}#unit-test), [Integration Tests]({{site.glossaryurl}}#integration-test), and [Acceptance Tests]({{site.glossaryurl}}#acceptance-test) cover individual [Units]({{site.glossaryurl}}#unit) to [Components]({{site.glossaryurl}}#component) that aggregate them, it is really necessary for our AI tests to cover not just model prompts and responses, but units and components they are part of. Nevertheless, for simplicity, we will mostly work with models directly.

## What's Next?

Start with [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/).

---