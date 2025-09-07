---
layout: default
title: Lessons from Systems Testing
nav_order: 340
parent: Testing Strategies and Techniques
has_children: false
---

# Lessons from Systems Testing

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Quality assurance professionals have long dealt with the challenges of testing whole systems, where determinism and isolation are not always possible, reflecting the real world conditions that systems face. What lessons can we learn from this expertise?

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO

For example, most real, &ldquo;enterprise-grade&rdquo; applications today are distributed systems where various services are invoked asynchronously, sometimes across different cloud environments, and the application has to orchestrate the invocations and processing of responses. Any distributed system is inherently nondeterministic, because concurrent activities in real-world systems won't have deterministic response times, etc. As one example, network congestion between distributed services means that responses won't arrive in a predictable order. 

Fortunately, these kinds of nondeterminism are bounded and well understood. Standard techniques for handling them are mature and standard practice for experienced teams. So, the first lesson for us is how can we quantify and bound the possible results from models we use?


TODOs:

1. Explore more general concepts and techniques from this community.
1. Provide specific examples of how to use those concepts.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/).

---
