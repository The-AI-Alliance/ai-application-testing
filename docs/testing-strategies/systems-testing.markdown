---
layout: default
title: Lessons from Systems Testing
nav_order: 350
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

Quality assurance professionals have long dealt with the challenges of testing whole systems, where determinism and isolation are rare guaranteed, because real world scenarios usually include concurrent, distributed systems, failing hardware and software components, etc. What lessons can we learn from this expertise?

{: .todo}
> **TODO:** This chapter needs contributions from experts. See [this issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/26){:target="_blank"} and [Contributing]({{site.baseurl}}/contributing) if you would like to help.


<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO

Most real-world, &ldquo;enterprise-grade&rdquo; applications today are distributed systems where various services (generically, [&ldquo;Components&rdquo;]({{site.glossaryurl}}/#component)) are invoked asynchronously, sometimes across different cloud environments, and the application has to orchestrate the invocations and processing of responses. This leads to all sorts of derived requirements, like effective security, _graceful failure_ when network or subsystem failures occur, etc.

However, for our purposes, the most interesting aspect is the inherently nondeterministic behavior in such systems, because distributed and concurrent invocations of components won't have deterministic response times and results. As one example, network congestion between distributed services means that responses won't arrive in a predictable order. For example, the ubiquitous networking protocol [TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol){:target="_blank"} is designed with the _expectation_ that the packets for a message will arrive in any order and they must be re-sequenced once all are received.

Fortunately, these kinds of nondeterminism are bounded and well understood. Standard techniques for handling them are mature and standard practice for experienced teams. In the TCP example, one _deterministic_ test could send a sequence of all packets for message in all possible orders and confirm that the TCP implementation correctly re-sequences them in the correct order. Additional tests could randomly vary the time delays between packet arrivals and verify that TCP handles this behavior seamlessly. (The protocol is designed for this, too, with specific handling for packets that appear _lost in transmission_, where a protocol involving timeouts and retries is used.)

In a sense, we explored this lesson already; our healthcare ChatBot is designed to detect FAQs, like prescription refill requests. Our analog of the TCP handling of lost packets roughly corresponds to our questions about handling edge cases; messages that are ambiguous and may or may not be actual refill requests. However, the situation in our example is less clear-cut, so we explored statistical techniques for decision making in [Statistical Evaluation]({{site.baseurl}}/testing-strategies/statistical-tests/).

{: .todo}
> **TODOs:**
>
> 1. Research the work of experts in this area. For example, explore the work pioneered by Netflix for deliberately triggering component failures so that the the systems were appropriately designed to handle them as _normal_ occurrences. 
> 1. Provide specific examples of how to use those concepts.

## Experiments to Try

{: .todo}
> **TODO:** We will expand this section once more content is provided above.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning/).

---
