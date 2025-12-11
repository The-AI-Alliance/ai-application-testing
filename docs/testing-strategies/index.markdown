---
layout: default
title: Testing Strategies and Techniques
nav_order: 30
has_children: true
---

# Testing Strategies and Techniques

After discussing [architecture and design considerations]({{site.baseurl}}/arch-design/), we turn to testing strategies and techniques that can be used to create reliable, repeatable tests for generative AI applications. 

For educational purposes, we demonstrate techniques using relatively simple tools that are easy for you to try. While they are designed to be suitable for research and development processes, we also describe more sophisticated tools that may be necessary for more &ldquo;advanced&rdquo; uses, larger teams, etc. These additional tools are described in sections with titles that begin with **Other Tools...** near the end of each chapter. Also, note that many startups and consulting organizations now offer proprietary tools and services to aid developer testing, but we won't cover those options.

The end of each chapter has an **Experiments to Try** section for further exploration.

{% comment %}
{% endcomment %}
{: .note }
> **NOTE:** 
> 
> Using a [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model){:target="_glossary"} can mean it is managed by the application itself, behind library APIs, or it is accessed as a remote service, such as ChatGPT, or through a protocol like [MCP]({{site.glossaryurl}}/#model-context-protocol){:target="_glossary"}. It can be part of more advanced design patterns like [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} and [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"}. Furthermore, evaluating just models is not sufficient since these other tools can modify prompts and responses. So, just as classic [Unit Tests]({{site.glossaryurl}}/#unit-test){:target="_glossary"}, [Integration Tests]({{site.glossaryurl}}/#integration-test){:target="_glossary"}, and [Acceptance Tests]({{site.glossaryurl}}/#acceptance-test){:target="_glossary"} cover individual [Units]({{site.glossaryurl}}/#unit){:target="_glossary"} to [Components]({{site.glossaryurl}}/#component){:target="_glossary"} that aggregate them, it is really necessary for our AI tests to cover not just model prompts and responses, but units and components they are part of. Nevertheless, for simplicity, we will often work with models directly.

## What's Next?

Start with [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/). Refer to the [Glossary]({{site.glossaryurl}}/){:target="_glossary"} regularly for definitions of terms. See the [References]({{site.baseurl}}/references/) for more information.

---