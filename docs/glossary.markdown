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

## Acceptance Benchmark

The analog of [Acceptance Tests](#acceptance-test) for an AI-enabled system that has [Stochastic](#stochastic) behaviors. [Benchmark](#benchmark) technology is adapted for the purpose. 

See also [Unit Test](#unit-test), [Unit Benchmark](#unit-benchmark), [Integration Test](#integration-test), [Integration Benchmark](#integration-benchmark), and [Acceptance Test](#acceptance-test).

## Acceptance Test

A test that verifies a user-visible feature works are required, often by driving the user interface or calling the external API. These tests are system-wide and end-to-end. They are sometimes executed manually, if automation isn't feasible.

However, it is desirable to make them automated, in which case all operations with [Side Effects](#side-effects) need to be replaced with [Deterministic](#determinism) [Test Doubles](#test-double). 

See also [Test](#test), [Unit Test](#unit-test), [Unit Benchmark](#unit-benchmark), [Integration Test](#integration-test), [Integration Benchmark](#integration-benchmark), [Acceptance Test](#acceptance-test), and [Acceptance Benchmark](#acceptance-benchmark).

## Adaptation

A general term used by [Nathan Lambert]({{site.baseurl}}/references/#nathan-lambert) for the addition [Tuning](#tuning) performed on a [Trained](#trained) [Generative AI Model](#generative-ai-model) to improve its [Alignment](#alignment) for user goals, like better domain-specific awareness, instruction following, and awareness of social norms, etc.

## Agent

An old concept in AI, but now experiencing a renaissance as the most flexible architecture pattern for AI-based applications. Agents are orchestrations of [Generative AI Model](#generative-ai-model) and external service invocations, e.g., planners, schedulers, reasoning engines, data sources (weather, search, ...), etc. In this architecture, the best capabilities of each service and model are leveraged, rather than assuming that models can do everything successfully themselves. Agent-based applications sometimes use multiple models, one per agent, where each one provides some specific capabilities. For example, one model might be process user prompts into back-end API invocations, including to other models, and interpret the results into user-friendly responses.

## AI Actor

[\[2\]](#nist) An organization or individual building an [AI System](#ai-system).

## AI System

Umbrella term for an application or system with AI [Components](#component), including [Data Sets](#data-set), [Generative AI Models](#generative-ai-model) (e.g., [LLMs](#large-language-model), [Evaluation Frameworks](#evaluation-framework) and [Evaluations](#evaluations) for safety detection and mitigation, etc., plus external services, databases for runtime queries, and other application logic that together provide functionality.

## Alignment

A general term for how well an [AI System's](#ai-system) outputs (e.g., replies to queries) and [Behaviors](#behavior) correspond to end-user and service provider objectives, including the quality and utility of results, as well as safety requirements. Quality implies factual correctness and utility implies the results are fit for purpose, e.g., a Q&A system should answer user questions concisely and directly, a Python code-generation system should output valid, bug-free, and secure Python code. [EleutherAI]({{site.baseurl}}/references/#eleuther-ai){:target="eleuther"} defines alignment [this way](https://www.eleuther.ai/alignment){:target="eleuther"}, &ldquo;Ensuring that an artificial intelligence system behaves in a manner that is consistent with human values and goals.&rdquo; See also the work of the [Alignment Forum]({{site.baseurl}}/references/#alignment-forum).

## Automatable

Can an action, like a test, be automated so it can be executed without human intervention?

## Behavior

What does a [Component](#component) do, either autonomously on its own (e.g., a security monitoring tool that is constantly running) or when invoked by another component through an API or [Function](#function) call? This is a general-purpose term that could cover a single [Feature](#feature), a whole [Use Case](#use-case) or anything in between.

## Behavior-Driven Development

Behavior-Driven Development (BDD) is an evolution of [TDD](#test-driven-development) where the testing APIs more explicitly express the language of specifying behaviors. Hence, writing tests in a BDD style means creating _executable specifications_. 

Popular examples include [RSpec](https://rspec.info/){:target="_blank"} for the Ruby language community and several BDD-inspired dialects supported by [ScalaTest](https://www.scalatest.org/user_guide/selecting_a_style){:target="_blank"} for Scala. While useful for thinking through requirements, there was a tendency for these APIs to be verbose to use, so practitioners often combined these APIs with more concise testing APIs. See also [Test-Driven Development](#test-driven-development), [Specification-Driven Development](#specification-driven-development), [Property-Based testing](#property-based-testing), and [Design by Contract](#design-by-contract).

## Benchmark

[\[1\]](#mlc) A methodology or [Function](#function) used for offline [Evaluation](#evaluation) of a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system) for a particular purpose and to interpret the results. It consists of:
* A set of tests with metrics.
* A summarization of the results.

See also [Unit Benchmark](#unit-benchmark), [Integration Benchmark](#integration-benchmark), and [Acceptance Benchmark](#acceptance-benchmark).

## Class

The primary [Component](#component) abstraction in [Object-Oriented Programming](#object-oriented-programming), although not necessarily the only one.

## Coding Agent

An AI-powered IDE or tool specifically designed for AI-assisted software development. Here is a partial list of _coding agents_:

* [AWS Kiro](https://kiro.dev/){:target="_blank"} (an AI IDE designed to support [Specification-Driven Development](#specification-driven-development))
* [Gemini CLI](https://github.com/google-gemini/gemini-cli){:target="_blank"}
* [Claude Code](https://www.anthropic.com/claude-code){:target="_blank"}
* [Cline](https://cline.bot/){:target="_blank"}
* [Cursor](https://cursor.com/){:target="_blank"}
* [GitHub Copilot](https://code.visualstudio.com/){:target="_blank"}
* [Roo Code](https://roocode.com/){:target="_blank"}
* [Windsurf](https://windsurf.com/){:target="_blank"}

## Component

An ill-defined, but often-used term in software. In this case, we use it to generically refer to any piece of software with a well-defined purpose, an access API that defines clear boundaries. Depending on the programming language, it may group together [Functions](#function), [Classes](#class), etc. Particular programming languages and &ldquo;paradigms&rdquo; (like [OOP](#object-oriented-programming) and [FP](#functional-programming)) might use terms like _packages_, _modules_, _subsystems_, _libraries_, and even _web services_ can be considered components.

In principal, a component could contain a single [Unit](#unit). So, for simplicity in the rest of the text, we will use [Component](#Component) as an umbrella term that could also mean an individual [Unit](#unit), unless it is important to make finer distinctions.

## Concurrent

When work can be partitioned into smaller steps that can be executed in any order and the runtime executes them in a nonpredictable order. If the order is predictable, no matter how it executed, we can say it is effectively [Sequential](#sequential).

## Context

Additional information passed to an [LLM](#large-language-model) as part of a user [Prompt](#prompt), which is intended to provide additional, useful _context_ information so that the [Response](#response) is better than if the user's prompt was passed to the LLM alone. This additional content may include a [System Prompt](#system-prompt), relevant documents retrieved using [RAG](#retrieval-augmented-generation), etc.

## Cohesion

Does a [Component](#component) feel like &ldquo;one thing&rdquo; with a single purpose, exhibiting well-defined [Behaviors](#behavior) with a coherent [State](#state)? Or does it feel like a miscellaneous collection of behaviors or state?

## Coupling

How closely connected is one [Component](#component) to others in the system? &ldquo;Loose&rdquo; coupling is preferred, because it makes it easier to test components in isolation, substitute replacements when needed, etc. Strongly coupled components often indicate poor abstraction boundaries between them.

## Design by Contract

[Design by Contract](https://en.wikipedia.org/wiki/Design_by_contract){:target="_wikipedia"} (&ldquo;DbC&rdquo;) is an idea developed by [Bertrand Meyer](https://en.wikipedia.org/wiki/Bertrand_Meyer){:target="_wikipedia"} and incorporated into his [Eiffel](https://en.wikipedia.org/wiki/Eiffel_(programming_language)){:target="_wikipedia"} programming language. In Eiffel all functions can define a _contract_ for allowed inputs, invariants, and guaranteed responses, if the input requirements are met. The runtime system would handle any failures of these contracts. A _core principle_ of DbC use is that contract failures should terminate the application immediately, forcing the developers to fix the issue. Failure to do so becomes an excuse to let bugs accumulate. If this principle was rigorously followed during development, it is often considered acceptable (or at least &ldquo;expedient&rdquo;), to log contract failures, but not terminate execution in production runs. DbC can be used in other languages through built-in features (like _assertions_), libraries, or various runtime features.

DbC provides many of the same design benefits provided by [TDD](#test-driven-development), which emerged later, such as directing attention to more rigorous API design. Because of the additional benefits of TDD, DbC has largely fallen out of practice, but it's formalism for what constitutes good contracts is still highly valuable and recommended for study. 

## Data Set

(See also [\[1\]](#mlc)) A collection of data items used for training, evaluation, etc. Usually, a given data set has a schema (which may be “this is unstructured text”) and some metadata about provenance, licenses for use, transformations and filters applied, etc.

## Determinism

The output of a [Component](#component) for a given input is always known precisely. This affords writing repeatable, predictable software and automated, reliable tests.

In contrast, _nondeterminism_ means identical inputs yield different results, removing [Repeatability](#Repeatable) and complicating [Predictability](#predictable), and the ability to write automated, reliable tests.

## Explainability

Can humans understand why the system behaves the way that it does in a particular [Use Case](#use-case)? Can the system provide additional information about about why it produced a particular output?

## Evaluation

Much like other software, models and AI systems need to be trusted and useful to their users. Evaluation aims to provide the evidence needed to gain users’ confidence for an [AI System](#ai-system).

An particular evaluation is the capability of measuring and quantifying how a [Generative AI Model](#generative-ai-model), e.g., an [LLM](#large-language-model), or an [AI System](#ai-system) as a whole handles [Prompts](#prompt) and the kinds of [Responses](#response) produced. For example, an evaluation might be used to see if hate speech is detected in prompts and responses, if responses contain hallucinations, measure the overhead (time and compute) for processing, and for our purposes, implements a required [Use Case]({{site.glossaryurl}}/#use-case){:target="_glossary"}, etc.

An evaluation may be implemented in one of several ways. A _classifier_ [LLM](#large-language-model) or another kind of model might be used to score content. A [Data Set](#data-set) of examples is commonly used. For our purposes, an implementation is API compatible for execution within an [Evaluation Framework](#evaluation-framework). 

See also [Evaluation Framework](#evaluation-framework).

## Evaluation Framework

An umbrella term for the software tools, runtime services, benchmark systems, etc. used to perform [Evaluations](#evaluation) by running their implementations to measure [AI systems](#ai-system) for trust and safety risks and mitigations, and other concerns.

## Fairness

Does the [AI system's](#ai-system) responses exhibit social biases, preferential treatment, or other forms of non-objectivity?

## Feature

For our purposes, a small bit of functionality provided by an application. It is the increment of change in a single cycle of the [Test-Driven Development](#test-driven-development) process, which could be enhancing some user-visible functionality or adding new functionality in small increments. See also [Use Case](#use-case)

## Fine Tuning

A more specific term for [Tuning](#tuning), a part of [Post-training](#post-training), that emphasizes that after the major learning has happened during [Pre-training](#pre-training), the model behavior is refined and improved with additional training techniques.

## Function

In most languages, the most fundamental [Unit](#unit) of abstraction and execution. Depending on the language, the term _function_ or _method_ might be used, where the latter are special functions associated with [Classes](#class) in [OOP](#object-oriented-programming) languages. Some languages allow code blocks outside of functions, perhaps inside alternative [Component](#component) boundaries, but this is not important for our purposes. 

Many functions are free of [Side Effects](#side-effect), meaning they don't read or write [State](#state) external to the function and shared by other functions. These functions are _always_ [Deterministic](#determinism); for a given input(s) they always return the same output. This is a very valuable property for design, testing, and reuse.

Other functions that read and possibly write external state are nondeterministic. So are functions that are implemented with [Concurrency](#concurrency) in a way that the order of results is not deterministic. For example, functions that retrieve data, like a database record, functions to generate UUIDs, functions that call other processes or systems.

## Functional Programming

FP is a design methodology that attempts to formalize the properties of [Functions](#function) and their properties, inspired by the behavior of mathematical functions. _State_ is maintained in a small set of abstractions, like _Maps_, _Lists_, and _Sets_, with operations that are implemented separately following protocol abstractions exposed by the collections. Like mathematical objects and unlike objects in [Object-Oriented Programming](#object-oriented-programming), mutation of [State](#state) is prohibited; any operation, like adding elements to a collection, creates a new, [Immutable](#immutable) copy. 

FP became popular when concurrent software became more widespread in the 2000s, because the immutable objects lead to far fewer concurrency bugs. FP languages may have other [Component](#component) constructs for grouping of functions, e.g., into _libraries_.

Contrast with [Object-Oriented Programming](#object-oriented-programming). Many programming languages combine aspects of FP and OOP.

## Generative Adversarial Networks

A GAN uses two neural networks that compete with each other in a &ldquo;zero-sum&rdquo; game, where one agent's gain is another agent's loss.

Quoting from the [Wikipedia page on GANs](https://en.wikipedia.org/wiki/Generative_adversarial_network){:target="_wikipedia"}:

{: .attention}

> Given a training data set, this technique learns to generate new data with the same statistics as the training set. For example, a GAN trained on photographs can generate new photographs that look at least superficially authentic to human observers, having many realistic characteristics...
>
> The core idea of a GAN is based on the "indirect" training through the discriminator, another neural network that can tell how "realistic" the input seems, which itself is also being updated dynamically. This means that the generator is not trained to minimize the distance to a specific image, but rather to fool the discriminator. This enables the model to learn in an unsupervised manner.

The &ldquo;adversarial&rdquo; part is how the generator attempts to _fool_ the discriminator, which learns to detect these situations.

## Generative AI Model

A combination of data and code, usually trained on a [Data Set](#data-set), to support [Inference](#inference) of some kind. 

For convenience, in the text, we use the shorthand term _model_ to refer to the generative AI [Component](#component) that has [Nondeterministic](#determinism) [Behavior](#behavior), whether it is a model invoked directly through an API in the same application or invoked by calling another service (e.g., ChatGPT). The goal of this project is to better understand how developers can test models.

See also [Large Language Model](#large-language-model) (LLMs) and [Multimodal Model](#multimodal-models).

## Hallucination

When a [Generative AI Model](#generative-ai-model) generates text that seems plausible, but is not factually accurate. Lying is not the right term, because there is no malice intended by the model, which only knows how to generate a sequence of [Tokens](#token) that are plausible. Which token is actually returned in a given context is a [Stochastic](#stochastic) process, i.e., a random process governed by a [Probability](#probability-and-statistics) distributions.

## Immutable

A [Unit's](#unit) or [Component's](#component) [State](#state) cannot be modified, once it has been initialized. If _all_ units in a [Component](#component) are immutable, then the component itself is considered immutable. Contrast with [Mutable](#mutable). See also [State](#state).

## Inference

Sending information to a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system) to have it return an analysis of some kind, summarization of the input, or newly generated information, such as text. The term _query_ is typically used when working with [LLMs](#large-language-model). The term _inference_ comes from traditional statistical analysis, including model building, that is used to _infer_ information from data.

## Instruction Fine Tuning

Often abbreviated _IFT_. A form of [Supervised Fine Tuning](#supervised-fine-tuning) that uses a [Labeled Data](#labeled-data) set of instruction prompts and responses. It is designed to improve model performance for specific tasks and for following instructions in general. See also [Tuning](#tuning).

## Integration Benchmark

The analog of [Integration Tests](#integration-test) for several [Units](#unit) and [Components](#component) working together, where some of them are AI-enabled and exhibit [Stochastic](#stochastic) behaviors. [Benchmark](#benchmark) technology is adapted for the purpose. 

See also [Unit Test](#unit-test), [Unit Benchmark](#unit-benchmark), [Integration Test](#integration-test), [Acceptance Test](#acceptance-test), and [Acceptance Benchmark](#acceptance-benchmark).

## Integration Test

A test for several [Units](#unit) and [Components](#component) working together that verifies they interoperate properly. These components could be distributed systems, too. When any of the units that are part of the test have [Side Effects](#side-effects) _and_ the purpose of the test is not to explore handling of such side effects, all units with side effects should be replaced with [Test Doubles](#test-double) to make the test [Deterministic](#determinism). 

See also [Test](#test), [Unit Test](#unit-test), [Unit Benchmark](#unit-benchmark), [Integration Benchmark](#integration-benchmark), [Acceptance Test](#acceptance-test), and [Acceptance Benchmark](#acceptance-benchmark)..

## Labeled Data

Labeled data contains content used to train a model and corresponding _labels_ of expected outcomes. A classic example is a labeled data set for [Training](#training) a SPAM filter, where example emails are labeled SPAM or not SPAM. In contrast, [Unlabeled Data](#unlabeled-data) contains no such labels. Labeled data is used in model [Tuning](#tuning), while sets of unlabeled data are used for training raw [Generative AI Models](#generative-aI-models). 

In the context of [Generative AI Models](#generative-aI-models), there are several popular formats for labeled data:

* **Question and answer (Q&A) pairs:** A prompt, such as a question or an instruction to do something, is accompanied by an answer to the question or an expected response to the instruction.
* **Preference data:** Similar to Q&A pairs, but in addition to the _preferred_ or _chosen_ answer, a _rejected_ answer is provided, which supports teaching about responses that are good as well as bad.

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

In the context of software, the quality that knowing a [Unit's](#unit) or [Components](#component) history of past [Behavior](#behavior) and its design, you can predict its future behavior reliably. See also [State Machine](#state-machine).

## Pre-training

See [Training](#training). A more precise term in the context of [Generative AI Model](#generative-ai-model) training, where pre-training uses massive datasets to teach models from scratch, followed by a [Post-training](#post-training) ([Tuning](#tuning)) process to refine the behaviors as needed.

## Post-training

See [Tuning](#tuning). A more precise term in the context of [Generative AI Model](#generative-ai-model) training, where [Pre-training](#pre-training) uses massive datasets to teach models from scratch, followed by a ost training (tuning) process to refine the behaviors as needed.

## Probability and Statistics

Two interrelated branches of mathematics, where statistics concerns such tasks as collecting, analyzing, and interpreting data, while probability concerns observations, in particular the percentage likelihood that certain values will be measured when observations are made of a _random_ process, or more precisely, a _random probability distribution_, like heads or tails when flipping a coin. This probability distribution is the simplest possible; there is a 50-50 chance of heads or tails (assuming a _fair coin_). The probability distribution for rolling a particular sum with a pair of dice is less simple, but straightforward. The probability distribution for the heights of women in the United States is more complicated, where historical data determines the distribution, not a simple formula.

Both disciplines emerged together to solve practical problems in science, industry, sociology, etc. It is common for researchers to build a mathematical _model_ (in the general sense of the word, not just an AI model) of the system being studied, in part to compare actual results with predictions from the model, confirming or rejecting the underlying theories about the system upon which the model was built. Also, if the model is accurate, it provides predictive capabilities for possible and likely future observations.

Contrast with [Determinism](#determinism). See also [Stochastic](#stochastic).

## Prompt

The query a user (or another system) sends to an [LLM](#large-language-model). Often, additional [Context](#context) information is added by an [AI System](#ai-system) before sending the prompt to the LLM. See also [Prompt Engineering](#prompt-engineering).

## Prompt Engineering

A term for the careful construction of good [Prompts](#prompt) to maximize the quality of [Inference](#inference) responses. It is really considered more _art_ than _science_ or _engineering_ because of the subjective relationship between prompts and responses for [Generative AI Models](#generative-ai-model).

## Property-Based Testing

Property-Based Testing (PBT) is sometimes also called _property-based development_ or _property-driven development_. This variation of [Test-Driven Development](#test-driven-development) emphasizes the mathematical properties of [Units](#unit) being tested. Obvious examples are arithmetic functions on integers, but properties and the &ldquo;laws&rdquo; they impose can be much more general. For example, all programming languages support concatenation (e.g., &ldquo;addition&rdquo;) of strings, where an empty string is the &ldquo;zero&rdquo;. Hence, `length("foo") == length("foo" + "") == 3`. Sting addition is associative, `(a+b)+c == a+(b+c)`, but not commutative, `a+b ≠ b+a`.

All libraries that support PBT let you define the properties that must hold and a way of defining allowed values of the &ldquo;types&rdquo; in question. At test time, the library generates a large set of representative instances of the types and verifies the properties hold for all instances.

Property-based testing emerged in the [Functional Programming](#functional-programming) community.

See also [Design by Contract](#design-by-contract), [Specification-Driven Development](#specification-driven-development), [Behavior-Driven Development](#behavior-driven-development), and [Test-Driven Development](#test-driven-development).

## Refactoring

Modifying code to change its structure as required to support a new feature. _No [Behavior](#behavior) changes are introduced_, so that the existing automated [Tests](#test) can verify that no regressions are introduced as the code is modified. This is first step in the [Test-Driven Development](#test-driven-development) cycle.

## Regression

When an unexpected [Behavior](#behavior) change is introduced into a previously-working [Unit](#unit), because of a change made to the code base, often in other units for unrelated functionality.

Automated [Tests](#test) are designed to catch regressions as soon as they occur, making it easier to diagnose the change that caused the regression, as well as detecting the regression in the first place.

## Reinforcement Fine Tuning

TODO. 

See the discussion of [Reinforcement Fine Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/#reinforcement-fine-tuning) in [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/). 

## Reinforcement Learning

Reinforcement learning (RL) is a form of machine learning, often used for optimizing control or similar systems. In RL, an agent performs a loop where it observes the state of the &ldquo;world&rdquo; visible to it at the current time, it takes what it thinks is a suitable action for the next step, chosen to maximize a reward signal, often with the goal of maximizing the long-term reward, such as wining a game. The _reinforcement_ aspect is an update at each step that is done to a _policy_ of some kind that used by the agent to decide which actions in subsequent steps are most likely to produce maximize long-term, cummulative reward, given the current known state. However, when choosing the next step, the _best_ choice is not always made. Some degree of randomness is introduced so that the agent explores all possible states and rewards, rather than getting stuck always choosing the same actions that are known good, but may be less optimal than actions that have not yet been tried. 

Variations include having a dedicated _reward model_ that calculates the reward based on the chosen action. When RL is used for a game, for example, it might be obvious what the reward is for any action and state combination, i.e., did you land on square that reveals a &ldquo;boost&rdquo; of some kind. In contrast, reward determination like deciding if an LLM output is a good response to a prompt, etc. is not so simple. 

In the generative AI context, RL is a popular tool in the suite of model [Tuning](#tuning) processes that are used to improve model performance in various ways. In particular, [Reinforcement Learning with Human Feedback]({{site.glossaryurl}}/#reinforcement-learning-with-human-feedback){:target="_glossary"} (RLHF) is a popular technique for [Adaptation](#adaptation).

See also the discussion of [Reinforcement Fine Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/#reinforcement-fine-tuning) in [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/), which describes RL in more detail. 

## Reinforcement Learning with Human Feedback

A [Reinforcement Learning](#reinforcement-learning) introduced by OpenAI that uses human data to train a reward model, which is then used with RL to improve the training of the [Generative AI Model](#generative-ai-model). This is an expensive process, because of the expense of acquiring human generated, often expert, data. 

## Reinforcement Learning with Verifiable Rewards

A [Reinforcement Learning](#reinforcement-learning) approach for LLMs where the response from a model during an RL step can be verified externally. For example, does the generated code compile and pass existing unit tests? See [Awesome RLVR](https://github.com/opendilab/awesome-RLVR){:target="_blank"} for more details.

## Repeatable

If an action, like running a test, is run repeatedly with no code or data changes, does it return the same results every time? By design, [Generative AI Models](#generative-ai-model) are _expected_ to return different results each time a query is repeated.

## Retrieval-augmented Generation

RAG was one of the first AI-specific design patterns for applications. It uses one or more data stores with information relevant to an application's use cases. For example, a [ChatBot](#chatbot) for automotive repair technicians would use RAG to retrieve sections from repair manuals and logs from past service jobs, selecting the ones that are most relevant to a particular problem or subsystem the technician is working on. This [Context](#context) is passed as part of the [Prompt](#prompt) to the [LLM](#large-language-model). 

A key design challenge is determining relevancy and structuring the data so that relevant information is _usually_ retrieved. This is typically done by breaking the reference data into &ldquo;chunks&rdquo; and encoding each chunk in a vector representation, e.g., a _hash_, which functions as a _similarity metric_. During inference, the prompt is passed through the same encoding and the top few _nearest neighbors_, based on the metric, are returned for the context, thereby attempting to ensure maximum relevancy.

See [this IBM blog post](https://research.ibm.com/blog/retrieval-augmented-generation-RAG){:target="ibm-rag"} for a description of RAG.

## Response

The generic term for outputs from a [Generative AI Model](#generative-ai-model) or [AI System](#ai-system). Sometimes _results_ is also used.

## Robustness

How well does the [AI System](#ai-system) continue to perform within acceptable limits or degrade &ldquo;gracefully&rdquo; when stressed in some way? For example, how well does a [Generative AI Model](#generative-ai-model) respond to prompts that deviate from its training data?

## Scenario

One _path_ through a use case, such as one &ldquo;happy path&rdquo; from beginning to end where a user completes a task or accomplishes a goal. A failure scenario is a path through the use case where the user is unable to succeed, due to system or user errors.

**Note:** When the text doesn't link to this definition, it is because the word is being used generically or because the text already linked to this definition. Hopefully the context will be clear. 

## Sequential

The steps of some work are performed in a predictable, repeatable order. This property is one of the requirements for [Deterministic](#determinism) [Behavior](#behavior). Contrast with [Concurrent](#concurrent).

## Side Effect

Reading and/or writing [State](#state) shared outside a [Unit](#unit), i.e., a [Function](#function) with other functions. See also [Determinism](#determinism). If a [Component](#component) contains unit that perform side effects, then the component itself is considered to perform side effects.

## Specification-Driven Development

Abbreviated _SDD_ and also known as _Spec-Driven Development_. In our context, this refers to [an idea introduced by GitHub and Microsoft]({{site.baseurl}}/references/#specification-driven-development), that we should structure code generation prompts in a more-precise format to ensure we get the code we need. The argument is that many models are already perfectly capable of generating this code, but they are &ldquo;literal minded&rdquo; and need to be told precisely what is needed from them.

We discuss SDD at length in the [Specification-Driven Development]({{site.baseurl}}/specification-driven-development) chapter. SDD is similar in its goals to [Test-Driven Development](#test-driven-development), although arguably closer to the emphasis in [Behavior-Driven Development](#behavior-driven-development).

## State

Used in software to refer to a set of values in some context, like a [Component](#component). The values determine how the component will behave in subsequent invocations to perform some work. The values can sometimes be read directly by other components. If the component is [Mutable](#mutable), then the state can be changed by other components either directly or through invocations of the component that cause state transitions to occur. (For example, popping the top element of a stack changes the contents of the stack, the number of elements it currently holds, etc.) 

Often, these _state transitions_ are modeled with a [State Machine](#state-machine), which constrains the allowed transitions.

## State Machine

A formal model of how the [State](#state) of a component can transition from one value (or set of values) to another. As an example, the TCP protocol [has a well-defined state machine](https://www.ietf.org/rfc/rfc9293.html#name-state-machine-overview){:target="tcp"}.

## Stochastic

The behavior of a system where observed values are governed by a random probability distribution. For example, when flipping a coin repeatedly, the observed values, heads or tails, are governed by a distribution that predicts 50% of the time heads will be observed and 50% of the time tails will be observed, assuming a _fair coin_ (not weighted on one side or the other). The value you observe for any given flip is random; you can't predict exactly which possibility will happen, only that there is an equal probability of heads or tails. After performing more and more flips, the total count of heads and tails should be very close to equal. See also [Probabilities and Statistics](#probabilities-and-statistics).

## Supervised Fine Tuning

Often abbreviated _SFT_. A more general term than [Instruction Fine Tuning](#instruction-fine-tuning), but often used synonymously. _Supervised_ is an old term in machine learning for any kind of training algorithm that uses [Labeled Data](#labeled-data), i.e., data that includes the expected answers. See also [Tuning](#tuning).

## System Prompt

A commonly-used, statically-coded part of the [Context](#context) information added by an [AI System](#ai-system) the [Prompt](#prompt) before sending it to the [LLM](#large-language-model). System prompts are typically used to provide the model with overall guidance about the application's purpose and how the LLM should respond. For example, it might include phrases like &ldquo;You are a helpful software development assistant.&rdquo;

## Teacher Model

A [Generative AI Model](#generative-ai-model) that can be used as part of a [Tuning](#tuning) (&ldquo;teach&rdquo;) process for other models, to generate synthetic data, to evaluate the quality of data, etc. These models are usually relatively large, sophisticated, and powerful, so they are very capable for these purposes, but they are often considered too costly to use as an application's runtime model, where smaller, lower-overhead models are necessary. However, for software development purposes, less frequent use of teacher models is worth the higher cost for the services they provide.

## Test

For our purposes, a [Unit Test](#unit-test), [Integration Test](#integration-test), or [Acceptance Test](#acceptance-test).

## Test Double

A test-only replacement for a [Unit](#unit) or a while [Component](#component), usually because it has [Side Effects](#side-effect) and we need the [Behavior](#behavior) to be [Deterministic](#determinism) for the purposes of testing a dependent unit that uses it. For example, a function that queries a database can be replaced with a version that always returns a fixed value expected by the test. A _mock_ is a popular kind of test double that uses the underlying runtime environment (e.g., the Python interpreter, the Java Virtual Machine - JVM) to intercept invocations of a unit and programmatically behave as desired by the tester.

See also [Test](#test), [Unit Test](#unit-test), [Integration Test](#integration-test), and [Acceptance Test](#acceptance-test).

## Test-Driven Development

When adding a [Feature](#feature) to a code base using _TDD_, the tests are written _before_ the code is written. A three step &ldquo;virtuous&rdquo; cycle is used, where changes are made _incrementally_ and _iterative_ using small steps, one at a time:

1. [Refactor](#refactoring) the code to change its structure as required to support the new feature, using the existing automated [Tests](#test) to verify that no regressions are introduced. For example, it might be necessary to introduce an abstraction to support two &ldquo;choices&rdquo; where previously only one choice existed.
2. Write a [Test](#test) for the new feature. This is _primarily_ a _design_ exercise, because thinking about testing makes you think about usability, [Behavior](#behavior), etc., even though you are also creating a reusable test that will become part of the [Regression](#regression) test suite. Note that the test suite will fail to run at the moment, because the code doesn't yet exist to make it pass!
3. Write the new feature to make the new test (as well as all previously written tests) pass.

TDD not only promotes iterative and incremental development, with a growing suite of tests resulting from the process, it effectively turns the writing of executable tests into a form of specification of the desired behavior, writing before the code is written to implement the specification. [Behavior-Driven Development](#behavior-driven-development) would take this idea to its logical conclusion, that tests are _executable specifications_. 

The [Wikipedia TDD](https://en.wikipedia.org/wiki/Test-driven_development){:target="_wikipedia"} article is a good place to start for more information.

See also [Design by Contract](#design-by-contract), [Specification-Driven Development](#specification-driven-development), [Behavior-Driven Development](#behavior-driven-development), and [Property-Based Testing](#property-based-testing).

## Token

For language [Generative AI Models](#generative-ai-model), the training texts and query prompts are split into tokens, usually whole words or fractions according to a vocabulary of tens of thousands of tokens that can include common single characters, several characters, and &ldquo;control&rdquo; tokens (like &ldquo;end of input&rdquo;). The rule of thumb is a corpus will have roughly 1.5 times the number of tokens as it will have words.

## Training

In our context, training is the processes used to teach a model, such as a [Generative AI Models](#generative-ai-model) how to do its intended job. A more precise term used in generative AI model development is _pre-training_, the training process that uses a massive data corpus to teach the model facts about the world, how to speak and understand human language, and do some skills. However, the resulting model uses does poorly on specialized tasks and even basic skills like following a user's instructions, conforming to social norms (e.g., avoiding hate speech), etc. 

That's where a second [Tuning](#tuning) (also sometimes called _post-training_) phase comes in, a suite of processes used to improve the models performance on many general or specific skills.

## Tuning

Tuning, or _post-training_, refers to one or more processes used to transform a [Pre-trained](#training) model into one that exhibits much better desired [Behaviors](#behavior) (like instruction following) or specialized domain knowledge. The term _fine tuning_ (sometimes spelled _finetuning_) is also widely used, e.g., for [Instruction Fine Tuning](#instruction-fine-tuning) and [Supervised Fine Tuning](#supervised-fine-tuning)

## Unit

For our purposes, the _unit_ in the context of a [Unit Test](#unit-test), the smallest granularity of functionality we care about. A unit can be a single [Function](#function) that is being designed and written, but this may be happening in the larger context of a [Component](#Component), such as a [Class](#class) in an [Object-Oriented Programming](#object-oriented-programming) language or some other self-contained. 

For simplicity, rather than say &ldquo;unit and/or component&rdquo; frequently in the text, we will often use just &ldquo;component&rdquo; as an umbrella term that could also mean either or both concepts, unless it is important to make finer distinctions.

## Unit Benchmark

An adaption of [Benchmark](#benchmark) tools and techniques for more fine-grained and targeted testing purposes, such as verifying [Features](#feature) and [Use Cases](#use-case) work as designed. See the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter for details. 

The same idea generalizes to the analogs of [Integration Tests](#integration-test), namely [Integration Benchmarks](#integration-benchmark), and [Acceptance Tests](#acceptance-test), namely [Acceptance Benchmarks](#acceptance-benchmark).

## Use Case

A common term for an end-to-end user activity done with a system, often broken down into several [Scenarios](#scenario) that describe different "paths" through the use case, including error scenarios, in addition to happy paths. Hence, scenarios would be the next level of granularity. Compare with [Features](#feature), which would be the capabilities implemented one at a time to support the scenarios that make up a use case.

## Unit Test

A test for a [Unit](#unit) that exercises its [Behavior](#behavior) in isolation from all other [Functions](#function) and [State](#state). When the unit being tested has [Side Effects](#side-effects), because of other units it invokes, all such side effects must be replaced with [Test Doubles](#test-double) to make the test [Deterministic](determinism). Note that writing a unit test as part of [Test-Driven Development](#test-driven-development) inevitably begins with a [Refactoring](#refactoring) step to modify the code, while preserving the current behavior, so that it is better positioned to support implementing the new functionality.

See also [Test](#test), [Unit Benchmark](#unit-benchmark), [Integration Test](#integration-test), [Integration Benchmark](#integration-benchmark), [Acceptance Test](#acceptance-test), [Acceptance Benchmark](#acceptance-benchmark).

## Unlabeled Data

Data without labels indicating expected &ldquo;information&rdquo; about the data, such as objects in images or themes in text examples. Massive sets of unlabeled data are used for [Training](#training) raw [Generative AI Models](#generative-ai-models), while [Labeled Data](#labeled-data) is typically used for [Tuning](#tuning) to improve those models to meet specific requirements.

## Vibe Coding

A term [coined by Andrej Karpathy](https://x.com/karpathy/status/1886192184808149383){:target="ak"} for just going with the code generated by an LLM, tweaking the prompt as needed to get the LLM to fix bugs and incorrect behavior. Hence, it's a completely &ldquo;non-engineered&rdquo; approach to coding, which can work well for quick coding needs, especially for non-programmers, but generally is not sufficient for longer-term projects. Hence, the term has a slightly negative connotation for many people, as in &ldquo;this is not a serious way to write software&rdquo;. Contrast with [Vibe Engineering](#vibe-engineering).

## Vibe Engineering

[Simon Willison's term](https://simonwillison.net/2025/Oct/7/vibe-engineering/){:target="sw-ve"}, made half in jest, for a more engineering-oriented approach to [Vibe Coding](#vibe-coding), which incorporates various engineering practices to ensure that quality and maintainability requirements can be met, longer term. As such, this blog post is a good counter argument to those who believe that AI coding assistants are now sufficiently reliable and powerful to completely take over from humans.

