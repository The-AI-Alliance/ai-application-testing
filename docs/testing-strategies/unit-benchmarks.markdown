---
layout: default
title: Unit Benchmarks
nav_order: 310
parent: Testing Strategies and Techniques
has_children: false
---

# &ldquo;Unit Benchmarks&rdquo; - Benchmarks as Tests

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

When testing AI applications with their [Stochastic]({{site.glossaryurl}}/#stochastic) model behaviors, an ad-hoc combination of existing [Benchmarks]({{site.glossaryurl}}/#benchmark) and &ldquo;playing around&rdquo; manual testing are typically used. This is a step backwards from the rigor of testing practices for non-AI applications, where deterministic, repeatable, and automated tests are the norm, covering [Unit Testing]({{site.glossaryurl}}/#unit-test) for fine-grained behavior, [Integration Testing]({{site.glossaryurl}}/#integration-test) for verifying that units work correctly together, and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-test) for final validation that the [Behaviors]({{site.glossaryurl}}/#behavior) of [Features]({{site.glossaryurl}}/#feature) and [Use Cases]({{site.glossaryurl}}/#use-case) are correctly implemented.

[&ldquo;Unit Benchmarks&rdquo;]({{site.glossaryurl}}/#unit-benchmark) are an adaptation of benchmarking tools and techniques for the same kinds of focused tests that traditional tests provide, this time for AI components. The goal is to use them, in combination with more traditional tests, to return to the practice of comprehensive, repeatable, and automatable testing, even for AI-enabled applications. The concepts generalize to [Integration Benchmarks]({{site.glossaryurl}}/#integration-benchmark) and [Acceptance Benchmarks]({{site.glossaryurl}}/#acceptance-benchmark).

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. We can adapt [Benchmark]({{site.glossaryurl}}/#benchmark) concepts to be appropriate for unit, integration, and acceptance testing of AI components, creating analogs we call [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark), [Integration Benchmarks]({{site.glossaryurl}}/#integration-benchmark), and [Acceptance Benchmarks]({{site.glossaryurl}}/#acceptance-benchmark), respectively.
> 1. Benchmarks require good datasets with prompts designed to probe how a model or AI-enabled component behaves in a certain area of interest, along with responses that represent acceptable answers. Following conventional practice,[^1] we will use the term question and answer (Q&A) pairs for these prompts and responses.
> 1. We may have suitable data for our domain that we can adapt for this purpose, for example logs of past customer interactions. However, adapting this data can be time consuming and expensive.
> 1. When we don't have enough test data available already, we should synthesize the test data we need using generative tools. This is much faster than collecting data or writing examples manually, which is slow, expensive, and error prone, as humans are not good at finding and exploring corner cases, where bugs often occur.
> 1. A [Teacher Model]({{site.glossaryurl}}/#teacher-model) can be used as part of a process of generating synthetic Q&A pairs, and also validating their quality.
> 1. We have to run experiments to generate good Q&A pairs and to determine the number of them we need for comprehensive and effective test coverage.
> 1. There are many [Evaluation]({{site.glossaryurl}}/#evaluation) tools that can be used for synthetic data generation and benchmark creation and execution.

[^1]: Not all benchmarks use Q&A pair datasets like this. For example, some benchmarks use a specially-trained model to evaluate content, like detecting SPAM or hate speech. For simplicity, we will only consider benchmarks that work with Q&A pairs, but most of the principles we will study generalize to other benchmark techniques.

Benchmarks are the most popular tool used to [Evaluate]({{site.glossaryurl}}/#evaluation) how well models perform in &ldquo;categories&rdquo; of activity with broad scope, like code generation, Q&A (question and answer sessions), instruction following, Mathematics, avoiding hate speech, avoiding hallucinations, etc. The typical, popular benchmarks attempt to provide a wide range of examples across the category and report a single number for the evaluation, the percentage of passing results between 0 and 100%. (We discuss a few examples [here](#adapting-third-party-public-domain-specific-benchmarks).)

We discussed in [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/#test-scope) that good software components and tests are very specific to a particular scope. A unit test that examines one specific [Behavior]({{site.glossaryurl}}/#behavior) of a [Unit]({{site.glossaryurl}}/#unit), while keeping everything else _invariant_. The scope of an integration test is scope of the units and [Components]({{site.glossaryurl}}/#component) it examines, while the scope of an acceptance test is one end-to-end [Use Case]({{site.glossaryurl}}/#use-case) [Scenario]({{site.glossaryurl}}/#scenario).

Why not write more focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused narrowly for each particular scope?

## Revisiting our TDD Example

In [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/), we discussed a hypothetical healthcare ChatBot and wrote an informal [unit benchmark]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai) for it. We created a handful of Q&A pairs for testing, but we also remarked that this manual curation is not scalable and it is error prone, as it is difficult to cover all the ways someone might request a refill, including potential corner cases, such as ambiguous messages. We need better datasets of Q&A pairs. 

### Acquiring the Test Data Required

There are a many publicly-available ChatBot benchmark suites, but they tend to be generic, broadly covering overall conversational abilities. They are worth investigating for testing the general Q&A abilities of the application, but they rarely cover more specific domains and they are very unlikely to cover our specific use cases. Hence, none of them are fine-grained in the ways that we need.

We may have historical data we can adapt into test data, such as saved online chats and phone calls between patients and providers, for our example. Adapting this data into suitable Q&A pairs for testing is labor intensive, although LLMs can accelerate this process. For example, you can feed one or more sessions to a good LLM and ask it to generate Q&A pairs based on the conversation. Everything we will discuss about validating test data, from manual inspection to automated techniques, still applies.

Also, for some domains, we may have good data, but it may have tight restrictions on use, like patient healthcare data subject to privacy laws. Using such data for testing purposes may be disallowed.

For completeness, another use for domain-specific historical data is to [Tune]({{site.glossaryurl}}/#tune) a &ldquo;generic&rdquo; model to be better at our use cases. The tuned model is then used for testing and production inference. Tuning is not yet a widespread technique for building AI applications, but tuning tools and techniques are becoming easier to use by non experts, so we anticipate that tuning will become more routine over time.

Suppose we don't have enough historical test data for our needs, for whatever reasons. Generation of synthetic data is our tool of choice.

## Synthetic Data Generation and Validation

So far, our narrowly-focused unit benchmark from the [TDD]({{site.baseurl}}/arch-design/tdd/) chapter exercised one behavior, detecting and handling a prescription refill request or any &ldquo;other&rdquo; message. From now on, we will think of this as _two_ units of behavior from the point of view of benchmarking: handing refill requests and handling all other queries for which we don't support special handling.

We will continue to follow this strategy:

1. Identify a new _unit_ (behavior) to implement.
1. Write one or more new unit benchmarks for it, including...
  1. Generate a separate dataset of Q&A pairs for the benchmark. 
1. Write whatever application logic is required for the unit, including suitable prompts for the generative models involved.

We will focus on the first two steps. The third step will be covered in [A Working Example]({{site.baseurl}}/working-example).

In addition to synthesizing Q&A pairs for the two behaviors we already have, we will add a new unit of behavior and a corresponding benchmark to study detection of prompts where the patient appears to require urgent or emergency care, in which case we want the response to be that the patient should call 911 (in the USA) immediately[^2].

[^2]: Anyone who has called a doctor's office in the USA has heard the automated message, "If this is a medical emergency, please hang up and dial 911."

### Generating the Synthetic Data

The [project repo]({{site.gh_edit_repository}}/){:target="_blank"} contains a tool [`src/scripts/unit-benchmark-data-synthesis.py`]({{site.gh_edit_repository}}/blob/main/src/scripts/unit-benchmark-data-synthesis.py/){:target="_blank"} that uses an LLM to generate Q&A pairs for the three unit benchmarks, each corresponding to the `prompt` from the following template files[^3]:

[^3]: Recall we said previously that these templates files are designed to be compatible with the `llm` CLI tool.

| Unit Benchmark | Template File | 
| :------------- | :------------ | 
| Prescription refill requests | [`synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml){:target="_blank"} |
| Apparent emergencies | [`synthetic-q-and-a_patient-chatbot-emergency-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency-data.yaml){:target="_blank"} |
| Other messages | [`synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml){:target="_blank"} |

Here is the prompt for the _emergency_ use case:

```text
You are a helpful assistant to generate synthetic question and answer (Q&A) pairs for
testing a healthcare ChatBot that allows medical patients to request help from their 
care provider. Some patients will request prescription refills, while some messages 
will be for other purposes. In some cases, the patient will need urgent attention, in
which case they should stop using the ChatBot and call 911 instead. Here are some
examples of other requests that should be interpreted as emergency situations,
where _P_ would be replaced by the name of a prescription the user mentions in the
message and _B_ would be a place in the patient's body where he or she feels pain or
has some other question or comment about it:

- "Since I started taking my prescription for _P_, I have trouble breathing."
- "Since I started taking my prescription for _P_, I have hives all over my skin."
- "Since I started taking my prescription for _P_, I have severe swelling."
- "Since I started taking my prescription for _P_, I have severe stomach cramps."
- "I have severe pain in my _B_."
- "I have severe pain in my _B_. What should I do?"
- "I have severe pain in my _B_. I think I need a referral to a specialist."
- "I have severe swelling in my _B_."
- "I have severe swelling in my _B_. What should I do?"
- "I have severe swelling in my _B_. I think I need a referral to a specialist."
- "I have trouble breathing."
- "I have trouble breathing. What should I do?"
- "I have trouble breathing. I think I need a referral to a specialist."
- "I have a sharp pain in my chest."
- "I have a sharp pain in my chest. What should I do?"
- "I have a sharp pain in my chest. I think I need a referral to a specialist."

Using these examples for inspiration, GENERATE AT LEAST 100 Q&A PAIRS, where each question 
or prompt suggests the patient needs urgent or emergency care. In the questions and answers,
insert _P_ as a placeholder for any mention of a prescription's name and insert _B_ for any 
mention of the patient's body part. Keep generating Q&A pairs until you have output at least
100 of them.

Write the Q&A pairs using this JSONL output:

- \"{"question": question, "answer": {"label": "_l_", "prescription": "_p_", "body-part": "_b_"}}\" 

DO NOT write any comments around the JSONL lines and do not wrap the JSONL in Markdown or 
other markup syntax. Just print the JSONL lines.

In the answer,
- Replace _l_ with "emergency" if the question (or message) appears to be an urgent or emergency situation, 
  use "refill" for a prescription refill request, or use "other" for any other message.
- Replace _p_ with _P_ if _P_ is mentioned in the question. Otherwise, replace _p_ with an empty string.
- Replace _b_ with _B_ if _B_ is mentioned in the question. Otherwise, replace _b_ with an empty string.
```

The other two prompts are similarly worded for their requirements.

### How Many Q&A Pairs Do We Need?

The prompts above ask for _at least 100_ Q&A pairs. This is an arbitrary number. The well-known, broad benchmarks for AI often have many thousands of Q&A pairs (or their equivalents).

For fine-grained _unit_ benchmarks, a suitable number could vary between tens of pairs, for simpler test scenarios, to hundreds of pairs for &ldquo;average&rdquo; complexity test scenarios, to thousands of pairs for complex test scenarios. The optimal number will also vary from one unit benchmark to another. 

Because [Integration Benchmarks]({{site.glossaryurl}}/#integration-benchmark) and [Acceptance Benchmarks]({{site.glossaryurl}}/#acceptance-benchmark) have broader scope, by design, they will usually require relatively larger datasets.

There aren't any hard and fast rules; we will have to experiment to determine what works best for each case. More specifically, as we study the results of a particular benchmark's runs, what number of pairs gives us sufficient, comprehensive coverage and therefore confidence that this benchmark thoroughly exercises the behavior? We can always err on the side of too much test data, but we may run into overhead concerns. 

### Thinking about Overhead

What about the cost of running lots of examples through an LLM? Say we have 100 examples in each fine-grained unit benchmark and we have 100 of those benchmarks. How long will each full test run take for those 10,000 invocations and how expensive will they be? We will have to benchmark these runs to answer these questions. If we use a commercial service for model inference during tests, we may need to watch those costs carefully.

For traditional unit testing, our development tools usually only invoke the unit tests associated with the source files that have just changed, saving full test runs for occasional purposes, such as part of the PR (pull request) process in GitHub. This optimization not only saves compute resources, it makes the cycle of editing and testing much faster. Instantaneous would be ideal, but running unit benchmarks are likely to be much slower, especially for larger datasets and doing inference during tests with larger models. Using a hosted service for inference vs. local inference _may_ be slower, but if the development machine is hitting resource limits when doing inference, it may be slower than going over the Internet for a hosted-service inference call!

When we [discuss integration]({{site.baseurl}}/working-example/#integration-into-test-suites) of our benchmarks into our testing suites, like PyTest, We can try to ensure that only a relevant subset of them are invoked for incremental feature changes, while the full suite is invoked less frequently, such as during PR (pull request) processes. 

Similarly, runs of the integration and acceptance tests, which are relatively slow and expensive, are typically run a few times per day. 

To reduce testing time and costs, we will want to experiment with model choices, both for the production deployments and for development purposes. For example, if we have picked a production version of a model, there may be smaller versions we can use successfully during development. We might have to trade off the quality of responses, as long as the results during testing remain &ldquo;good enough&rdquo;. 

However, since acceptance tests are designed to confirm that a feature is working in real production scenarios (or as close to those as possible in our test environment), we must use the full production models for acceptance tests. 

### Running the Data Synthesis Tool

Try running this tool yourself using `make`. If you haven't done so, follow the setup instructions in the [Try It Yourself!]({{site.baseurl}}/arch-design/tdd/#try-it-yourself) section in the [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/) chapter. The instructions are also the project repository's [README]({{site.gh_edit_repository}}/){:target="_blank"}. 

Once setup, here is the `make` command to run the data synthesis tool with the default model, `ollama/gpt-oss:20b`:

```shell
make run-unit-benchmark-data-synthesis
```

After some setup, the following command is executed:

```shell
time uv run src/scripts/unit-benchmark-data-synthesis.py \
  --model ollama/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir src/prompts/templates \
  --output temp/output/ollama/gpt-oss_20b/unit-benchmark-data-synthesis.out \
  --data temp/output/ollama/gpt-oss_20b/data
```

Recall that a different model can be specified, i.e., `make MODEL=ollama/llama3.2:3B`run-unit-benchmark-data-synthesis`. (See the project README and also in [Running the TDD Tool]({{site.baseurl}}/arch-design/tdd/#running-the-tdd-tool).) 

Note the arguments for where output is captured (`--output`) and the data Q&A pairs files are written (`--data`). Specifically, the following data files are written, examples of which can be found [in the repository](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama){:target="_blank"} (for both `gpt-oss:20b` and `llama3.2:3B`):

| Synthetic Data File | `gpt-oss:20b` | `llama3.2:3B` |
| :---- | :---- | :---- |
| `synthetic-q-and-a_patient-chatbot-emergency-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-emergency-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.json){:target="_blank"} |

They cover the three _unit-benchmarks_:
* `emergency`: The patient prompt suggests he or she needs urgent or emergency care, so the patient should stop using the ChatBot and call 911 (in the US) immediately.
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

The actual "answer" in each Q&A pair is a JSON object with one of these labels and some additional information. We mentioned in the [TDD]({{site.baseurl}}/arch-design/tdd/) chapter that generating ad-hoc text like, "It sounds like you are having an emergency. Please call 911..." doesn't make sense for FAQs. It's better to return labels and have the application reply in a deterministic way.

Here is an example from the _emergency_ file (nicely formatted):

```json
{
  "question": "Since I started taking my prescription for _P_, I feel like my heart is racing and I'm short of breath.",
  "answer": { 
    "label": "emergency",
    "prescription": "_P_",
    "body-part":"heart"
  }
}
```

Note that the answer has the identified prescription (placeholder `_P_`) and the specific body part (heart) found in the question.

Each of the Q&A data files is generated with a single inference invocation, using the prompt in the corresponding template file discussed above. In some cases, output Q&A pairs don't actually fit the use case. There are times when a _prescription refill_ Q&A pair is labeled as an emergency, times when an _emergency_ Q&A pair is labeled a _refill_, etc. This is more likely to happen with smaller models. Is this _okay_? We will return to this issue of _cross pollination_ in [LLM as a Judge]({{site.baseurl}}/llm-as-a-judge).

Finally, even though the system prompt emphasizes that we want _at least_ 100 Q&A pairs, we rarely got that many in the actual results with `llama3.2:3B`, while using `gpt-oss:20b` over delivered. This is probably more of a quirk of using a small model than a reflection of any &ldquo;defects&rdquo; or advantages of one model architecture vs. the other.

## Evaluating the Synthetic Data

In the TDD example, we used a system prompt to cause the LLM to _almost_ always return a deterministic answer for the two cases, a prescription refill request and everything else. When you have a scenario like this, it simplifies evaluating the Q&A pair. We were able to hard-code logic in the tool to compare the actual and expected outputs, after some minor reformatting of the actual output to eliminate some trivial differences.

For the more general case, where the output isn't as deterministic, but more [Stochastic]({{site.glossaryurl}}/#stochastic), we have to lean on other techniques.

One of the best techniques is to rely on a [Teacher Model]({{site.glossaryurl}}/#teacher-model) to evaluate synthetic data based on a few criteria:

* Is the question relevant to the purpose of this test?
* If the question is relevant, is the supplied answer correct?

We examine this process in [LLM as a Judge]({{site.baseurl}}/testing-strategies/LLM-as-a-Judge). Other techniques we will explore include [External Tool Verification]({{site.baseurl}}/external-verification/), and [Statistical Evaluation]({{site.baseurl}}/statistical-tests/).

## Adapting Third-Party, Public, Domain-Specific Benchmarks

While the best-known benchmarks tend to be too broad in scope and generic for our needs, they are good sources of ideas and sometimes actually data. There is also a growing set of domain-specific benchmarks that could provide good starting points for test benchmarks.

Note that benchmarks fall into the broad category of [Evaluation]({{site.glossaryurl}}/#evaluation), including datasets and tools for safety purposes. Many of the datasets and tools discussed below use this term, so we call it out here for clarity.

Here is a list of some domain-specific benchmarks that we know of. [Let us know]({{site.baseurl}}/) of any others you find useful, so we can add them here.


### General Collections of Domain-Specific Evaluations

* [Weval](https://weval.org/sandbox){:target="weval"} from the [Collective Intelligence Project](https://www.cip.org/){:target="cip"}, is a community-driven collection of domain-specific evaluations, designed to allow non-experts to contribute and use evaluation suites relevant to their needs. 
* [ClairBot](https://clair.bot/){:target="clairbot"} from the Responsible AI Team at [Ekimetrics](https://ekimetrics.com/){:target="ekimetrics"} is a research project that compares several model responses for domain-specific questions, where each of the models has been tuned for a particular domain, in this case ad serving, laws and regulations, and social sciences and ethics.

### Education

* The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}.

### Finance

Benchmarks for finance applications.

* Patronus AI [FinanceBench](https://github.com/patronus-ai/financebench){:target="finance-bench"}

### Healthcare 

Benchmarks for testing health-related use cases.

* OpenAI [Healthbench](https://openai.com/index/healthbench/){:target="oai-hb"}
* Stanford HELM for healthcare, [MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/){:target="medhelm"}

### Industrial Systems

I.e., manufacturing, shipping, etc.

* FailureSensorIQ
  * [paper](https://arxiv.org/abs/2506.03278){:target="_blank"} &ldquo;... a novel Multi-Choice Question-Answering (MCQA) benchmarking system designed to assess the ability of Large Language Models (LLMs) to reason and understand complex, domain-specific scenarios in Industry 4.0. Unlike traditional QA benchmarks, our system focuses on multiple aspects of reasoning through failure modes, sensor data, and the relationships between them across various industrial assets.&rdquo;
  * [GitHub](https://github.com/IBM/FailureSensorIQ){:target="_blank"}
  * [Dataset](https://huggingface.co/datasets/ibm-research/AssetOpsBench){:target="_blank"}

### Legal

* Stanford [LegalBench](https://hazyresearch.stanford.edu/legalbench/){:target="legalbench"} ([paper](https://arxiv.org/abs/2308.11462){:target="arxiv"})

### Software Engineering

Benchmarks for testing software engineering use cases.

* Open AI [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/){:target="oai-swe"}

### Other Domains?

What other domains would you like to see here?

<a id="other-tools"/>

## Other Tools for Unit Benchmarks

We are using relatively-simple, custom tools for our examples, which work well so far, but may not be as flexible for real-world use in large development teams with diverse skill sets and large evaluation suites. Here are some additional tools to explore. 

Additional tools that have some data synthesis and evaluation capabilities are discussed in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/#other-tools) and [From Testing to Tuning]({{site.baseurl}}/future-ideas/from-testing-to-tuning/#other-tools).

See also [A Working Example]({{site.baseurl}}/working-example) for a discussion of integrating new tools into existing frameworks, like [PyTest](https://docs.pytest.org/en/stable/){:target="_blank"}.

### Other Tools for Synthetic Data Generation

If you use synthetic data generation a lot in your organization, it will become necessary to understand some of the potential complexities that you might encounter. [Synthetic Data Generation Using Large Language Models: Advances in Text and Code](https://arxiv.org/abs/2503.14023){:target="_blank"} surveys techniques that use LLMs, like we are doing. 

#### synthetic-data-kit

Meta's [`synthetic-data-kit`](https://github.com/meta-llama/synthetic-data-kit/){:target="_blank"} focuses on larger-scale data synthesis and processing (such as translating between formats), especially for model [Tuning]({{site.glossaryurl}}/#tuning) with Llama models.

#### Older Synthetic Data Tools

[Nine Open-Source Tools to Generate Synthetic Data](https://opendatascience.com/9-open-source-tools-to-generate-synthetic-data/){:target="_blank"} lists several tools that use different approaches for data generation, serving different purposes. For example, several use [Generative Adversarial Networks]({{site.glossaryurl}}/#generative-adversarial-networks), a technique most popular in the late 2010s.

### More Advanced Benchmark and Evaluation Tools

Similarly, there are other general-purpose tools for authoring, managing, and running benchmarks and evaluations. 

{: .todo}
> **TODO:** The following sections are placeholders. We intend to provide more coverage of these tools, as well as add new tools as we become aware of them. [Contributions are welcome!]({{site.baseurl}}/contributing). See [issue #22](https://github.com/The-AI-Alliance/ai-application-testing/issues/22){:target="_blank"} for details. Other [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues/){:target="_blank"} discuss particular tools on our radar for investigation.

#### PleurAI Intellagent

[Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} demonstrates some advanced techniques developed by [Plurai](https://www.plurai.ai/){:target="_blank"} for understanding a project's requirements and interdependencies, then using this _graph_ of information to generate synthetic datasets and tests.

#### LM Evaluation Harness

[LM Evaluation Harness](https://www.eleuther.ai/projects/large-language-model-evaluation){:target="lm-site"} is a de facto standard tool suite for defining and running evaluations. Its distribution comes with a rich suite of evaluations for safety and other topics.

#### Unitxt

[Unitxt](https://www.unitxt.ai){:target="unitxt"} makes it easy to generate evaluations with minimal coding required. Its distribution comes with a rich suite of evaluations for safety and other topics.

Some examples using `unitxt` are available in the [IBM Granite Community](https://github.com/ibm-granite-community){:target="igc"}, e.g., in the [Granite &ldquo;Snack&rdquo; Cookbook](https://github.com/ibm-granite-community/granite-snack-cookbook){:target="igc-snack"} repo. See the [`recipes/Evaluation`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation){:target="igc-snack-eval"} folder. These examples only require running [Jupyter](https://jupyter.org/){:target="jupyter"} locally, because all inference is done remotely by the community's back-end services. Here are the specific Jupyter notebooks:

* [`Unitxt_Quick_Start.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Quick_Start.ipynb){:target="igc-snack-eval1"} - A quick introduction to `unitxt`.
* [`Unitxt_Demo_Strategies.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Demo_Strategies.ipynb){:target="igc-snack-eval2"} - Various ways to use `unitxt`.
* [`Unitxt_Granite_as_Judge.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Granite_as_Judge.ipynb){:target="igc-snack-eval3"} - Using `unitxt` to drive the _LLM as a judge_ pattern.

#### Using LM Evaluation Harness and Unitxt Together

Evaluations implemented with `unitxt` can be executed by LM Evaluation Harness. Start with [this `unitxt` documentation page](https://www.unitxt.ai/en/latest/docs/lm_eval.html){:target="unitxt-lm-eval"}, then look at the [`unitxt` tasks](https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/unitxt){:target="unitxt-lm-eval2"} described in the [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness){:target="lm-eval"} repo.

#### Final Thoughts on Advanced Benchmark and Evaluation Tools

Be careful to check the licenses for any benchmarks or tools you use, as some of them may have restrictions on use. Also, you can find many proprietary benchmarks that might be worth the investment for your purposes. See also the [references]({{site.baseurl}}/references) for related resources.

[Let us know]({{site.baseurl}}/contributing/#join-us) of any other tools that you think we should discuss here!

While use of benchmarks with synthetic data generation of Q&A pairs is standard practice, see [this &ldquo;Beyond Benchmarks&rdquo; discussion]({{site.baseurl}}/references/#university-of-tübingen) about a possible alternative approach.

## Experiments to Try

There is a lot to explore here:

* Study the Q&A pairs generated. How might you refine the prompts to be more effective at generating good data?
* One way to assist studying the data is to ask the model to also generate a _confidence_ rating for how good it thinks the Q&A pair is for the target unit benchmark and how good it thinks the answer is for the question. Try this experiment using a scale of 1-5, where one is low confidence and five is high confidence. Make sure to also ask for an explanation for why it provided that rating. Review the Q&A pairs with low confidence scores. Should they be discarded automatically below a certain threshold? Do they instead suggest good corner cases for further exploration? If there are a lot of low confidence pairs in the output, could the prompt be improved to provide better clarity about the desired output dataset?  
* Try different runs where you vary the requested number of Q&A pairs in the prompts from tens of pairs up to many hundreds. What are the impacts for compute resources and time required? Look through the data sets. Can you develop an intuition about which sizes are sufficient large for good coverage? Is there an approximate size beyond which lots of redundancy is apparent? Save these outputs for revisiting in subsequent chapters. 
* Add more unit benchmarks for new behaviors. For example, explore requests for referrals to specialists.
* Try other models. See how bigger and smaller models perform, especially within the same &ldquo;family&rdquo;, like Llama.
* How might you modify the example to handle a patient prompt that includes a refill request and other content that requires a response? We have assumed that a prompt with a refill request contains no other content that requires separate handling. In other words, our _classifier_ only returns one label for the prompt. What if it returned a list of labels and a _confidence_ score for each one? Because of _cross pollination_, all the prompts used to generate Q&A pairs for all the unit benchmarks should be modified to support one or more responses (e.g., the requested JSONL format of the &ldquo;answers&rdquo;). However, treat testing for this specific situation as a new unit benchmark.
* For all of the above, note the resource requirements, such as execution times, hardware resources required for the models, service costs if you use an inference service, etc.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/).

---
