---
layout: default
title: Unit Benchmarks
nav_order: 240
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

When testing applications with nondeterministic model output, an ad-hoc combination of [Benchmarks]({{site.glossaryurl}}/#benchmark) and &ldquo;playing around&rdquo; (manual testing) are typically done today.

Benchmarks are a popular tool for &ldquo;globally&rdquo; evaluating how well models perform categories of activities like code generation, Q&A (question and answer sessions), avoid hate speech, avoid hallucinations, etc. A typical benchmark attempts to provide a wide range of examples across the category and report a single number for the evaluation, usually scaled as a percentage of passing results between 0 and 100%). 

In contrast, good software tests are very specific, examining one specific [Behavior]({{site.glossaryurl}}/#behavior), while keeping everything else _invariant_.

Why not write focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused very narrowly?

Suppose we want to define unit tests that verify our application does a very good job generating SQL queries from human text. We have tuned a model to be very knowledgeable about the databases, schemas, and typical queries in our organization.

We can build a Q&A dataset for this purpose using logged queries in the past. Some human labeling will likely be required to create human text equivalents for the example queries, which would provide the expected answers. Each _unit benchmark_ could focus on one specific kind of common query for one specific table.

What about the cost of running lots of examples through your LLM? Say you have 100 examples in each fine-grained unit benchmark and yo have 100 of those benchmarks. How long with each full test run take for those 10,000 invocations and how expensive will they be? 

For traditional unit testing, your development environment might only invoke the tests associated with the source files that have just changed, saving a full run for occasional purposes, like before saving changes to version control. Can you develop a similar strategy here, where only a subset of your unit benchmarks are invoked for incremental updates, while the full suite is only invoked occasionally? 

To reduce testing time and costs, could you use a version of your production model that is quantized or a version with fewer parameters? Will the results during unit testing be good enough that running against the production model can be saved for periodic integration test runs? The smaller model may allow you to do inference on your development machine, rather than calling a service for every invocation, which is slow and expensive!

A related approach that is widely used is to leverage a separate model, one that is very smart and expensive to use, as a _judge_ to generate Q&A pairs for the benchmarks. See [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge).

## Adapting Domain-Specific Benchmarks

While the best-known benchmarks tend to be broad in scope, there is a growing set of domain-specific benchmarks that could provide a good starting point for your application-specific benchmarks.

Here is a list of some domain-specific benchmarks... or at least the start of this list. [Let us know]({{site.baseurl}}/contributing/#join-us) of any that you find!

{: .note}
> **Note:** Check the licenses for any benchmark you use, as some of them may have restrictions on use. Also, you can find many proprietary benchmarks that might be worth the investment for your purposes. See also the [references]({{site.baseurl}}/references) for related resources.

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
