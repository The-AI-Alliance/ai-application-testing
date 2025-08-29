---
layout: default
title: Testing Strategies and Techniques
nav_order: 30
has_children: true
---

# Testing Strategies and Techniques

After discussing [architecture and design considerations]({{site.baseurl}}/arch-design/), we turn to testing strategies and techniques that can be used to create reliable, repeatable tests for generative AI applications. 

This is a work in progress, so each page has a list of ideas we are exploring as _TODO_ items. See also the project [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues){:target="issues"}.

{% comment %}
{: .note }
> **NOTE:** Using a [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model) can mean it is managed by the application itself, behind APIs, such as [MCP]({{site.glossaryurl}}/#model-context-protocol) or [Agents]({{site.glossaryurl}}/#agent), or it is used through direct calls to a separate service, like ChatGPT. When discussing models as components, we will often just use _model_ as a shorthand for all these cases.
{% endcomment %}

Start with [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/).
