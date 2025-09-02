---
layout: default
title: Unit Benchmarks
nav_order: 240
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

Currently, when testing AI applications with their nondeterministic model behaviors, an ad-hoc combination of existing [Benchmarks]({{site.glossaryurl}}/#benchmark) and ad hoc manual testing are used. This is a step backwards from the rigor of testing practices for non-AI applications, where deterministic, repeatable, and automated tests are the norm, covering [Unit Testing]({{site.glossaryurl}}/#unit-test) for fine-grained behavior, [Integration Testing]({{site.glossaryurl}}/#integration-test) for verifying that units work correctly together, and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-test) for final validation that the [Behaviors]({{site.glossaryurl}}#behavior) of [Features]({{site.glossaryurl}}/#feature) and [Use Cases]({{site.glossaryurl}}/#use-case) are correctly implemented.

_Unit benchmarks_ are an adaptation of benchmarking tools and techniques for the same kinds of focused tests that traditional tests provide, this time for AI components.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. We can adapt benchmark concepts to be appropriate for unit, integration, and acceptance testing of AI components.

Benchmarks are a popular tool for _globally_ evaluating how well models perform &ldquo;categories&rdquo; of activity like code generation, Q&A (question and answer sessions), avoiding hate speech, avoiding hallucinations, etc. A typical benchmark attempts to provide a wide range of examples across the category and report a single number for the evaluation, usually scaled as a percentage of passing results between 0 and 100%). 

In contrast, good software tests are very specific, examining one specific [Behavior]({{site.glossaryurl}}/#behavior), while keeping everything else _invariant_. The scope of the test will vary from fine grained for unit tests to broad for integration tests to whole-application for acceptance tests.

Why not write more focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused very narrowly?

Suppose we want to define unit tests that verify our application does a very good job generating SQL queries from human text. We have tuned a model to be very knowledgeable about the databases, schemas, and typical queries in our organization.

We can build a Q&A dataset for this purpose using logged queries in the past. Some human labeling will likely be required to create human text equivalents for the example queries, which would provide the expected answers. Each _unit benchmark_ could focus on one specific kind of common query for one specific table.

What about the cost of running lots of examples through your LLM? Say you have 100 examples in each fine-grained unit benchmark and you have 100 of those benchmarks. How long with each full test run take for those 10,000 invocations and how expensive will they be? 

For traditional unit testing, your development environment might only invoke the tests associated with the source files that have just changed, saving a full run for occasional purposes, like before saving changes to version control. Can you develop a similar strategy here, where only a subset of your unit benchmarks are invoked for incremental updates, while the full suite is only invoked occasionally? 

To reduce testing time and costs, could you use a version of your production model that is quantized or a version with fewer parameters? Will the results during unit testing be good enough that running against the more-expensive production model can be reserved for less frequent integration test runs? Another benefit of a smaller model is the ability to do inference on development machines, rather than having to call a inference service for every invocation, which is slower and more expensive.

A related approach that is widely used is to leverage a separate model, one that is very smart and expensive to use, as a _judge_ to generate Q&A pairs for the benchmarks. See [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge).

## Revisting our TDD Example

In [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/), we sketched a [unit benchmark]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai) for a healthcare ChatBot, specifically a feature where patient requests for a prescription refill result in the same deterministic response.

We hand-wrote several example Q&A pairs that focused only on this feature, and nothing else about the ChatBot's behavior. In other words, while there are a many available ChatBot benchmarks, they tend to be very broad, covering overall conversational abilities or perhaps facility for a a particular domain. 

In contrast, our unit benchmark was very narrowly focused. It exercised this one behavior and left other behaviors to be exercised by separate unit benchmarks. For each of those unit benchmarks, a separate suite of Q&A pairs would be written. For example, we will want a healthcare ChatBot to detect when the patient appears to be in need of urgent care, in which case the response should be to call 911 (in the USA) immediately[^1].

[^1]: Anyone who has called a doctor's office in the USA and heard the automated message, "If this is a medical emergency, please hang up and dial 911."

Like conventional unit tests, we can run this &ldquo;unit test&rdquo; any time we make a change that might affect the system behavior, as well as periodic, automated runs to catch regressions. 

Our example was somewhat _ad hoc_ in creation and execution. Let's look at more systematic approaches to creating and executing unit benchmarks:

1. Synthetic data generation and validation.
2. Integration into a standard testing framework.


### Synthetic Data Generation and Validation

In our TDD example, we wrote the Q&A pairs by hand for our unit benchmark. This has two disadvantages:

1. It is time consuming, so it doesn't scale well for large applications.
2. Covering the whole &ldquo;space&rdquo; of possible questions and answers is difficult and error prone.

The solution is to use generative AI to generate a lot of diverse Q&A pairs (or other benchmark data required). The disadvantage of this approach is ensuring that generated data is of good quality. We will discuss how to perform this assessment, too.


#### Evaluating the Synthetic Data

In the TDD example, we used a system prompt to cause the LLM to always returned a deterministic answer for the two cases, a prescription refill request and everything else. When you have a design like this, it makes it simplifies evaluating the Q&A pair. Essentially, we ask the teacher model, "For each question, is the corresponding answer correct?"

In the more general case, where the output isn't as deterministic, we have to lean more heavily on the teacher model to evaluate a few things:

* Is the question relevant to the purpose of this test?
* If the question is relevant, is the supplied answer correct?

#### PleurAI Intellagent



### Integration Into a Standard Testing Framework

* Ad hoc execution in your development workflows.
* PyTest and other Python test frameworks.

## Adapting Domain-Specific Benchmarks

While the best-known benchmarks tend to be broad in scope, there is a growing set of domain-specific benchmarks that could provide a good starting point for your more-specific benchmarks.

Here is a partial list of some domain-specific benchmarks that we know of. [Let us know]({{site.baseurl}}/contributing/#join-us) of any that you find that aren't listed here!

{: .note}
> **Note:** Check the license for any benchmark you use, as some of them may have restrictions on use. Also, you can find many proprietary benchmarks that might be worth the investment for your purposes. See also the [references]({{site.baseurl}}/references) for related resources.

### General Collections of Domain-Specific Evaluations

* [Weval](https://weval.org/sandbox){:target="weval"} from the [Collective Intelligence Project](https://www.cip.org/){:target="cip"}, is a community-driven collection of domain-specific evaluations, designed to allow non-experts to contribute and use evaluation suites relevant to their needs. 
* [ClairBot](https://clair.bot/){:target="clairbot"} from the Responsible AI Team at [Ekimetrics](https://ekimetrics.com/){:target="ekimetrics"} is a research project that compares several model responses for domain-specific questions, where each of the models has been tuned for a particular domain, in this case ad serving, laws and regulations, and social sciencies and ethics.

### Healthcare 

Benchmarks for testing health-related use cases.

* OpenAI [Healthbench](https://openai.com/index/healthbench/){:target="oai-hb"}
* Stanford HELM for healthcare, [MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/){:target="medhelm"}

### Software Engineering

Benchmarks for testing software engineering use cases.

* Open AI [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/){:target="oai-swe"}

### Finance

Benchmarks for finance applications.

* Patronus AI [FinanceBench](https://github.com/patronus-ai/financebench){:target="finance-bench"}

### Legal

* Stanford [LegalBench](https://hazyresearch.stanford.edu/legalbench/) ([paper](https://arxiv.org/abs/2308.11462){:target="arxiv"})

### Education

* The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}.

### Other Domains?

What other domains should we list here?


---

Review the [highlights](#highlights) summarized above, then proceed to [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).
.
