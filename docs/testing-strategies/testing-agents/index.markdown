---
layout: default
title: Testing Agents
nav_order: 350
parent: Testing Strategies and Techniques
has_children: true
---

# Testing Agents

{% comment %}
<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>
{% endcomment %}

So far in this guide, we have focused on testing AI-enabled applications in a generic sense and not focusing on specific concerns for testing [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} and other popular application patterns (like [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"}). 

This section contains several chapters that dive into the design and building of agents, in the [Building Agents](building-agents/) chapter, and how to test and evaluate them, in the [Evaluating Agents](evaluating-agents/) chapter. 

Agents offer broad and increasingly-sophisticated behaviors, working in tandem with LLMs and traditional software services and systems. Agents introduce new challenges for testing. Effective design patterns, development techniques, and tool kits for agents are also rapidly evolving. We won't attempt to cover all these topics in depth here, but we will focus on a few promising techniques and tools for building and testing agents. We include a list of additional resources and tools for further investigation in the [Tools for Agent Development and Testing](./agent-tools/) chapter.

## About Agents

[Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} are a broad class of software components with behaviors that are complementary to the capabilities that models themselves provide. They range from relatively simple to very sophisticated.

In contrast, the original, _simple_ healthcare ChatBot application just adds context information to user queries to create prompts and it uses custom handling of the responses. It relies heavily on an LLM's ability to classify the kind of query, e.g., a prescription refill request, and to extract some useful details from the query, such as the prescription in question, if the patient mentions it. For most such use cases, instead of returning the generated text to the user, the application presents a predefined message corresponding to the classification returned, so we have better control over potentially &ldquo;suboptimal&rdquo; generated responses. However, it can only handle simple queries and responses, not perform any workflows, like manage appointments. 

This is where agents come in. They enable complex workflows, research and report preparation, planning, reasoning, and even autonomous action on your behalf, when allowed to do so. Work is on-going to make agents self-learning, so they can adapt to evolving or new uses without special programming or training. The [next chapter](./building-agents/) will introduce an agent-based ChatBot implementation, called [`ChatBotAgent`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"}, 

An example of a more sophisticated agent is the AI Alliance project [Deep Research Agent for Applications](https://the-ai-alliance.github.io/deep-research-agent-for-applications/){:target="_blank"}, which demonstrates an important agent design pattern, [Deep Research Agent]({{site.glossaryurl}}/#deep-research-agent){:target="_glossary"}, (see, for example, [here](https://openai.com/index/introducing-deep-research/){:target="_blank"} and [here](https://arxiv.org/abs/2506.18096){:target="_blank"}), with several example applications. (It is built on [LastMile AI's](https://www.lastmileai.dev/){:target="lastmile"} agent framework, [MCP Agent](https://github.com/lastmile-ai/mcp-agent){:target="mcp-agent"}.) An example of an even more advanced agent that is very _hot_ at this time is [OpenClaw](https://openclaw.ai){:target="openclaw"}.

Agents are arguably the most rapidly evolving area of the AI ecosystem right now, in part because they are helping to fully realize the potential of AI to transform work and life activities. While we believe the concepts discussed in these chapters will remain relevant for a long time, the specific techniques, tools, and services mentioned will likely change.

## What's Next?

Proceed to the first chapter [Building Agents](./building-agents/), followed by [Evaluating Agents](./evaluating-agents/), and finally [Tools for Agent Development and Testing](./agent-tools/) chapter.

Then review the [highlights](#highlights) in each chapter and proceed to the [Lessons from Systems Testing]({{site.baseurl}}/testing-strategies/systems-testing/).

---
