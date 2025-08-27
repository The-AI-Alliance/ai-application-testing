---
layout: default
title: Coupling and Cohesion
nav_order: 220
parent: Architecture and Design for Testing
has_children: false
---


## Is This Enough?

So, we should carefully design our applications to control where nondeterministic AI behaviors occur and keep the rest of the components as deterministic as possible. Those components can be tested in the traditional ways.

We still have the challenge of testing model behaviors themselves, especially for [Integration]({{site.glossaryurl}}/#integration-test), and [Acceptance]({{site.glossaryurl}}/#acceptance-test) tests that are intended to exercise whole systems or subsystems, including how parts of the system interact with models, both creating queries and processing results. 

--- 

With this background on coupling and cohesion, [Component Design]({{site.baseurl}}/architecture-design/component-design) looks at specific considerations for AI _components_.

