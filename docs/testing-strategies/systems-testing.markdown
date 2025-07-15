---
layout: default
title: Lessons from Systems Testing
nav_order: 230
parent: Testing Strategies and Techniques
has_children: false
---

# Lessons from Systems Testing

Quality assurance professionals have long dealt with the challenges of testing whole systems, where determinism and isolation are not always possible, reflecting the real world conditions that systems face. What lessons can we learn from this expertise?

For example, most real, &ldquo;enterprise-grade&rdquo; applications today are distributed systems where various services are invoked asynchronously, sometimes across different cloud environments, and the application has to orchestrate the invocations and processing of responses. Any distributed system is inherently nondeterministic, because concurrent activities in real-world systems won't have deterministic response times, etc. As one example, network congestion between distributed services means that responses won't arrive in a predictable order. 

Fortunately, these kinds of nondeterminism are bounded and well understood. Standard techniques for handling them are mature and standard practice for experienced teams.

Testing these real world systems, ...


TODOs:

1. Cite examples of systems testing concepts and techniques.

