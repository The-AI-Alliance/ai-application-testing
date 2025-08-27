---
layout: default
title: Coupling and Cohesion
nav_order: 220
parent: Architecture and Design for Testing
has_children: false
---

# The Venerable Principles of Coupling and Cohesion

This section is a reminder that the tools that worked well for us in the past are still very useful.

Real applications, AI-enabled or not, combine many [Components]({{site.glossaryurl}}/#component), such as web pages for the user experience (UX), database and/or streaming systems for data retrieval and management, third-party libraries, and external web services. The [Units]({{site.glossaryurl}}/#unit) in these components should be testable in isolation, when their dependencies are well-encapsulated and easy to replace with [Test Doubles]({{site.glossaryurl}}/#test-double), and most are deterministic or can be made to behave in a deterministic way for testing. Good software design is a _divide and conquer_ strategy. 

The terms [Coupling]({{site.glossaryurl}}/#coupling) and [Cohesion]({{site.glossaryurl}}/#cohesion) embody good abstraction design. A well-design component abstraction is &ldquo;loosely coupled&rdquo; to its dependencies and it presents a 

An AI application adds one or more [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) invoked through libraries, web services, [Agents]({{site.glossaryurl}}/#agent), and increasingly using [Model Context Protocol]({{site.glossaryurl}}/#model-context-protocol) (MCP). 

The first lesson we should apply is to clearly encapsulate AI dependencies separately from the rest of the components that behave deterministically.

{: .highlight }
> _All units that don't encapsulate models or directly handle model responses should be made as deterministic as possible and tested using the traditional, deterministic techniques._ 

With the deterministic components handled in traditional ways, now we can focus on the AI-enabled components.

## Encapsulate Each Model Behind an API

Invoking models through an abstraction serves several purposes.

### Tests of Dependencies

When [Unit Testing]({{site.glossaryurl}}/#unit-test) _other_ units that use the model, the regular implementation of the encapsulating API can be replaced at test time with a test double, which _fakes_ handling of [Prompts]({{site.glossaryurl}}/#prompt) and returns deterministic [Responses]({{site.glossaryurl}}/#response) that allow the logic of the unit to be tested in the usual ways. 

Many [Integration Tests]({{site.glossaryurl}}/#integration-test) will cover aspects of how units and components interact that don't require model [Behaviors]({{site.glossaryurl}}/#behavior), so they can also use test doubles this way. Other integration tests and all [Acceptance Tests]({{site.glossaryurl}}/#acceptance-test) need to exercise handling of realistic model invocations.

### Design and Testing of Model Usage

Conversely, the encapsulation makes it easier to write and run focused tests that explore how the model handles the variety of possible, [allowed](#constrain-prompts) prompts and the responses received. _This is where most of the new testing techniques discussed in this guide will be applied._

One benefit of this encapsulation occurs when a new version of the existing model or a potential alternative replacement model needs to be tested. You can run the test suite for the encapsulation unit to see how the proposed replacement behaves compared to the current model in use.

## Design Considerations for Test Doubles

It's common to write a [Test Doubles]({{site.glossaryurl}}/#test-double) for _each_ test, to keep it simple and focused on the particular goals of the test. 

### Test Doubles at Netflix

In [Testing Problems]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem), we mentioned that Netflix dealt faced the same testing challenges back in 2008 for their recommendation systems. Part of their solution was to write model test doubles that would &ldquo;... dynamically create similar input content for tests classified along the axes that mattered for the algorithm.&rdquo; In other words, while traditional test doubles usually hard-code deterministic outputs for specific inputs, make the test double for a probabilistic model generate nondeterministic outputs that are within the expected bounds of acceptability, so that tests using these test doubles can fully exercise the _unit_ under test with a full range of possible, but acceptable outputs.

However, this also suggests that test doubles are needed that deliberately write _unacceptable_ output, for use when testing [Component](#component) error handling and _graceful degradation_ when they ingest and process model output that isn't acceptable. Note that we didn't use the word _unexpected_. While it's not possible to fully anticipate all possible generative model outputs, we have to work extra hard to anticipate all possible outputs (or _kinds_ of them), and design handling accordingly.

Netflix also added extra hidden output that showed the workings of the algorithm, i.e., for [Explainability]({{site.glossaryurl}}/#explainability), when running a test configuration. Details about model weights, algorithmic details, etc. were encoded as HTML comments, visible if their developers viewed the page source. This information helped them understand why a particular list of movies were chosen, for example, in a test scenario.

The generative AI equivalent of their approach might be to include in the prompt a clause that says something like, &ldquo;in a separate section explain how you came up with the answer&rdquo;. The output of that section is then hidden from end users, but recorded for monitoring and debugging purposes by the engineering team.



constrain-prompts


### Designing APIs in AI-based Applications

TODO: BOUNDARIES FOR TEST DOUBLES.

A hallmark of good software design is clear and unambiguous abstractions with API interfaces between components that try to eliminate potential misunderstands and guide the user to do the correct things. 

> Let's be clear; exchanging free-form text for human-tool or tool-tool interactions is the _worst possible interface you can use_, from the perspective of good software development practices, because it undermines predictable, testable behaviors. We will get the benefits of generative AI only if we successfully compensate for this serious disadvantage.

Consider tools like [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/){:target="pydantic-ai"}, part of the [`pydantic`](https://ai.pydantic.dev){:target="pydantic"} tools. It is an example agent frameworks (one of many...) uses type checking of results returned by models and other tool invocations. This introduces an extra level of rigor and validation of the information exchanged.

Projects like [OpenDXA with DANA](https://the-ai-alliance.github.io/#ai-powered-programming-language-for-agents){:target="dana"} are working to establish better control over model behaviors in part by automatically learning to be more effective.

In general, the API encapsulating model inference should interpret the results and translate them into a more predictable, if not fully deterministic, format, so that components that invoke the API experience behaviors more like expect for traditional components, where we know how to design and test them effectively.

### Abstractions Encapsulate Complexities

[Michael Feathers]({{site.baseurl}}/references/#michael-feathers) gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024.  

Near the end, he discussed how the software industry has a history of introducing new levels of abstractions when complexity becomes a problem. For example, high-level programming languages removed most of the challenges of writing lower-level assembly code.

From this perspective, the nondeterministic nature of generative AI is a significant source of _complexity_. While generative AI has the potential to provide many benefits (e.g., ease of use for non-technical users, generation of new ideas, productivity acceleration, etc.), it also makes testing and reliability much harder. What kinds of abstractions make sense for AI that would help us manage this new form of complexity?

## Is This Enough?

So, we should carefully design our applications to control where nondeterministic AI behaviors occur and keep the rest of the components as deterministic as possible. Those components can be tested in the traditional ways.

We still have the challenge of testing model behaviors themselves, especially for [Integration]({{site.glossaryurl}}/#integration-test), and [Acceptance]({{site.glossaryurl}}/#acceptance-test) tests that are intended to exercise whole systems or subsystems, including how parts of the system interact with models, both creating queries and processing results. 

--- 

With this background on coupling and cohesion, [Component Design]({{site.baseurl}}/architecture-design/component-design) looks at specific considerations for AI _components_.

