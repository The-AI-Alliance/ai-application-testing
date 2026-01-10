---
layout: default
title: Component Design
nav_order: 210
parent: Architecture and Design for Testing
has_children: false
---

# Component Design

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

What makes a good [Unit]({{site.glossaryurl}}/#unit){:target="_glossary"}?
What makes a good [Component]({{site.glossaryurl}}/#component){:target="_glossary"}, consisting of one or more units? How do good abstraction boundaries help us _divide and conquer_ our challenges?

{: .note}
> **NOTE:** 
> 
> Although technically this chapter is about designing [Units]({{site.glossaryurl}}/#unit){:target="_glossary"} and [Components]({{site.glossaryurl}}/#component){:target="_glossary"}, we'll just use _component_, which is the more conventional term used in the literature about software design principles. We'll use _unit_ more frequently in the next chapter, on [Test-Driven Development]({{site.baseurl}}/tdd/) (TDD), because _unit_ is more conventional the TDD literature. Sorry for any confusion...

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. The classic design principles of [Coupling]({{site.glossaryurl}}/#coupling){:target="_glossary"} and [Cohesion]({{site.glossaryurl}}/#cohesion){:target="_glossary"} still apply: &ldquo;Loosely couple&rdquo; to dependencies and design each [Component]({{site.glossaryurl}}/#component){:target="_glossary"} with one purpose and a clear abstraction.
> 1. Use non-AI components for functionality that is mature and robustly implemented, where performance will be better and more predictable than relying on AI to provide the functionality. Examples include logical reasoning, planning, code verification, etc.
> 1. Encapsulate each generative AI [Model]({{site.glossaryurl}}/#generative-ai-model){:target="_glossary"} and [Agent]({{site.glossaryurl}}/#agent){:target="_glossary"} in a component separate from non-AI components. Build and test the non-AI components in &ldquo;traditional&rdquo; ways.
> 1. Use an AI component's interface to constrain allowed inputs and ensure usable outputs for optimal control and testability, while retaining AI's unique utility. 
> 1. Make testing as deterministic as possible by using [Test Doubles]({{site.glossaryurl}}/#test-double){:target="_glossary"} as a stand-in for an AI component when testing other components that depend on it. If you can't make it completely deterministic, try to _bound_ the scope of responses for test prompts. 
> 1. Leverage other tools, like type checking, to make your interfaces more robust.

<a id="coupling-cohesion"></a>
	
## The Venerable Principles of Coupling and Cohesion

Real applications, AI-enabled or not, combine many components, such as web pages for the user experience (UX), database and/or streaming systems for data retrieval and management, third-party libraries, and external web services. Each of these components should be testable in isolation, when their dependencies are well-encapsulated and easy to replace with [Test Doubles]({{site.glossaryurl}}/#test-double){:target="_glossary"} (see also [below](#design-considerations-for-test-doubles)), and most are deterministic or can be made to behave in a deterministic way for testing. Good software design is a _divide and conquer_ strategy. 

A good component should have a clear purpose with understandable [State]({{site.glossaryurl}}/#state){:target="_glossary"} and [Behaviors]({{site.glossaryurl}}/#behavior){:target="_glossary"}.

Good abstraction boundaries are key. The terms [Coupling]({{site.glossaryurl}}/#coupling){:target="_glossary"} and [Cohesion]({{site.glossaryurl}}/#cohesion){:target="_glossary"} embody the qualities of good abstractions, as expressed through programming language interfaces or web APIs. A well-designed component interface is _loosely coupled_ to its dependencies. It also has high _cohesion_, which means it supports a single, logical purpose, with clear behaviors for all its [Functions]({{site.glossaryurl}}/#function){:target="_glossary"} (or other ways of invocation), and state that's easy to comprehend. If the component state is [Mutable]({{site.glossaryurl}}/#mutable){:target="_glossary"}), state transitions follow a well-designed [State Machine]({{site.glossaryurl}}/#state-machine){:target="_glossary"} of how transitions can happen.

### Abstractions Encapsulate Complexities

[Michael Feathers]({{site.referencesurl}}/#michael-feathers) gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024.  

Near the end, he discussed how the software industry has a history of introducing new levels of abstractions when complexity becomes a problem. For example, high-level programming languages removed most of the challenges of writing low-level assembly code.

From this perspective, the nondeterministic nature of generative AI is a significant source of _complexity_. While generative AI has the potential to provide many benefits (e.g., ease of use for non-technical users, generation of new ideas, productivity acceleration, etc.), it also makes testing and reliability much harder. What kinds of abstractions make sense for AI that would help us manage this new form of complexity?

An AI application is like any other application, except it adds one or more [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model){:target="_glossary"} invoked directly through libraries and web services, or invoked indirectly through [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} and the [Model Context Protocol]({{site.glossaryurl}}/#model-context-protocol){:target="_glossary"} (MCP). 

The first lesson we should apply is to clearly encapsulate AI dependencies separately from the rest of the components that behave deterministically. Then we can focus on the nondeterministic behaviors and how to design and test them.

{: .attention }
> All units and components that don't encapsulate models or directly handle model responses should be designed and implemented to be as deterministic as possible and tested using the traditional, deterministic testing techniques.

## Bring in the Experts (i.e., Other Services)

Given the application's responsibilities, which ones should be implemented with AI and which ones should not? We know we need to that ensure safe output (e.g., free of hate speech), avoid hallucination, and in general, ensure that generative AI outputs are suitable for the intended purpose Here are some thoughts about how to assign responsibilities to different kinds of components in your applications.

### Bias Towards Non-AI Tools

Social media is full of examples of the otherwise-highly capable AI systems failing to get basic factual information correct, like historical events, science, etc.

When possible, rely on more reliable methods to find factual information, like search of reputable information repositories, internal data sources accessed through [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"}, etc.

Use non-AI tools to perform logical and mathematical reasoning, to do planning and routing, validate code quality, etc. At the very least, use non-AI tools to validate AI responses in live systems, not just as a testing strategy, which we discuss in more detail in [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/). [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"} and [MCP]({{site.glossaryurl}}/#model-context-protocol){:target="_glossary"} are popular approaches for tool integration.

As much as possible, restrict use of generative AI to tasks for which it is most reliable and useful, like translating between human language and tool invocations (and vice-versa), summarization of information retrieved (without allowed extrapolation or speculation), any task that is well constrained and wouldn't require a human who possesses deep intuition or expertise in the subject, if a human performed the task instead.

Popular architectural patterns like RAG and agents emerged because generative models by themselves are not sufficient to do &ldquo;everything&rdquo;. Bringing together the best tools for each task creates more reliable AI-enabled applications.

We will look at more specific examples of tools in [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification).

### Mitigate Risks with Human in the Loop

Use _human in the loop_, meaning require human intervention for any decision or to approve any action with significant consequences. Over time, your confidence in the system should grow to allow greater autonomy, but make sure this confidence is earned.

## Encapsulate Each Model Behind an API

Let's discuss abstractions that wrap AI components, especially direct invocations of models. These abstractions provide several benefits.

### Manipulate the Prompts and Responses

It is common for any interface to an underlying component to do some transformation and filtering of inputs and outputs, and also to impose restrictions on invocations (see, in particular, [Design by Contract]({{site.glossaryurl}}/#design-by-contract){:target="_glossary"}). Similarly, it may post-process the results into a more usable form. In production systems, logging and tracing of activity, security enforcement, etc. may occur at these boundaries.

For an AI-enabled unit, allowing open-ended prompts greatly increases the care required to prevent undesirable use and the resulting testing burden. How can the allowed inputs to this unit be constrained, so the AI benefits are still available, but the potential downsides are easier to manage? 

{: .attention}
> From the perspective of good software engineering practices, exchanging free-form text between humans and tools or between tools is the _**worst possible interface you can use**_, because it is impossible to reason about the behavior, enforce constraints, predict all possible behaviors, and write repeatable, reliable, and comprehensive tests. This is a general paradox for APIs; _**the more open-ended the &ldquo;exchanges&rdquo; that are allowed, the more progress and utility are constrained**_. So, we will get the benefits of generative AI only if we successfully manage for this serious disadvantage vs. its potential benefits.

When possible, don't provide an open-ended chat interface for inputs, but instead constrain inputs to a set of values from which a prompt is generated for the underlying AI model. This approach allows you to retain the control you need, while often providing a better user experience, too.

A familiar analog is the known security vulnerability, [SQL Injection](https://en.wikipedia.org/wiki/SQL_injection){:target="_wikipedia"}, where we should never allow users to specify SQL fragments in plain text that are executed by the system. A malicious user could cause a destructive query to execute. Instead, the user is offered a constrained interface for data and actions that are permitted. The underlying SQL query is generated from that input.

If you do have a chat component, what can you do _immediately_ within the component to transform the user input into a safer, more usable form? 

Similarly, avoid returning &ldquo;raw&rdquo; AI-generated replies. This creates the same kind of significant burden for handling results, which this time has to be borne by the components that depend on the AI component. For _their_ benefit, can you restrict or translate the response in some way that narrows the &ldquo;space&rdquo; of possible results returned to them?

In [TDD section]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai), we will explore an example involving _frequently-asked questions_ in a healthcare ChatBot, such as the common request for a prescription renewal. We will see how we can successfully design our prompts so that such questions are mapped to a single, _deterministic_ reply, which is to easy handle downstream, as well as test effectively. Other, more general patient prompts will require different handling.

Hence, we will see that the idea of transforming arbitrary user input into a more a constrained and manageable form, even deterministic outputs, is feasible and reduces our challenges. 

### Hide Model Details

The encapsulation also minimizes awareness of the underlying generative model to components that depend on the encapsulation. We can substitute updated model versions or wholly different models with no API impact. However, even updating an existing model to a newer version often changes how it responds to the same prompts and it may require rewriting the actual prompt _template_ used. Fortunately, such changes can be kept invisible to the users of the AI component. Also, such changes can be tested thoroughly using the test suite you already have (right? :grin:) for the component. 

If there are breaking changes that affect dependents, can you modify how you construct the prompt or process the results to keep the behavior of the abstraction unchanged? If not, and you decide to proceed with the upgrade anyway, dependents will have to be modified accordingly to accommodate the changed behavior.

## Design Considerations for Test Doubles

In [TDD and Generative AI]({{site.baseurl}}/arch-design/#tdd-and-generative-ai), we start our exploration of how to create tests for AI-enabled components. Here, we consider the case where we are [Unit Testing]({{site.glossaryurl}}/#unit-test){:target="_glossary"} _another_, non-AI component that depends on an AI-enabled dependency. Tests, like components, should have a single purpose (_cohesion_), so _all_ unit tests will not want to handle the [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} behavior the AI-enabled dependency normally provides, because the unit tests we are writing now will exercise other aspects of behavior and require deterministic behaviors so these tests are reliable.

{: .attention}
> We said that _all_ the unit tests for this non-AI component should use a test double, _not_ the real AI dependency. We must write unit tests to exercise how the component responds to any potential responses it might receive from the real AI dependency, but the easiest way to do this is to first understand as best we can the _space_ of all possible behaviors, including error scenarios, and then write tests for them that explore this space exhaustively and ensure the component being tested handles them all correctly. In contrast, it should be the [Integration Tests]({{site.glossaryurl}}/#integration-test){:target="_glossary"} that explore what happens with real interactions.

So, we still need to test the behavior of the component when it interacts with the real AI dependency. This is the role of some of the [Integration Tests]({{site.glossaryurl}}/#integration-test){:target="_glossary"}. We fully expect these tests to occasionally catch query-response interactions that we didn't anticipate in our _space_ analysis of possibilities, so they aren't covered by our existing test doubles and unit tests. When this happens, we will need to add or modify our unit tests and test doubles to account for the new behaviors observed.

Also, some integration tests will focus on other, non-stochastic aspects of the integration. Those tests should use test doubles for the AI component, too. 

In contrast, [Acceptance Tests]({{site.glossaryurl}}/#acceptance-test){:target="_glossary"} should _never_ use test doubles, because their _sole_ purpose is final validation that a _feature_ is working as designed, running in the full, real system, including all generative AI and other _real world_ dependencies.

So, [Test Doubles]({{site.glossaryurl}}/#test-double){:target="_glossary"} take the place of dependencies when needed to ensure predictable behavior, eliminate overhead not needed for the test (like calling a remote service), and to simulate all possible behaviors the real dependency might exhibit, including error scenarios. The simulation role is important to ensure the component being tested is fully capable of handling anything the dependency throws at it. It can also be very difficult to &ldquo;force&rdquo; the real dependency to produce some behaviors, like triggering certain error scenarios.

In traditional software, it is somewhat uncommon for a component developer to also deliver test doubles of the component for use in tests for other components that depend on the component. At best, the test suite for the dependency might cover all known behaviors the dependency might exhibit, but it is also essential to test _other_ components that use it to ensure they _respond_ to all these behaviors correctly. Hence, they need a way to trigger all possible behaviors in the dependency. In current practice, it is up to the user of a dependency to understand all the behaviors (which is good to do) and write her own test doubles to simulate all these behaviors (which is a burden).

{: .attention}
> For a component with non-trivial behaviors, especially complex error scenarios, AI-based or not, consider delivering test doubles of the component along with the real component, where the test doubles simulate every possible component behavior.

### Lessons Learned Writing Test Doubles at Netflix

In [Testing Problems]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem), we mentioned that Netflix faced similar testing challenges back in 2008 for their recommendation systems. Part of their solution was to write model test doubles that would &ldquo;... dynamically create similar input content for tests classified along the axes that mattered for the algorithm.&rdquo; 

Netflix also added extra hidden output that showed the workings of the algorithm, i.e., for [Explainability]({{site.glossaryurl}}/#explainability){:target="_glossary"}, when running a test configuration. Details about model weights, algorithmic details, etc. were encoded as HTML comments, visible if their developers viewed the page source. This information helped them understand why a particular list of movies were chosen, for example, in a test scenario.

In their experience, it was not be feasible for all AI test doubles to return deterministic responses. However, they could _constraint_ the responses to fit into defined &ldquo;classes&rdquo; with boundaries of some sort. So, some of our test doubles may sometimes need to use a stochastic model of some kind (generative AI or not) that generates nondeterministic outputs that fit within our identified &ldquo;classes&rdquo;. Those generators are used in  test doubles so that tests for dependent components can see a full range of possible outputs in this &ldquo;class&rdquo;. The tests will have to be designed to handle nondeterministic, but constrained behaviors.

This also suggests that you should have test doubles that deliberately return _unacceptable_ responses, meaning out of acceptable bounds. These test doubles would be used for testing error handling and _graceful degradation_ scenarios. Note that we used the word _unacceptable_, not _unexpected_. While it's not possible to fully anticipate all possible generative model outputs, we have to work extra hard to anticipate all possible outputs, good and bad, and design handling accordingly.

{: .attention}
> Successful, reliable software systems are designed to _expect_ all possible [Scenarios]({{site.glossaryurl}}/#scenario){:target="_glossary"} in all [Use Cases]({{site.glossaryurl}}/#use-case){:target="_glossary"}, including failures of _any_ kind. Encountering an unexpected scenario should be considered a design failure.

## More Tools for APIs Design

Finally, for completeness, there are other traditional tools that make designs more robust.

_Type checking_ is a programming language technique to constrain allowed values for variables and [Function]({{site.glossaryurl}}/#function){:target="_glossary"} arguments and return values. _Dynamically typed_ languages like Python, don't require explicit declarations of types, but many of these languages permit optional type declarations with type checking tools to catch many errors where values with incompatible types are used. This checking eliminates a lot of potential bugs. 

In the Python community, [`pydantic`](https://ai.pydantic.dev){:target="pydantic"}is one of these type-checking tools. The project has an [Agent]({{site.glossaryurl}}/#agent){:target="_glossary"} framework called [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/){:target="pydantic-ai"} that uses type checking of results returned by models and other tool invocations to make these interactions more robust.

A different approach to achieving greater resiliency is [OpenDXA with DANA](https://the-ai-alliance.github.io/#ai-powered-programming-language-for-agents){:target="dana"}. Here, they seek to establish better control over model behaviors by automatically learning to be more effective.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to our discussion of [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/).

---