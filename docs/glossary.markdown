---
layout: default
title: Glossary of Terms
nav_order: 70
has_children: false
---

# Glossary of Terms

Some of the terms defined here are industry standards, while others are not standard, but they are useful for our purposes.

Some definitions are adapted from the following sources, which are indicated below using the same numbers, i.e., [\[1\]](#mlc) and [\[2\]](#nist):

1. <a id="mlc">[_MLCommons AI Safety v0.5 Benchmark Proof of Concept Technical Glossary_]({{site.baseurl}}/references/#mlcommons-glossary){:id="mlc-glossary"}
2. <a id="nist">[_NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0)_]({{site.baseurl}}/references/#nist-risk-management-framework){:id="nist-rmf"}

Sometimes we will use a term that could be defined, but we won't provide a definition for brevity. We show these terms in _italics_. You can assume the usual, plain-sense meaning for the term, or in some cases it is easy to search for a definition. 

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Acceptance Test

A test that verifies a user-visible feature works are required, often by driving the user interface or calling the external API. These tests are system-wide and are sometimes executed manually. However, it is desirable to make them automated, in which case all operations with [Side Effects](#side-effects) need to be replaced with [Deterministic](#determinism) [Test Doubles](#test-double). See also [Test](#test), [Unit Test](#unit-test), and [Integration Test](#integration-test).

## Agent

An old concept in AI, but now experiencing a renaissance as the most flexible architecture pattern for AI-based applications. Agents are orchestrations of [Generative AI Model](#generative-ai-model) and external service invocations, e.g., planners, schedulers, reasoning engines, data sources (weather, search, ...), etc. In this architecture, the best capabilities of each service and model are leveraged, rather than assuming that models can do everything successfully themselves. Agent-based applications sometimes use multiple models, one per agent, where each one provides some specific capabilities. For example, one model might be process user prompts into back-end API invocations, including to other models, and interpret the results into user-friendly responses.

## AI Actor

[\[2\]](#nist) An organization or individual building an [AI System](#ai-system).

## AI System

Umbrella term for an application or system with AI [Components](#component), including [Datasets](#dataset), [Generative AI Models](#generative-ai-model) (e.g., [LLMs](#large-language-model), [Evaluation Frameworks](#evaluation-framework) and [Evaluations](#evaluations) for safety detection and mitigation, etc., plus external services, databases for runtime queries, and other application logic that together provide functionality.

## Alignment

A general term for how well an [AI System's](#ai-system) outputs (e.g., replies to queries) and [Behaviors](#behavior) correspond to end-user and service provider objectives, including the quality and utility of results, as well as safety requirements. Quality implies factual correctness and utility implies the results are fit for purpose, e.g., a Q&A system should answer user questions concisely and directly, a Python code-generation system should output valid, bug-free, and secure Python code. [EleutherAI]({{site.baseurl}}/references/#eleuther-ai){:target="eleuther"} defines alignment [this way](https://www.eleuther.ai/alignment){:target="eleuther"}, &ldquo;Ensuring that an artificial intelligence system behaves in a manner that is consistent with human values and goals.&rdquo; See also the work of the [Alignment Forum]({{site.baseurl}}/references/#alignment-forum).

## Automatable

Can an action, like a test, be automated so it can be executed without human intervention?

## Behavior

What does a [Component](#component) do, either autonomously on its own (e.g., a security monitoring tool that is constantly running) or when invoked by another component through an API or [Function](#function) call?

## Benchmark

[\[1\]](#mlc) A methodology or [Function](#function) used for offline [Evaluation](#evaluation) of a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system) for a particular purpose and to interpret the results. It consists of:
* A set of tests with metrics.
* A summarization of the results.

## Class

The primary [Component](#component) abstraction in [Object-Oriented Programming](#object-oriented-programming), although not necessarily the only one.

## Component

An ill-defined, but often-used term in software. In this case, we use it to generically refer to any piece of software with a well-defined purpose, an access API that defines clear boundaries. Depending on the programming language, it may group together [Functions](#function), [Classes](#class), etc. Particular programming languages and &ldquo;paradigms&rdquo; (like [OOP](#object-oriented-programming) and [FP](#functional-programming)) might use terms like _packages_, _modules_, _subsystems_, _libraries_, and even _web services_ can be considered components.

## Concurrent

When work can be partitioned into smaller steps that can be executed in any order and the runtime executes them in a nonpredictable order. If the order is predictable, no matter how it executed, we can say it is effectively [Sequential](#sequential).

## Context

Additional information passed to an [LLM](#large-language-model) as part of a user [Prompt](#prompt), which is intended to provide additional, useful _context_ information so that the [Response](#response) is better than if the user's prompt was passed to the LLM alone. This additional content may include a [System Prompt](#system-prompt), relevant documents retrieved using [RAG](#retrieval-augmented-generation), etc.

## Cohesion

Does a [Component](#component) feel like &ldquo;one thing&rdquo; with a single purpose, exhibiting well-defined [Behaviors](#behavior) with a coherent [State](#state)? Or does it feel like a miscellaneous collection of behaviors or state?

## Coupling

How closely connected is one [Component](#component) to others in the system? &ldquo;Loose&rdquo; coupling is preferred, because it makes it easier to test components in isolation, substitute replacements when needed, etc. Strongly coupled components often indicate poor abstraction boundaries between them.

## Dataset

(See also [\[1\]](#mlc)) A collection of data items used for training, evaluation, etc. Usually, a given dataset has a schema (which may be “this is unstructured text”) and some metadata about provenance, licenses for use, transformations and filters applied, etc.

## Determinism

The output of a [Unit](#unit) for a given input is always known precisely. This affords writing repeatable, predictable software and automated, reliable tests.

In contrast, _nondeterminism_ means identical inputs yield different results, removing [Repeatability](#Repeatable) and complicating [Predictability](#predictable), and the ability to write automated, reliable tests.

## Explainability

Can humans understand why the system behaves the way that it does in a particular scenario? Can the system provide additional information about about why it produced a particular output?

## Evaluation

Much like other software, models and AI systems need to be trusted and useful to their users. Evaluation aims to provide the evidence needed to gain users’ confidence for an [AI System](#ai-system).

An particular evaluation is the capability of measuring and quantifying how a [Generative AI Model](#generative-ai-model), e.g., an [LLM](#large-language-model), or an [AI System](#ai-system) as a whole handles [Prompts](#prompt) and the kinds of [Responses](#response) produced. For example, an evaluation might be used to see if hate speech is detected in prompts and responses, if responses contain hallucinations, measure the overhead (time and compute) for processing, and for our purposes, implements a required use case, etc.

An evaluation may be implemented in one of several ways. A _classifier_ [LLM](#large-language-model) or another kind of model might be used to score content. A [Dataset](#dataset) of examples is commonly used. For our purposes, an implementation is API compatible for execution within an [Evaluation Framework](#evaluation-framework). 

See also [Evaluation Framework](#evaluation-framework).

## Evaluation Framework

An umbrella term for the software tools, runtime services, benchmark systems, etc. used to perform [Evaluations](#evaluation) by running their implementations to measure [AI systems](#ai-system) for trust and safety risks and mitigations, and other concerns.

## Fairness

Does the [AI system's](#ai-system) responses exhibit social biases, preferential treatment, or other forms of non-objectivity?

## Feature

For our purposes, a small bit of functionality provided by an application. It is the increment of change in a single cycle of the [Test-Driven Development](#test-driven-development) process, which could be enhancing some user-visible functionality or adding new functionality in small increments.

## Function

In most languages, the most fundamental unit of abstraction and execution. Depending on the language, the term _function_ or _method_ might be used, where the latter are special functions associated with [Classes](#class) in [OOP](#object-oriented-programming) languages. Some languages allow code blocks outside of functions, perhaps inside alternative [Component](#component) boundaries, but this is not important for our purposes. 

Many functions are free of [Side Effects](#side-effect), meaning they don't read or write [State](#state) external to the function and shared by other functions. These functions are _always_ [Deterministic](#determinism); for a given input(s) they always return the same output. This is a very valuable property for design, testing, and reuse.

Other functions that read and possibly write external state are nondeterministic. So are functions that are implemented with [Concurrency](#concurrency) in a way that the order of results is not deterministic. For example, functions that retrieve data, like a database record, functions to generate UUIDs, functions that call other processes or systems.

## Functional Programming

FP is a design methodology that attempts to formalize the properties of [Functions](#function) and their properties, inspired by the behavior of mathematical functions. _State_ is maintained in a small set of abstractions, like _Maps_, _Lists_, and _Sets_, with operations that are implemented separately following protocol abstractions exposed by the collections. Like mathematical objects and unlike objects in [Object-Oriented Programming](#object-oriented-programming), mutation of [State](#state) is prohibited; any operation, like adding elements to a collection, creates a new, [Immutable](#immutable) copy. 

FP became popular when concurrent software became more widespread in the 2000s, because the immutable objects lead to far fewer concurrency bugs. FP languages may have other [Component](#component) constructs for grouping of functions, e.g., into _libraries_.

Contrast with [Object-Oriented Programming](#object-oriented-programming). Many programming languages combine aspects of FP and OOP.

## Generative AI Model

A combination of data and code, usually trained on a [Dataset](#dataset), to support [Inference](#inference) of some kind. 

For convenience, in the text, we use the shorthand term _model_ to refer to the generative AI [Component](#component) that has [Nondeterministic](#determinism) [Behavior](#behavior), whether it is a model invoked directly through an API in the same application or invoked by calling another service (e.g., ChatGPT). The goal of this project is to better understand how developers can test models.

See also [Large Language Model](#large-language-model) (LLMs) and [Multimodal Model](#multimodal-models).

## Hallucination

When a [Generative AI Model](#generative-ai-model) generates text that seems plausible, but is not factually accurate. Lying is not the right term, because there is no malice intended by the model, which only knows how to generate a sequence of [Tokens](#token) that are plausible, i.e., probabilistically likely.

## Immutable

A [Unit's](#unit) [State](#state) cannot be modified, once it has been initialized. If _all_ units in a [Component](#component) are immutable, then the component itself is considered immutable. Contrast with [Mutable](#mutable). See also [State](#state).

## Inference

Sending information to a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system) to have it return an analysis of some kind, summarization of the input, or newly generated information, such as text. The term _query_ is typically used when working with [LLMs](#large-language-model). The term _inference_ comes from traditional statistical analysis, including model building, that is used to _infer_ information from data.

## Integration Test

A test for several [Units](#unit) working together that verifies they interoperate properly. These "units" could be distributed systems, too. When any of the units that are part of the test have [Side Effects](#side-effects) _and_ the purpose of the test is not explore handling of such side effects, all units with side effects must be replaced with [Test Doubles](#test-double) to make the test [Deterministic](#determinism). 

See also [Test](#test), [Unit Test](#unit-test), and [Acceptance Test](#acceptance-test).

## Large Language Model

Abbreviated _LLM_, a state of the art [Generative AI Model](#generative-ai-model), often with billions of parameters, that has the ability to summarize, classify, and even generate text in one or more spoken and programming languages. See also [Multimodal Model](#multimodal-model).

## Model Context Protocol

Abbreviated MCP, a de-facto standard for communications between models, agents, and other tools. See [_modelcontextprotocol.io_](https://modelcontextprotocol.io/introduction){:target="_blank"} for more information.

## Object-Oriented Programming

OOP (or OOSD - object-oriented software development) is a design methodology that creates software [Components](#component) with boundaries that mimic real-world objects (like _Person_, _Automobile_, _Shopping Cart_, etc.). Each object encapsulates [State](#state) and [Behavior](#behavior) behind its abstraction.

Introduced in the Simula language in the 1960s, it gained widespread interest in the 1980s with the emergence of graphical user interfaces (GUIs), where objects like _Window_, _Buttons_, and _Menus_ were an intuitive way to organize such software.

Contrast with [Functional Programming](#functional-programming). Many programming languages combine elements of FP and OOP.

## Multimodal Model

[Generative AI Models](#generative-ai-model) that usually extend the text-based capabilities of [LLMs](#large-language-model) with additional support for other media, such as video, audio, still images, or other kinds of data.

## Mutable

A [Unit's](#unit) [State](#state) can be modified during execution, either through direct manipulation by another unit or indirectly by invoking the unit (e.g., calling a [Function](#function) that changes the state. If any _one_ unit in a [Component](#component) is mutable, then the component itself is considered mutable. Contrast with [Immutable](#immutable). See also [State](#state).

## Paradigm

From the [_Merriam-Webster Dictionary_]({{site.baseurl}}/references/#merriam-webster-dictionary) definition of [_paradigm_](https://www.merriam-webster.com/dictionary/paradigm){:target="dict"}: &ldquo;a philosophical and theoretical framework of a scientific school or discipline within which theories, laws, and generalizations and the experiments performed in support of them are formulated.&rdquo;

## Predictable

In the context of software, the quality that knowing a [Unit's](#unit) history of past [Behavior](#behavior) and its design, you can predict its future behavior reliably. See also [State Machine](#state-machine).

## Probability and Statistics

Two interrelated branches of mathematics, where statistics concerns such tasks as collecting, analyzing, and interpreting data, while probability concerns events, in particular the percentage likelihood that certain values will be measured when events occur. 

Both disciplines emerged together to solve practical problems in science, industry, sociology, etc. It is common for researchers to build a _model_ of the system being studied, in part to compare actual results with model predictions, confirming or rejecting the underlying theories about the system upon which the model was built. Also, if the model is accurate, it provides predictive capabilities for possible and likely future events.

Contrast with [Determinism](#determinism).

## Prompt

The query a user (or another system) sends to an [LLM](#large-language-model). Often, additional [Context](#context) information is added by an [AI System](#ai-system) before sending the prompt to the LLM.

## Refactoring

Modifying code to change its structure as required to support a new feature. _No [Behavior](#behavior) changes are introduced_, so that the existing automated [Tests](#test) can verify that no regressions are introduced as the code is modified. This is first step in the [Test-Driven Development](#test-driven-development) cycle.

## Regression

When an unexpected [Behavior](#behavior) change is introduced into a previously-working [Unit](#unit), because of a change made to the code base, often in other units for unrelated functionality.

Automated [Tests](#test) are designed to catch regressions as soon as they occur, making it easier to diagnose the change that caused the regression, as well as detecting the regression in the first place.

## Repeatable

If an action, like running a test, is run repeatedly with no code or data changes, does it return the same results every time? By design, [Generative AI Models](#generative-ai-model) are _expected_ to return different results each time a query is repeated.

## Response

The generic term for outputs from a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system). Sometimes _results_ is also used.

## Robustness

How well does the [AI System](#ai-system) continue to perform within acceptable limits or degrade &ldquo;gracefully&rdquo; when stressed in some way? For example, how well does a [Generative AI Model](#generative-ai-model) respond to prompts that deviate from its training data?

## Sequential

The steps of some work are performed in a predictable, repeatable order. This property is one of the requirements for [Deterministic](#determinism) [Behavior](#behavior). Contrast with [Concurrent](#concurrent).

## Side Effect

Reading and/or writing [State](#state) shared outside a [Unit](#unit), i.e., a [Function](#function) with other functions. See also [Determinism](#determinism).

## State

Used in software to refer to a set of values in some context, like a [Component](#component). The values determine how the component will behave in subsequent invocations to perform some work. The values can sometimes be read directly by other components. If the component is [Mutable](#mutable), then the state can be changed by other components either directly or through invocations of the component that cause state transitions to occur. (For example, popping the top element of a stack changes the contents of the stack, the number of elements it currently holds, etc.) 

Often, these _state transitions_ are modeled with a [State Machine](#state-machine), which constrains the allowed transitions.

## State Machine

A formal model of how the [State](#state) of a component can transition from one value (or set of values) to another. As an example, the TCP protocol [has a well-defined state machine](https://www.ietf.org/rfc/rfc9293.html#name-state-machine-overview){:target="tcp"}.

## System Prompt

A commonly-used, statically-coded part of the [Context](#context) information added by an [AI System](#ai-system) the [Prompt](#prompt) before sending it to the [LLM](#large-language-model). System prompts are typically used to provide the model with overall guidance about the application's purpose and how the LLM should respond. For example, it might include phrases like &ldquo;You are a helpful software development assistant.&rdquo;

## Test

For our purposes, a [Unit Test](#unit-test), [Integration Test](#integration-test), or [Acceptance Test](#acceptance-test).

## Test Double

A test-only replacement for a [Unit](#unit), usually because it has [Side Effects](#side-effect), so its [Behavior](#behavior) is [Deterministic](#determinism) for the purposes of testing a dependent unit that uses it. For example, a function that queries a database can be replaced with a version that always returns a fixed value expected by the test. A _mock_ is a popular kind of test double that uses the underlying runtime environment (e.g., the Python interpreter, the Java Virtual Machine - JVM) to intercept invocations of a unit and programmatically behave as desired by the tester.

See also [Test](#test), [Unit Test](#unit-test), [Integration Test](#integration-test), and [Acceptance Test](#acceptance-test).

## Test-Driven Development

When adding a [Feature](#feature) to a code base using _TDD_, the tests are written _before_ the code is written. A three step &ldquo;virtuous&rdquo; cycle is used, where changes are made _incrementally_ and _iterative_ using small steps, one at a time:

1. [Refactor](#refactoring) the code to change its structure as required to support the new feature, using the existing automated [Tests](#test) to verify that no regressions are introduced. For example, it might be necessary to introduce an abstraction to support two &ldquo;choices&rdquo; where previously only one choice existed.
2. Write a [Test](#test) for the new feature. This is _primarily_ a _design_ exercise, because thinking about testing makes you think about usability, [Behavior](#behavior), etc., even though you are also creating a reusable test that will become part of the [Regression](#regression) test suite. Note that the test suite will fail to run at the moment, because the code doesn't yet exist to make it pass!
3. Write the new feature to make the new test (as well as all previously written tests) pass.

The [Wikipedia TDD](https://en.wikipedia.org/wiki/Test-driven_development){:target="tdd"} article is a good place to start for more information.

## Token

For language [Generative AI Models](#generative-ai-model), the training texts and query prompts are split into tokens, usually whole words or fractions according to a vocabulary of tens of thousands of tokens that can include common single characters, several characters, and &ldquo;control&rdquo; tokens (like &ldquo;end of input&rdquo;). The rule of thumb is a corpus will have roughly 1.5 times the number of tokens as it will have words.

## Training

In our context, training is the processes used to teach a model, such as a [Generative AI Models](#generative-ai-model) how to do its intended job. 

In the generative AI case, we often speak of _pretraining_, the training process that uses a massive data corpus to teach the model facts about the world, how to speak and understand human language, and do some skills. However, the resulting model often does poorly on specialized tasks and even basic skills like following a user's instructions, conforming to social norms (e.g., avoiding hate speech), etc. 

That's where a second [Tuning](#tuning) phase comes in, a suite of processes used to improve the models performance on many general or specific skills.

## Tuning

Tuning refers to one or more processes used to transform a [Pretrained](#training) model into one that exhibits much better desired [Behaviors](#behavior) (like instruction following) or specialized domain knowledge.

## Unit

For our purposes, the _unit_ in the context of a [Unit Test](#unit-test). Usually, this is a single [Function](#function) that is being designed and written, but this may be happening in the larger context of a _class_ in an [Object-Oriented Programming](#object-oriented-programming) language or some other self-contained [Component](#Component). We will use _unit_ as an umbrella term in many discussions, unless it is important to make finer distinctions.

## Unit Test

A test for a [Unit](#unit) that exercises its [Behavior](#behavior) in isolation from all other [Functions](#function) and [State](#state). When the unit being tested has [Side Effects](#side-effects), because of other units it invokes, all such side effects must be replaced with [Test Doubles](#test-double) to make the test [Deterministic](determinism). Note that writing a unit test as part of [Test-Driven Development](#test-driven-development) inevitably begins with a [Refactoring](#refactoring) step to modify the code, while preserving the current behavior, so that it is better positioned to support implementing the new functionality.

See also [Test](#test), [Integration Test](#integration-test), and [Acceptance Test](#acceptance-test).
