---
layout: default
title: Coupling and Cohesion
nav_order: 210
parent: Architecture and Design for Testing
has_children: false
---

# The Venerable Principles of Coupling and Cohesion

Real applications, AI-enabled or not, combine many [Components]({{site.glossaryurl}}/#components), such as web pages for the user experience (UX), database and/or streaming systems for data retrieval and management, third-party libraries, and external web services. Each of these components can be tested in isolation and most are deterministic or can be made to behave in a deterministic way for testing. Good software design is a _divide and conquer_ strategy. 

An AI application adds one or more [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) invoked through libraries, web services, or [Agents]({{site.glossaryurl}}/#agent), increasingly using [Model Context Protocol]({{site.glossaryurl}}/#model-context-protocol) (MCP). 

{: .highlight }
> _Everything that isn't model output should be made as deterministic as possible and tested using the traditional, deterministic techniques._ 

Invocations of the model should be hidden behind an API abstraction that can be replaced at test time with a [Test Double]({{site.glossaryurl}}/#test-double). Even for some integration and acceptance tests, use a model test double for tests that _aren't_ exercising the behavior of the model itself.

## Possible &ldquo;Tactics&rdquo;

Let's consider ways our encapsulation APIs can be most effective in the context of generative AI.

### Test Doubles at Netflix

Adrian Cockcroft [told one of us]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem) that Netflix wrote model [Test Doubles]({{site.glossaryurl}}/#test-double) that would &ldquo;... dynamically create similar input content for tests classified along the axes that mattered for the algorithm.&rdquo; In other words, while traditional test doubles usually hard-code deterministic outputs for specific inputs, make the test double for a probabilistic model generate nondeterministic outputs that are within the expected bounds of acceptability, so that tests using these test doubles can fully exercise the _unit_ under test with a full range of possible, but acceptable outputs.

However, this also suggests that test doubles are needed that deliberately write _unacceptable_ output, for use when testing [Component](#component) error handling and _graceful degradation_ when they ingest and process model output that isn't acceptable. Note that we didn't use the word _unexpected_. While it's not possible to fully anticipate all possible generative model outputs, we have to work extra hard to anticipate all possible outputs (or _kinds_ of them), and design handling accordingly.

Netflix also added extra hidden output that showed the workings of the algorithm, i.e., for [Explainability]({{site.glossaryurl}}/#explainability), when running a test configuration. Details about model weights, algorithmic details, etc. were encoded as HTML comments, visible if their developers viewed the page source. This information helped them understand why a particular list of movies were chosen, for example, in a test scenario.

The generative AI equivalent of their approach might be to include in the prompt a clause that says something like, &ldquo;in a separate section explain how you came up with the answer&rdquo;. The output of that section is then hidden from end users, but recorded for monitoring and debugging purposes by the engineering team.

### Designing APIs in AI-based Applications

TODO: BOUNDARIES FOR TEST DOUBLES.

A hallmark of good software design is clear and unambiguous abstractions with API interfaces between [Components]({{site.glossaryurl}}/#component) that try to eliminate potential misunderstands and guide the user to do the correct things. 

> Let's be clear; exchanging free-form text for human-tool or tool-tool interactions is the _worst possible interface you can use_, from the perspective of good software development practices, because it undermines predictable, testable behaviors. We will get the benefits of generative AI only if we successfully compensate for this serious disadvantage.

Consider tools like [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/){:target="pydantic-ai"}, part of the [`pydantic`](https://ai.pydantic.dev){:target="pydantic"} tools. It is an example agent frameworks (one of many...) uses type checking of results returned by models and other tool invocations. This introduces an extra level of rigor and validation of the information exchanged.

Projects like [OpenDXA with DANA](https://the-ai-alliance.github.io/#ai-powered-programming-language-for-agents){:target="dana"} are working to establish better control over model behaviors in part by automatically learning to be more effective.

In general, the API encapsulating model inference should interpret the results and translate them into a more predictable, if not fully deterministic, format, so that components that invoke the API experience behaviors more like expect for traditional components, where we know how to design and test them effectively.

### Abstractions Encapsulate Complexities

[Michael Feathers]({{site.baseurl}}/references/#michael-feathers) gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024.  

Near the end, he discussed how the software industry has a history of introducing new levels of abstractions when complexity becomes a problem. For example, high-level programming languages removed most of the challenges of writing lower-level assembly code.

From this perspective, the nondeterministic nature of generative AI is a significant source of _complexity_. While generative AI has the potential to provide many benefits (e.g., ease of use for non-technical users, generation of new ideas, productivity acceleration, etc.), it also makes testing and reliability much harder. What kinds of abstractions make sense for AI that would help us manage this new form of complexity?

## Is This Enough?

So, we should carefully design our applications to control where non-deterministic AI behaviors occur and keep the rest of the [Components]({{site.glossaryurl}}/#component) as deterministic as possible. Those components can be tested in the traditional ways.

We still have the challenge of testing model behaviors themselves, especially for [Integration]({{site.glossaryurl}}/#integration-test), and [Acceptance]({{site.glossaryurl}}/#acceptance-test) tests that are intended to exercise whole systems or subsystems, including how parts of the system interact with models, both creating queries and processing results. 

The [rest of the strategies and techniques]({{site.baseurl}}/testing-strategies/) explore these concerns, starting with [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).

