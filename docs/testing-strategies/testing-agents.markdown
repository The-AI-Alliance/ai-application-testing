---
layout: default
title: Testing Agents
nav_order: 360
parent: Testing Strategies and Techniques
has_children: false
---

# Testing Agents

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Agents are inherently more complex than application patterns that use &ldquo;conventional&rdquo; code wrapping invocations of LLMs. Agents are evolving to be more and more autonomous in their capabilities, requiring special approaches to testing. This chapter explores the requirements and available approaches.

{: .todo}
> **TODO:** 
> 
> This chapter needs contributions from experts. See [this issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/39){:target="_blank"} and [Contributing]({{site.baseurl}}/contributing) if you would like to help.


<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO



{: .todo}
> **TODOs:**
>
> 1. Research the work of experts in this area. See the following list.
> 1. Catalog the unique requirements for agent testing.
> 1. Provide specific examples of how to use those concepts.

A list of agent-related tools and techniques to investigate:

* PyTorch OpenEnv:
    * https://meta-pytorch.org/OpenEnv/
    * https://huggingface.co/blog/openenv
    * https://huggingface.co/openenv
    * https://github.com/meta-pytorch/OpenEnv
    * Agent Beats Competition:
        * https://www.linkedin.com/posts/jspisak_agentic-ai-weekly-berkeley-rdi-january-activity-7414721490018906112-UbpX
        * https://berkeleyrdi.substack.com/p/agentic-ai-weekly-berkeley-rdi-january
* https://research.ibm.com/blog/cuga-agent-framework
    * https://github.com/cuga-project/cuga-agent
    * https://huggingface.co/blog/ibm-research/cuga-on-hugging-face
* https://partnershiponai.org/resource/prioritizing-real-time-failure-detection-in-ai-agents/
* www.anthropic.com/engineering/multi-agent-research-system
* Mozilla's `any-agent`:
    * https://www.mozilla.ai/open-tools/choice-first-stack/any-agent
    * https://github.com/mozilla-ai/any-agent
* https://agenttoolkit.github.io/agent-lifecycle-toolkit/
* https://github.com/agentsmd/agents.md
* https://glaforge.dev/talks/2025/12/02/ai-agentic-patterns-and-anti-patterns/
* https://www.microsoft.com/en-us/research/blog/agent-lightning-adding-reinforcement-learning-to-ai-agents-without-code-rewrites/
* https://www.patronus.ai/blog/introducing-generative-simulators
* https://github.com/rustyoldrake/security_governance_compliance_ai_agentic
* https://mellea.ai/
* https://openagi.aiplanet.com/ - "OpenAGI"

<a id="other-tools"/>

## Other Tools for Testing Agents

### DoomArena

[DoomArena](https://servicenow.github.io/DoomArena/){:target="_blank"} from [ServiceNow](https://www.servicenow.com/){:target="_blank"} is a framework for testing AI Agents against evolving security threats. It offers a modular, configurable, plug-in framework for testing the security of AI agents across multiple attack scenarios.

DoomArena enables detailed threat modeling, adaptive testing, and fine-grained security evaluations through real-world case studies, such as τ-Bench and BrowserGym. These case studies showcase how DoomArena evaluates vulnerabilities in AI agents interacting in airline customer service and e-commerce contexts.

Furthermore, DoomArena serves as a laboratory for AI agent security research, revealing fascinating insights about agent vulnerabilities, defense effectiveness, and attack interactions.

### Google's Agent Development Kit

Google's [Agent Development Kit](https://google.github.io/adk-docs/){:target="adk"} has a chapter called [Why Evaluate Agents?](https://google.github.io/adk-docs/evaluate/){:target="adk"}, which provides tips for writing evaluations specifically tailored for agents.

### LastMile AI's MCP Eval

[MCP Eval](https://mcp-eval.ai/){:target="mcp-eval"} is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation. It is built on [MCP Agent](https://mcp-agent.com/){:target="mcp-agent"}, their agent framework that emphasizes MCP as the communication protocol.

### IBM's AssetOpsBench

[AssetOpsBench](https://github.com/IBM/AssetOpsBench){:target="ibm-aob"} is a unified framework for developing, orchestrating, and evaluating domain-specific AI agents in industrial asset operations and maintenance. It is designed for maintenance engineers, reliability specialists, and facility planners, it allows reproducible evaluation of multi-step workflows in simulated industrial environments.

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will expand this section once more content is provided above.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Advanced Techniques]({{site.baseurl}}/advanced-techniques/).

---
