---
layout: default
title: Component Design
nav_order: 220
parent: Architecture and Design for Testing
has_children: false
---

# Component Design

What makes a good [Unit]({{site.glossaryurl}}/#unit)?
What makes a good [Component]({{site.glossaryurl}}/#component), consisting of one or more units?


<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. The classic design principles of [Coupling]({{site.glossaryurl}}/#coupling) and [Cohesion]({{site.glossaryurl}}/#cohesion) still apply: &ldquo;Loosely couple&rdquo; to dependencies. Design each [Component]({{site.glossaryurl}}/#component) with one purpose and clear abstractions.
> 1. Use non-AI components for functionality that is mature and robustly implemented, where performance will be better and more predictable than relying on AI to provide the functionality. Examples include logical reasoning, planning, code verification, etc.
> 1. Encapsulate each generative AI [Model]({{site.glossaryurl}}/#generative-ai-model) and [Agent]({{site.glossaryurl}}/#agent) in a component separate from non-AI components. Build and test the non-AI components in &ldquo;traditional&rdquo; ways.
> 1. Use an AI component's interface to constrain allowed inputs and ensure usable outputs for optimal control and testability, while retaining AI's unique utility. 
> 1. Make testing as deterministic as possible by using [Test Doubles]({{site.glossaryurl}}/#test-double) as a stand-in for an AI component when testing other components that depend on it. If you can't make it completely deterministic, try to _bound_ the scope of responses for test prompts. 
> 1. Leverage other tools, like type checking, to make your interfaces more robust.

<a id="coupling-cohesion"></a>
	
## The Venerable Principles of Coupling and Cohesion

Real applications, AI-enabled or not, combine many components, such as web pages for the user experience (UX), database and/or streaming systems for data retrieval and management, third-party libraries, and external web services. The [Units]({{site.glossaryurl}}/#unit) in these components should be testable in isolation, when their dependencies are well-encapsulated and easy to replace with [Test Doubles]({{site.glossaryurl}}/#test-double) (see also [below](#design-considerations-for-test-doubles)), and most are deterministic or can be made to behave in a deterministic way for testing. Good software design is a _divide and conquer_ strategy. Similar, a collection of units that forms a component should have a clear purpose with understandable [State]({{site.glossaryurl}}/#state) and [Behaviors]({{site.glossaryurl}}/#behavior).

Good abstraction boundaries are the key. The terms [Coupling]({{site.glossaryurl}}/#coupling) and [Cohesion]({{site.glossaryurl}}/#cohesion) embody the qualities of good abstractions, as expressed through language interfaces or web APIs, as appropriate. A well-designed component interface is &ldquo;loosely coupled&rdquo; to its dependencies. Cohesion means it supports a single, logical purpose, with clear behaviors for all its [Functions]({{site.glossaryurl}}/#function) (or other ways of invocation), and state that's easy to comprehend, which follows a well-designed [State Machine]({{site.glossaryurl}}/#state-machine) for any state transitions that can happen.

### Abstractions Encapsulate Complexities

[Michael Feathers]({{site.baseurl}}/references/#michael-feathers) gave a talk recently called [The Challenge of Understandability](https://www.youtube.com/watch?v=sGgkl_RnkvQ){:target="youtube"} at Codecamp Romania, 2024.  

Near the end, he discussed how the software industry has a history of introducing new levels of abstractions when complexity becomes a problem. For example, high-level programming languages removed most of the challenges of writing lower-level assembly code.

From this perspective, the nondeterministic nature of generative AI is a significant source of _complexity_. While generative AI has the potential to provide many benefits (e.g., ease of use for non-technical users, generation of new ideas, productivity acceleration, etc.), it also makes testing and reliability much harder. What kinds of abstractions make sense for AI that would help us manage this new form of complexity?

An AI application is like any other application, except it adds one or more [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) invoked directly through libraries and web services, or invoked indirectly through [Agents]({{site.glossaryurl}}/#agent) and the [Model Context Protocol]({{site.glossaryurl}}/#model-context-protocol) (MCP). 

The first lesson we should apply is to clearly encapsulate AI dependencies separately from the rest of the components that behave deterministically.

{: .highlight }
> All units and components that don't encapsulate models or directly handle model responses should be designed and implemented to be as deterministic as possible and tested using the traditional, deterministic testing techniques.

## Bring in the Experts (i.e., Other Services)

Given the application's responsibilities, which ones should be implemented with AI and which ones should not? Given the challenges of ensuring safe output (e.g., free of hate speech), avoiding hallucination, and in general, ensuring that generative AI outputs are suitable for the intended purpose, here are thoughts about how to assign responsibilities to different kinds of components in your applications.

### Bias Towards Non-AI Tools

Social media is full of examples of the most capable AI systems failing to get basic factual information correct, like historical events, science, etc.

When possible, rely on more reliable methods to find factual information, like search of reputable information repositories, internal data sources accessed through [RAG]({{site.glossaryurl}}/#retrieval-augmented-generation), etc.

Use non-AI tools to perform logical and mathematical reasoning, to do planning and routing, validate code quality, etc. At the very least, use non-AI tools to validate AI responses in live systems, not just as a testing strategy, which we discuss in more detail in [External Verification]({{site.baseurl}}/testing-strategies/external-verification/).

As much as possible, restrict use of generative AI to tasks for which it is most reliable and useful, like translating between human language and tool invocations (and vice-versa), summarization of information retrieved (without allowed extrapolation or speculation), any task that is well constrained and wouldn't require a human who possesses deep intuition or expertise in the subject, if a human performed the task instead.

Popular architectural patterns like RAG and agents emerged because generative models by themselves are not sufficient to do &ldquo;everything&rdquo;.

### Mitigate Risks with Human in the Loop

Use _human in the loop_, meaning require human intervention for any decision or to approve any action with significant consequences. Over time, your confidence in the system might grow to allow greater autonomy, but make sure this confidence is earned.

## Encapsulate Each Model Behind an API

Let's discuss abstractions that wrap AI components, especially direct invocations of models. These abstractions provide several benefits.

### Manipulate the Prompts and Responses

It is common for any interface to an underlying component to do some transformation, filtering, and impose restrictions on invocations. Similarly, it may post-process the results into a more usable form. In production systems, logging and tracing of activity, security enforcement, etc. may occur at these boundaries.

For an AI-enabled unit, allowing open-ended prompts greatly increases the care required to prevent undesirable use and the resulting testing burden. How can the allowed inputs to this unit be constrained, so the AI benefits are still available, but the potential downsides are easier to manage? 

{: .highlight}
> From the perspective of good software engineering practices, exchanging free-form text between humans and tools or between tools is the _**worst possible interface you can use**_, because it is impossible to reason about the behavior, enforce constraints, predict all possible behaviors, and write repeatable, reliable, and comprehensive tests. We will get the benefits of generative AI only if we successfully manage for this serious disadvantage vs. its potential benefits.

When possible, don't provide an open-ended chat interface for inputs, but instead constrain inputs to a set of values from which a prompt is generated for the underlying AI model. This approach allows you to retain the control you need, while often providing a better user experience, too.

A familiar analog is the known security vulnerability, _SQL Injection_, where we should never allow users to specify SQL fragments in plain text that are executed by the system. A malicious user could cause a destructive query to execute. Instead, the user is offered a constrained interface for data and actions that are permitted. The underlying SQL query is generated from that input.

If you do have a chat component, what can you do _immediately_ within the component to transform the user input into a safer, more usable form? 

Similarly, avoid returning &ldquo;raw&rdquo; AI-generated replies. This creates the same kind of significant burden for handling results, which this time has to be borne by the components that depend on the AI component. For _their_ benefit, can you restrict or translate the response in some way that narrows the &ldquo;space&rdquo; of possible results returned to them?

Recall the example unit &ldquo;test&rdquo; benchmark we explored in the [TDD section]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai). For a _frequently asked question_, such as asking for a prescription renewal, we successfully pursued a design where all such questions are mapped to a single, _deterministic_ reply. Hence, it was easy test these responses, although we deferred the question of how to generate a full range of possible patient questions, especially edge cases. For a component depending on this chat API, handling responses is easy, at least for the special cases of known FAQs.

This example is also instructive about the point above concerning how we might transform arbitrary user input into a more constrained and manageable form. In a real patient app, for prescription refill requests, you might return a response to the user like `Okay, I have your request for a refill for miracle drug. I will check your records and get back to you within the next business day.`, while at the same time you invoke a non-AI programmatic API to process the the refill request, `start_refill_request(patient_id = 1234, prescription = "miracle drug");`. No AI is required in that part of the process.

### Hide Model Details

The encapsulation also minimizes awareness of the underlying generative model to components that depend on the encapsulation. We can substitute updated model versions or wholly different models with no API impact. However, even updating an existing model to a newer version often changes how it responds to the same prompts. Fortunately, this can be tested thoroughly using the test suite you already have (right? :grin:) focused on the AI component. 

If there are breaking changes that affect dependents, can you modify how you construct the prompt or process the results to keep the behavior of the abstraction unchanged? If not, and you decide to proceed with the upgrade anyway, dependents will have to be modified accordingly to accommodate the changed behavior.

## Design Considerations for Test Doubles

In [TDD and Generative AI]({{site.baseurl}}/arch-design/#tdd-and-generative-ai), we started our exploration of how to create tests for AI-enabled components. Now let's consider the case where we are [Unit Testing]({{site.glossaryurl}}/#unit-test) _another_, non-AI component that depends on an AI-enabled dependency. Tests, like components, should have a singular purpose, so _all_ unit tests will not want the [Stochastic]({{site.glossaryurl}}/#stochastic) behavior the AI-enabled dependency normally provides, because the unit tests we are writing now will exercise other aspects of behavior.

{: .highlight}
> We said that _all_ the unit tests for this non-AI component should use a test double, _not_ the real AI dependency. We must write unit tests to exercise how the component responds to any potential responses it might receive from the real AI dependency, but the easiest way to do this is to first understand as best we can the _space_ of all possible behaviors, including error scenarios, and then write tests for them that explore this space exhaustively and ensure the component being tested handles them all correctly. In contrast, it will be the [Integration Tests]({{site.glossaryurl}}/#integration-test) that explore what happens with real interactions.

We still need to test the behavior of the component when it interacts with the real AI dependency. This is the role of [Integration Tests]({{site.glossaryurl}}/#integration-test). We fully expect these tests to occasionally catch query-response interactions that we didn't anticipate in our _space_ analysis of possibilities, so they aren't covered by our existing test doubles and unit tests. When this happens, we will need to add or modify our unit tests and test doubles to account for the new behaviors observed.

Some integration tests will not need to talk to the real AI dependency when they exercise other aspects of the integration. We can use test doubles in those cases, perhaps for faster or cheaper execution of those tests. 

Finally, [Acceptance Tests]({{site.glossaryurl}}/#acceptance-test) should never use test doubles, because their purpose is final validation that a _feature_ is working as designed, running in the full, real system, including all generative AI and other _real world_ dependencies.

So, [Test Doubles]({{site.glossaryurl}}/#test-double) take the place of dependencies when needed to ensure predictable behavior, eliminate overhead not needed for the test (like calling a remote service), and to simulate all possible behaviors the real dependency might exhibit, including error scenarios. The simulation role is important to ensure the component being tested is fully capable of handling anything the dependency throws at it. It can also be very difficult to &ldquo;force&rdquo; the real dependency to produce some behaviors, like triggering certain error scenarios.

In traditional software, it is somewhat uncommon for a component developer to also write test doubles of the component for use by other developers depending on the component. At best, the test suite for the dependency might cover all known behaviors the dependency might exhibit, but it is desirable for other components to also test that they _respond_ to all these behaviors correctly. Hence, they need a way to trigger them. In practice, it's up to the user of a dependency to understand it's behaviors (which is good) and write her own test doubles to simulate what the dependency does (not as good).

{: .highlight}
> For a component with non-trivial behaviors, especially complex error scenarios, consider delivering test doubles of the component along with the real component, where the test doubles simulate every possible component behavior.

### Test Doubles for AI Dependencies

When a dependency is an AI component, its test doubles map inputs, such as [Prompts]({{site.glossaryurl}}/#prompt), into [Responses]({{site.glossaryurl}}/#response), allowing the logic of the component we are currently testing to proceed in the usual ways, while exercising all possible responses from the AI component.  

Can we make these test doubles behave deterministically, i.e., return deterministic responses based on the inputs? This is desirable, but it not be completely feasible, as Netflix discovered.

### Test Doubles at Netflix

In [Testing Problems]({{site.baseurl}}/testing-problems/#this-is-not-a-new-problem), we mentioned that Netflix dealt faced the same testing challenges back in 2008 for their recommendation systems. Part of their solution was to write model test doubles that would &ldquo;... dynamically create similar input content for tests classified along the axes that mattered for the algorithm.&rdquo; 

In other words, while test doubles usually hard-code deterministic outputs for their inputs, it may not be possible for AI test doubles, but we should be able to _constraint_ the responses, i.e., use a stochastic model to generate nondeterministic outputs that are within the expected bounds of acceptability, so that tests using these test doubles can fully exercise the component under test with a full range of possible, but acceptable outputs.

However, this also suggests that you should have test doubles that deliberately return _unacceptable_ responses for use when testing error handling and _graceful degradation_ scenarios. Note that we used the word _unacceptable_, not _unexpected_. While it's not possible to fully anticipate all possible generative model outputs, we have to work extra hard to anticipate all possible outputs, good and bad, and design handling accordingly.

Netflix also added extra hidden output that showed the workings of the algorithm, i.e., for [Explainability]({{site.glossaryurl}}/#explainability), when running a test configuration. Details about model weights, algorithmic details, etc. were encoded as HTML comments, visible if their developers viewed the page source. This information helped them understand why a particular list of movies were chosen, for example, in a test scenario.

## More Tools for APIs Design

_Type checking_ is a programming language technique to constrain allowed values for variables and [Function]({{site.glossaryurl}}/#function) arguments and return values. _Dynamically typed_ languages like Python, don't require explicit declarations of types, but many of these languages permit optional type declarations with type checking tools to catch errors in contexts where values of an incompatible type are found. This eliminates a lot of potential bugs. 

In the Python community, [`pydantic`](https://ai.pydantic.dev){:target="pydantic"}is one of these type-checking tools. The project has an [Agent]({{site.glossaryurl}}/#agent) framework called [`pydantic-ai`](https://github.com/pydantic/pydantic-ai/){:target="pydantic-ai"} that uses type checking of results returned by models and other tool invocations to make these interactions more robust.

A different approach to achieving greater resiliency is [OpenDXA with DANA](https://the-ai-alliance.github.io/#ai-powered-programming-language-for-agents){:target="dana"}. Here, they seek to establish better control over model behaviors by automatically learning to be more effective.

---

Review the [highlights](#highlights) summarized above, then proceed to our discussion of [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies).
