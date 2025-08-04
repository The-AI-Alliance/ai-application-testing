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


<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Acceptance Test

A test that verifies a user-visible feature works are required, often by driving the user interface or calling the external API. These tests are system-wide and are sometimes executed manually. However, it is desirable to make them automated, in which case all operations with [_side effects_](#side-effects) need to be replaced with [_deterministic_](#determinism) [_test doubles_](#test-double). See also [_test_](#test), [_unit test_](#unit-test), and [_integration test_](#integration-test).

## Agent

An old concept in AI, but now experiencing a renaissance as the most flexible architecture pattern for AI-based applications. Agents are orchestrations of [_generative AI model_](#generative-ai-model) and external service invocations, e.g., planners, schedulers, reasoning engines, data sources (weather, search, ...), etc. In this architecture, the best capabilities of each service and model are leveraged, rather than assuming that models can do everything successfully themselves. Agent-based applications sometimes use multiple models, one per agent, where each one provides some specific capabilities. For example, one model might be process user prompts into back-end API invocations, including to other models, and interpret the results into user-friendly responses.

## AI Actor

[\[2\]](#nist) An organization or individual building an [_AI system_](#ai-system).

## AI System

Umbrella term for an application or system with AI components, including [_datasets_](#dataset), [_generative AI models_](#generative-ai-model), [_evaluation framework_](#evaluation-framework) and [_evaluators_](#evaluator) for safety detection and mitigation, etc., plus external services, databases for runtime queries, and other application logic that together provide functionality.

## Alignment

A general term for how well an [_AI system's_](#ai-system) outputs (e.g., replies to queries) and behaviors correspond to end-user and service provider objectives, including the quality and utility of results, as well as safety requirements. Quality implies factual correctness and utility implies the results are fit for purpose, e.g., a Q&A system should answer user questions concisely and directly, a Python code-generation system should output valid, bug-free, and secure Python code. [EleutherAI]({{site.baseurl}}/references/#eleuther-ai){:target="eleuther"} defines alignment [this way](https://www.eleuther.ai/alignment){:target="eleuther"}, &ldquo;Ensuring that an artificial intelligence system behaves in a manner that is consistent with human values and goals.&rdquo; See also the work of the [Alignment Forum]({{site.baseurl}}/references/#alignment-forum).

## Automatable

Can an action, like a test, be automated so it can be executed without human intervention?

## Benchmark

[\[1\]](#mlc) A methodology or function used for offline [_evaluation_](#evaluation) of a [_generative AI model_](#generative-ai-model) or [_AI system_](#ai-system) for a particular purpose and to interpret the results. It consists of:
* A set of tests with metrics.
* A summarization of the results.

## Component

An ill-defined, but often-used term in software. In this case, we use it to generically refer to anything with well-defined boundaries and access APIs: libraries, web services, etc.

## Dataset

(See also [\[1\]](#mlc)) A collection of data items used for training, evaluation, etc. Usually, a given dataset has a schema (which may be “this is unstructured text”) and some metadata about provenance, licenses for use, transformations and filters applied, etc.

## Determinism

The output of a [_function_](#function) for a given input is always known precisely. This affords writing repeatable, predictable software and automated, reliable tests.

In contrast, _nondeterminism_ means components for which identical inputs yield different results, removing repeatability and complicating predictability, and the ability to write automated, reliable tests.

## Explainability

Can humans understand why the system behaves the way that it does in a particular scenario? Can the system provide additional information about about why it produced a particular output?

## Evaluation

The capability of measuring and quantifying how a [_generative AI model_](#generative-ai-model) or [_AI system_](#ai-system) that uses models responds to inputs. Much like other software, models and AI systems need to be trusted and useful to their users. Evaluation aims to provide the evidence needed to gain users’ confidence. See also [_evaluation framework_](#evaluation-framework) and [_evaluator_](#evaluator).

## Evaluation Framework

An umbrella term for the software tools, runtime services, benchmark systems, etc. used to perform [_evaluations_](#evaluation) by running different [_evaluators_](#evaluator) to measure [_AI systems_](#ai-system) for trust and safety risks and mitigations, and other kinds of measurements.

## Evaluator

A classifier [_generative AI model_](#generative-ai-model) or similar tool, possibly including a [_dataset_](#dataset), that can quantify an [_AI system's_](#ai-system) inputs and outputs to detect the presence of risky content, such as hate speech, hallucinations, etc. For our purposes, an evaluator is API compatible for execution within an [_evaluation framework_](#evaluation-framework). In general, an evaluator could be targeted towards non-safety needs, such as measuring other aspects of [_alignment_](#alignment), [_inference_](#inference) model latency and throughput, carbon footprint, etc. Also, a given evaluator could be used at many points in the total AI life cycle, e.g., for a benchmark and an inference-time test.

## Fairness

Does the [_AI system's_](#ai-system) behaviors exhibit social biases, preferential treatment, or other forms of non-objectivity?

## Feature

For our purposes, a small bit of functionality provided by an application. It is the increment of change in a single cycle of the [_test-driven development_](#test-driven-development) process, which could be enhancing some user-visible functionality or adding new functionality in small increments.

## Function

Used here as an umbrella term for any unit of execution, including actual functions, methods, code blocks, etc. Many functions are free of [_side effects_](#side-effect), meaning they don't read or write state external to the function and shared by other functions. These functions are _always_ [_deterministic_](#determinism); for a given input(s) they always return the same output.

Other functions that read and possibly write external state or usually [_nondeterministic_](#determinism). For example, functions that retrieve data, like a database record, functions to generate UUIDs, functions that call other processes or systems.

## Functional Programming

FP is a design methodology that attempts to formalize the properties of components and their properties, inspired by constructs in mathematics. State is maintained in a small set of abstractions, like _Maps_, _Lists_, and _Sets_, with operations that are implemented separately following protocol abstractions exposed by the collections. Like mathematical objects and unlike objects in [_object-oriented programming_](#object-oriented-programming), mutation of state is prohibited; any operation, like adding elements to a collection, creates a new copy.

FP became popular when concurrent software became more widespread in the 2000s, because the immutable objects lead to far fewer concurrency bugs.

Contrast with [_object-oriented programming_](#object-oriented-programming). Many programming languages combine elements of FP and OOP.

## Generative AI Model

A combination of data and code, usually trained on a [_dataset_](#dataset), to support [_inference_](#inference) of some kind. See also [_large language model_](#large-language-model) and [_multimodal model_](#multimodal-models).

For convenience, in the text, we use the term _model_ to refer to the generative AI component that has [_nondeterministic_](#determinism) behavior, whether it is a model invoked directly through an API in the same application or invoked by calling another service (e.g., ChatGPT). The goal of this project is to better understand how developers can test _models_.

See also [_multimodal model_](#multimodal-model) and [_large language model_](#large-language-model) (LLMs)

## Hallucination

When a [_generative AI model_](#generative-ai-model) generates text that seems plausible, but is not factually accurate. Lying is not the right term, because there is no malice intended by the model, which only knows how to generate a sequence of [_tokens_](#token) that are plausible, i.e., probabilistically likely.

## Inference

Sending information to a [_generative AI model_](#generative-ai-model) or [_AI system_](#ai-system) to have it return an analysis of some kind, summarization of the input, or newly generated information, such as text. The term _query_ is typically used when working with [_LLMs_](#large-language-model). The term _inference_ comes from traditional statistical analysis, including model building, that is used to _infer_ information from data.

## Integration Test

A test for several [_functions_](#function) that verifies they interoperate properly. These "functions" could be other, distributed systems, too. When any of the functions being tested have [_side effects_](#side-effects), perhaps indirectly through other functions they call, all such side effects must be replaced with [_test doubles_](#test-double) to make the test [_deterministic_](#determinism). See also [_test_](#test), [_unit test_](#unit-test), and [_acceptance test_](#acceptance-test).

## Large Language Model

Abbreviated _LLM_, a state of the art [_generative AI model_](#generative-ai-model), often with billions of parameters, that has the ability to summarize, classify, and even generate text in one or more spoken and programming languages. See also [_multimodal model_](#multimodal-model).

## Model Context Protocol

A de-facto standard for communications between models, agents, and other tools. See [_modelcontextprotocol.io_](https://modelcontextprotocol.io/introduction){:target="_blank"} for more information.

## Object-Oriented Programming

OOP (or OOSD - object-oriented software development) is a design methodology that creates software components with boundaries that mimic real-world objects (like _Person_, _Automobile_, _Shopping Cart_, etc.). Each object encapsulates state and behavior behind its abstraction.

Introduced in the Simula language in the 1960s, it gained widespread interest in the 1980s with the emergence of graphical user interfaces (GUIs), where objects like _Window_, _Buttons_, and _Menus_ were an intuitive way to organize such software.

Contrast with [_functional Programming_](#functional-programming). Many programming languages combine elements of FP and OOP.

## Multimodal Model

[_generative AI models_](#generative-ai-model) that usually extend the text-based capabilities of [_LLMs_](#large-language-model) with additional support for other media, such as video, audio, still images, or other kinds of data.

## Paradigm

From the [_Merriam-Webster Dictionary_]({{site.baseurl}}/references/#merriam-webster-dictionary) definition of [_paradigm_](https://www.merriam-webster.com/dictionary/paradigm){:target="dict"}: &ldquo;a philosophical and theoretical framework of a scientific school or discipline within which theories, laws, and generalizations and the experiments performed in support of them are formulated.&rdquo;

## Probability and Statistics

Two interrelated branches of mathematics, where statistics concerns such tasks as collecting, analyzing, and interpreting data, while probability concerns events, in particular the percentage likelihood that certain values will be measured when events occur. 

Both disciplines emerged together to solve practical problems in science, industry, sociology, etc. It is common for researchers to build a _model_ of the system being studied, in part to compare actual results with model predictions, confirming or rejecting the underlying theories about the system upon which the model was built. Also, if the model is accurate, it provides predictive capabilities for possible and likely future events.

Contrast with [_determinism_](#determinism).

## Refactoring

Modifying code to change its structure as required to support a new feature. _No behavior changes are introduced_, so that the existing automated [_tests_](#test) can verify that no regressions are introduced as the code is modified. This is first step in the [_test-driven development_](#test-driven-development) cycle.

## Regression

When an unexpected behavior change is introduced into previously-working [_function_](#function), because of a change made to the code base, often in other functions for unrelated functionality.

Automated [_tests_](#test) are designed to catch regressions as soon as they occur, making it easier to diagnose the change that caused the regression, as well as detecting the regression in the first place.

## Repeatable

If an action, like running a test, is run repeatedly with no code or data changes, does it return the same results every time? By design, [_generative AI models_](#generative-ai-model) are _expected_ to return different results each time a query is repeated.

## Robustness

How well does the [_AI system_](#ai-system) continue to perform within acceptable limits or degrade &ldquo;gracefully&rdquo; when stressed in some way? For example, how well does a [_generative AI model_](#generative-ai-model) respond to prompts that deviate from its training data?

## Side Effect

Reading and/or writing state shared outside a [_function_](#function) with other functions. See also [_determinism_](#determinism).

## Test

For our purposes, a [_unit_](#unit-test), [_integration_](#integration-test), or [_acceptance_](#acceptance-test) test.

## Test Double

A test-only replacement for a [_function_](#function) with [_side effects_](#side-effect), so it returns [_deterministic_](#determinism) values or behaviors when a dependent function uses it. For example, a function that queries a database can be replaced with a version that always returns a fixed value expected by the test.

See also [_test_](#test), [_unit test_](#unit-test), [_integration test_](#integration-test), and [_acceptance test_](#acceptance-test).

## Test-Driven Development

When adding a [_feature_](#feature) to a code base using _TDD_, the tests are written _before_ the code is written. A three step &ldquo;virtuous&rdquo; cycle is used, where changes are made _incrementally_ and _iterative_ using small steps, one at a time:

1. [_refactor_](#refactoring) the code to change its structure as required to support the new feature, using the existing automated [_tests_](#test) to verify that no regressions are introduced. For example, it might be necessary to introduce an abstraction to support two &ldquo;choices&rdquo; where previously only one choice existed.
2. Write a [_test_](#test) for the new feature. This is _primarily_ a _design_ exercise, because thinking about testing makes you think about usability, behavior, etc., even though you are also creating a reusable test that will become part of the [_regression_](#regression) test suite. Note that the test suite will fail to run at the moment, because the code doesn't yet exist to make it pass!
3. Write the new feature to make the new test (as well as all previously written tests) pass.

The [_Wikipedia_]({{site.baseurl}}/references/#wikipedia) article on [_TDD_](https://en.wikipedia.org/wiki/Test-driven_development){:target="tdd"} is a good place to start for more information.

## Token

For language [_generative AI models_](#generative-ai-model), the training texts and query prompts are split into tokens, usually whole words or fractions according to a vocabulary of tens of thousands of tokens that can include common single characters, several characters, and &ldquo;control&rdquo; tokens (like &ldquo;end of input&rdquo;). The rule of thumb is a corpus will have roughly 1.5 times the number of tokens as it will have words.

## Training

In our context, training is the processes used to teach a model, such as a [_generative AI models_](#generative-ai-model) how to do its intended job. 

In the generative AI case, we often speak of _pretraining_, the training process that uses a massive data corpus to teach the model facts about the world, how to speak and understand human language, and do some skills. However, the resulting model often does poorly on specialized tasks and even basic skills like following a user's instructions, conforming to social norms (e.g., avoiding hate speech), etc. 

That's where a second [_tuning_](#tuning) phase comes in, a suite of processes used to improve the models performance on many general or specific skills.

## Tuning

Tuning refers to one or more processes used to transform a [_pretrained_](#training) model into one that exhibits much better desired behaviors (like instruction following) or specialized domain knowledge.

## Unit Test

A test for a function that exercises its behavior in isolation from all other functions and state. When the function being tested has [_side effects_](#side-effects), perhaps indirectly through other functions it calls, all such side effects must be replaced with [_test doubles_](#test-double) to make the test [_deterministic_](determinism). See also [_test_](#test), [_integration test_](#integration-test), and [_acceptance test_](#acceptance-test).
