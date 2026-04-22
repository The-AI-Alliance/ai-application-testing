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

When testing AI applications with their [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} model behaviors, an ad-hoc combination of existing [Benchmarks]({{site.glossaryurl}}/#benchmark){:target="_glossary"} and &ldquo;playing around&rdquo; manual testing are typically used. This is a step backwards from the rigor of testing practices for non-AI applications, where deterministic, repeatable, and automated tests are the norm, covering [Unit Testing]({{site.glossaryurl}}/#unit-test){:target="_glossary"} for fine-grained behavior, [Integration Testing]({{site.glossaryurl}}/#integration-test){:target="_glossary"} for verifying that units work correctly together, and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-test){:target="_glossary"} for final validation that the [Behaviors]({{site.glossaryurl}}/#behavior){:target="_glossary"} of [Features]({{site.glossaryurl}}/#feature){:target="_glossary"} and [Use Cases]({{site.glossaryurl}}/#use-case){:target="_glossary"} are correctly implemented.

[&ldquo;Unit Benchmarks&rdquo;]({{site.glossaryurl}}/#unit-benchmark){:target="_glossary"} are an adaptation of benchmarking tools and techniques for the same kinds of focused tests that traditional tests provide, this time for AI components. The goal is to use them, in combination with more traditional tests, to return to the practice of comprehensive, repeatable, and automatable testing, even for AI-enabled applications. The concepts generalize to [Integration Benchmarks]({{site.glossaryurl}}/#integration-benchmark){:target="_glossary"} and [Acceptance Benchmarks]({{site.glossaryurl}}/#acceptance-benchmark){:target="_glossary"}.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. We can adapt [Benchmark]({{site.glossaryurl}}/#benchmark){:target="_glossary"} concepts to be appropriate for unit, integration, and acceptance testing of AI components, creating analogs we call [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark){:target="_glossary"}, [Integration Benchmarks]({{site.glossaryurl}}/#integration-benchmark){:target="_glossary"}, and [Acceptance Benchmarks]({{site.glossaryurl}}/#acceptance-benchmark){:target="_glossary"}, respectively.
> 1. Benchmarks require good data sets with prompts designed to probe how a model or AI-enabled component behaves in a certain area of interest, along with responses that represent acceptable answers. Following conventional practice,[^1] we will use the term question and answer (Q&A) pairs for these prompts and responses.
> 1. We may have suitable data for our domain that we can adapt for this purpose, for example logs of past customer interactions. However, adapting this data can be time consuming and expensive.
> 1. When we don't have enough test data available already, we should synthesize the test data we need using generative tools. This is much faster than collecting data or writing examples manually, which is slow, expensive, and error prone, as humans are not good at finding and exploring corner cases, where bugs often occur.
> 1. A [Teacher Model]({{site.glossaryurl}}/#teacher-model){:target="_glossary"} can be used as part of a process of generating synthetic Q&A pairs, and also validating their quality.
> 1. We have to run experiments to generate good Q&A pairs and to determine the number of them we need for comprehensive and effective test coverage.
> 1. There are many [Evaluation]({{site.glossaryurl}}/#evaluation){:target="_glossary"} tools that can be used for [Synthetic Data Generation]({{site.glossaryurl}}/#synthetic-data-generation){:target="_glossary"} and benchmark creation and execution.

[^1]: Not all benchmarks use Q&A pair data sets like this. For example, some benchmarks use a specially-trained model to evaluate content, like detecting SPAM or hate speech. For simplicity, we will only consider benchmarks that work with Q&A pairs, but most of the principles we will study generalize to other benchmark techniques.

Benchmarks are the most popular tool used to [Evaluate]({{site.glossaryurl}}/#evaluation){:target="_glossary"} how well models perform in &ldquo;categories&rdquo; of activity with broad scope, like code generation, Q&A (question and answer sessions), instruction following, Mathematics, avoiding hate speech, avoiding hallucinations, etc. The typical, popular benchmarks attempt to provide a wide range of examples across the category and report a single number for the evaluation, the percentage of passing results between 0 and 100%. (We discuss a few examples [here](#adapting-third-party-public-domain-specific-benchmarks).)

We discussed in [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/#test-scope) that good software components and tests are very specific to a particular scope. A unit test that examines one specific [Behavior]({{site.glossaryurl}}/#behavior){:target="_glossary"} of a [Unit]({{site.glossaryurl}}/#unit){:target="_glossary"}, while keeping everything else _invariant_. The scope of an integration test is scope of the units and [Components]({{site.glossaryurl}}/#component){:target="_glossary"} it examines, while the scope of an acceptance test is one end-to-end [Use Case]({{site.glossaryurl}}/#use-case){:target="_glossary"} [Scenario]({{site.glossaryurl}}/#scenario){:target="_glossary"}.

Why not write more focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused narrowly for each particular scope?

## Revisiting our TDD Example

In [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/), we discussed a hypothetical healthcare ChatBot and wrote an informal [unit benchmark]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai) for it. We created a handful of Q&A pairs for testing, but we also remarked that this manual curation is not scalable and it is error prone, as it is difficult to cover all the ways someone might request a refill, including potential corner cases, such as ambiguous messages. We need better data sets of Q&A pairs. 

### Acquiring the Test Data Required

There are a many publicly-available ChatBot benchmark suites, but they tend to be generic, broadly covering overall conversational abilities. They are worth investigating for testing the general Q&A abilities of the application, but they rarely cover more specific domains and they are very unlikely to cover our specific use cases. Hence, none of them are fine-grained in the ways that we need.

We may have historical data we can adapt into test data, such as saved online chats and phone calls between patients and providers, for our example. Adapting this data into suitable Q&A pairs for testing is labor intensive, although LLMs can accelerate this process. For example, you can feed one or more sessions to a good LLM and ask it to generate Q&A pairs based on the conversation. Everything we will discuss about validating test data, from manual inspection to automated techniques, still applies.

Also, for some domains, we may have good data, but it may have tight restrictions on use, like patient healthcare data subject to privacy laws. Using such data for testing purposes may be disallowed.

For completeness, another use for domain-specific historical data is to [Tune]({{site.glossaryurl}}/#tuning){:target="_glossary"} a &ldquo;generic&rdquo; model to be better at our use cases. The tuned model is then used for testing and production inference. Tuning is not yet a widespread technique for building AI applications, but tuning tools and techniques are becoming easier to use by non experts, so we anticipate that tuning will become more routine over time.

Suppose we don't have enough historical test data for our needs, for whatever reasons. Generation of synthetic data is our tool of choice.

## Synthetic Data Generation and Validation

So far, our narrowly-focused unit benchmark from the [TDD]({{site.baseurl}}/arch-design/tdd/) chapter exercised one behavior, detecting and handling a prescription refill request or any &ldquo;other&rdquo; message. From now on, we will think of this as _two_ units of behavior from the point of view of benchmarking: handing refill requests and handling all other queries for which we don't support special handling.

We will continue to follow this strategy:

1. Identify a new _unit_ (behavior) to implement.
1. Write one or more new unit benchmarks for it, including...
    1. Write [Prompts]({{site.glossaryurl}}/#prompt){:target="_glossary"} for the unit. For the generative AI parts of an application, the prompts become the most important specification of the requirements. (We will explore this more in [Specification-Driven Development]({{site.baseurl}}/advanced-techniques/sdd/).) Several related prompts will be needed per unit:
        1. A prompt for data synthesis.
        1. A prompt for directing runtime behavior (integrated with all the other unit prompts into one runtime prompt).
    1. [Synthetic Data Generation]({{site.glossaryurl}}/#synthetic-data-generation){:target="_glossary"} for a separate data set of Q&A pairs for the benchmark. 
1. Write whatever application logic is required for the unit, including suitable prompts for the generative models involved.

We will focus on the first two steps. The third step will be covered in [A Working Example]({{site.baseurl}}/working-example).

In addition to synthesizing Q&A pairs for the two behaviors we already have, we will add a new unit of behavior and a corresponding benchmark to study detection of prompts where the patient appears to require urgent or emergency care, in which case we want the response to be that the patient should call 911 (in the USA) immediately[^2].

[^2]: Anyone who has called a doctor's office in the USA has heard the automated message, "If this is a medical emergency, please hang up and dial 911."

### Generating the Synthetic Data

The [project repo]({{site.gh_edit_repository}}/){:target="_blank"} contains a tool [`src/tools/unit-benchmark-data-synthesis.py`]({{site.gh_edit_repository}}/blob/main/src/tools/unit-benchmark-data-synthesis.py/){:target="_blank"} that uses an LLM to generate Q&A pairs for the three unit benchmarks, each corresponding to the `prompt` from the following template files[^3]:

[^3]: Recall we said previously that these templates are designed to be compatible with the `llm` CLI tool.

| Unit Benchmark | Template File | 
| :------------- | :------------ | 
| Prescription refill requests | [`synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml){:target="_blank"} |
| Apparent emergencies | [`synthetic-q-and-a_patient-chatbot-emergency-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency-data.yaml){:target="_blank"} |
| Other messages | [`synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml){:target="_blank"} |

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

{: .note}
> **NOTE:** The runtime prompt template used by the ChatBot application, [`patient-chatbot.yaml`]({{site.gh_edit_repository}}/blob/main/src/apps/chatbot/prompts/templates/patient-chatbot.yaml){:target="_blank"}, integrates these three behavioral units and additional behaviors.

### How Many Q&A Pairs Do We Need?

The prompts above ask for _at least 100_ Q&A pairs. This is an arbitrary number. The well-known, broad benchmarks for AI often have thousands to hundreds of thousands of Q&A pairs (or their equivalents). At the same time, benchmarks that focus on more involved tasks, rather than &ldquo;simple&rdquo; questions and answers, will have a relatively smaller number of those tasks, but each one will be much more sophisticated compared to benchmarks using Q&A pairs. Also, the broader the scope of the benchmark, the more Q&A pairs (or task examples) are required. A general high-school math benchmark will need a lot more Q&A pairs than a benchmark focused on Boolean algebra, for example. For now, we will focus on benchmarks that utilize Q&A pairs, returning to more sophisticated benchmarks in [Testing Agents]({{site.baseulr}}/testing-strategies/testing-agents/).

So, 100 is a good starting point, but you should experiment to determine what works best for each unit in your applications. Some points to consider: 

* How complex and varied is the behavior in this unit?
    * Is the behavior so broad that I should consider decomposing it into more fine-grained units?
* For the Q&A pairs available for this unit benchmark (e.g., the ones will generate below):
    * How many of them are very similar and potentially redundant?
        * Be careful of similarities that are more significant than they appear. In our ChatBot example, one drug vs. another might require very different answers to questions that are identical except for the name of the drug. Similarly, a sharp pain in the chest might indicate a medical emergency, more so than a sharp pain in a foot.
    * How well do they cover the possibilities for this unit?
* If I add incrementally more Q&A pairs, at one point do the evaluation results appear to plateau?

Ultimately, we want just enough pairs to give us comprehensive coverage and therefore confidence that the benchmark thoroughly exercises the behavior. Err on the side of too much test data vs. too little, but pay attention to the testing overhead. 

### Thinking about Overhead

What about the cost of running lots of examples through an LLM? Say we have 100 examples in each fine-grained unit benchmark and we have 100 of those benchmarks. How long will each full test run take for those 10,000 invocations and how expensive will they be? We will have to benchmark these runs to answer these questions. If we use a commercial service for model inference during tests, we may need to watch those costs carefully.

For traditional unit testing, our development tools usually only invoke the unit tests associated with the source files that have just changed, saving full test runs for occasional purposes, such as part of the PR (pull request) process in GitHub. This provides near instantaneous feedback. For this to work, the development environment has to know through code analysis which unit tests exercise the code being modified. This optimization not only saves compute resources, it makes the cycle of editing and testing much faster. 

Running unit benchmarks will be much slower, especially for more sophisticated agents and when using larger models for inference. Using local inference saves costs during testing vs. paying for an inference service, but it can be slower than using an optimized service.

In the discussion of [using benchmarks as automated tests]({{site.baseurl}}/working-example/#automated-testing-practical-enhancements), we use a strategy of [sampling the Q&A pairs in unit tests]({{site.baseurl}}/working-example/#dealing-with-slow-and-expensive-inference) to make them run faster, with the downside of losing some coverage. The integration test suite runs the same tests with all pairs (plus other tests). It could also use the version of the model that will be deployed to production, but if this is still too expensive, consider running the same tests with the production model as part of the acceptance tests, which ultimate decide when features are &ldquo;done&rdquo;.

For incremental development cycles, more fine-grained units (i.e., use cases) will be better, as they will need fewer Q&A pairs for coverage. Currently, there isn't an automated way for your development environment or your testing framework to know which unit benchmarks to run while you are working on a particular unit of behavior. However, the CLIs for all testing tools let you specify individual test files to run.

To further reduce testing time and costs, experiment with model choices, too. Pick a model from a model family with a  parameter count that gives excellent performance in production deployments. Then look for a version that works sufficiently well during development, but with less overhead. For example, a [Quantized]({{site.glossaryurl}}/#quantization){:target="_glossary"} version of the production model or smaller parameter-count versions in the same model family. You could use models from different families, but you will have wider variation in behavior between testing and production, making your testing a less reliable predictor of production behavior.

## Running the Data Synthesis Tool

Try running this tool yourself using `make`. If you haven't done so, follow the setup instructions in the [Try It Yourself!]({{site.baseurl}}/arch-design/tdd/#try-it-yourself) section in the [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/) chapter. The instructions are also the project repository's [README]({{site.gh_edit_repository}}/){:target="_blank"}. 

Once setup, here is the `make` command to run the data synthesis tool with the default model, `ollama_chat/gpt-oss:20b`:

```shell
make run-unit-benchmark-data-synthesis
```

After some setup, the following command is executed:

```shell
cd src && time uv run tools/unit-benchmark-data-synthesis.py \
  --model ollama_chat/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir tools/prompts/templates \
  --data-dir .../output/ollama_chat/gpt-oss_20b/data \
  --log-file .../output/ollama_chat/gpt-oss_20b/logs/TIMESTAMP/unit-benchmark-data-synthesis.log
```

Where `TIMESTAMP` is of the form `YYYYMMDD-HHMMSS` and the values passed for `--data-dir` and `--log-file` are absolute paths.

Recall that a different model can be specified, i.e., `make MODEL=ollama_chat/llama3.2:3B`run-unit-benchmark-data-synthesis`. (See the project README and also in [Running the TDD Tool]({{site.baseurl}}/arch-design/tdd/#running-the-tdd-tool).) 

Note the arguments for where log output is captured (`--log-file`) and the data Q&A pairs files are written (`--data-dir`). Specifically, the following data files are written, examples of which can be found [in the repository]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat){:target="_blank"} (for both `gpt-oss:20b` and `llama3.2:3B`):

| Synthetic Data File | `gpt-oss:20b` | `llama3.2:3B` |
| :---- | :---- | :---- |
| `synthetic-q-and-a_patient-chatbot-emergency-data.jsonl` | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-emergency-data.jsonl){:target="_blank"} | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data.jsonl){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.jsonl` | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.jsonl){:target="_blank"} | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.jsonl){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data.jsonl` | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.jsonl){:target="_blank"} | [example]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.jsonl){:target="_blank"} |

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

For the more general case, where the output isn't as deterministic, but more [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"}, we have to lean on other techniques.

One of the best techniques is to rely on a [Teacher Model]({{site.glossaryurl}}/#teacher-model){:target="_glossary"} to evaluate synthetic data based on a few criteria:

* Is the question relevant to the purpose of this test?
* If the question is relevant, is the supplied answer correct?

We examine this process in [LLM as a Judge]({{site.baseurl}}/testing-strategies/LLM-as-a-Judge). Other techniques we will explore include [External Tool Verification]({{site.baseurl}}/external-verification/), and [Statistical Evaluation]({{site.baseurl}}/statistical-tests/).

## Adapting Third-Party, Public, Domain-Specific Benchmarks

While the best-known benchmarks tend to be too broad in scope and generic for our needs, they are good sources of ideas and sometimes actually data. There is also a growing set of domain-specific benchmarks that could provide good starting points for test benchmarks.

Note that benchmarks fall into the broad category of [Evaluation]({{site.glossaryurl}}/#evaluation){:target="_glossary"}, including data sets and tools for safety purposes. Many of the data sets and tools discussed below use this term, so we call it out here for clarity.

Here is a list of some domain-specific benchmarks that we know of. [Let us know]({{site.baseurl}}/) of any others you find useful, so we can add them here.

### General Collections of Domain-Specific Evaluations

* [EvalEval](https://evalevalai.com/){:target="ee"} ([Blog post](https://evalevalai.com/infrastructure/2026/02/17/everyevalever-launch/){:target="ee-blog"}, [GitHub organization](https://github.com/evaleval){:target="ee-gh"}) is a research coalition on _evaluating evaluations_. [Every Eval Ever](https://github.com/evaleval/every_eval_ever){:target="eee-gh"}, is defining a shared schema for evaluations and a crowdsourced database of AI evaluations.
* [Weval](https://weval.org/sandbox){:target="weval"} from the [Collective Intelligence Project](https://www.cip.org/){:target="cip"}, is a community-driven collection of domain-specific evaluations, designed to allow non-experts to contribute and use evaluation suites relevant to their needs. 
* [ClairBot](https://clair.bot/){:target="clairbot"} from the Responsible AI Team at [Ekimetrics](https://ekimetrics.com/){:target="ekimetrics"} is a research project that compares several model responses for domain-specific questions, where each of the models has been tuned for a particular domain, in this case ad serving, laws and regulations, and social sciences and ethics.
* [HELM Enterprise Benchmark](https://github.com/IBM/helm-enterprise-benchmark){:target="heb"} is an enterprise benchmark framework for LLM evaluation. It extends [HELM](https://crfm.stanford.edu/helm/lite/latest/){:target="helm"}, an open-source benchmark framework developed by [Stanford CRFM](https://crfm.stanford.edu/helm/lite/latest/){:target="crfm"}, to enable users evaluate LLMs with domain-specific data sets such as finance, legal, climate, and cybersecurity. 

### Education

* The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}.

### Finance

Benchmarks for finance applications.

* Patronus AI [FinanceBench](https://github.com/patronus-ai/financebench){:target="finance-bench"}
* [FIBEN Benchmark](https://github.com/IBM/fiben-benchmark){:target="_blank"}.

### Healthcare 

Benchmarks for testing health-related use cases.

* OpenAI [Healthbench](https://openai.com/index/healthbench/){:target="oai-hb"}
* Stanford HELM for healthcare, [MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/){:target="medhelm"}
* Stanford ML's [MedAgentBench](https://stanfordmlgroup.github.io/projects/medagentbench/){:target="mab"} an virtual environment and benchmark suite for assessing the performance of LLMs in the context of _electronic health records_ (EHR).

### Industrial Systems

I.e., manufacturing, shipping, etc.

* FailureSensorIQ
  * [paper](https://arxiv.org/abs/2506.03278){:target="_blank"} &ldquo;... a novel Multi-Choice Question-Answering (MCQA) benchmarking system designed to assess the ability of Large Language Models (LLMs) to reason and understand complex, domain-specific scenarios in Industry 4.0. Unlike traditional QA benchmarks, our system focuses on multiple aspects of reasoning through failure modes, sensor data, and the relationships between them across various industrial assets.&rdquo;
  * [GitHub](https://github.com/IBM/FailureSensorIQ){:target="_blank"}
  * [Data set](https://huggingface.co/datasets/ibm-research/AssetOpsBench){:target="_blank"}

### Legal

* Stanford [LegalBench](https://hazyresearch.stanford.edu/legalbench/){:target="legalbench"} ([paper](https://arxiv.org/abs/2308.11462){:target="arxiv"})

### Software Engineering

Benchmarks for testing software engineering use cases.

* Open AI [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/){:target="oai-swe"}

Benchmarks for software systems performance and reliability include the following:

* The [Llama Stack](https://github.com/llamastack/llama-stack/){:target="ls"} project's [Kubernetes Benchmark](https://github.com/llamastack/llama-stack/tree/main/benchmarking/k8s-benchmark){:target="ls-kb"} suite.


### Other Domains?

What other domains would you like to see here?

<a id="other-tools"/>

## Evaluating Benchmark Quality

See [What Makes a Good AI Benchmark?](https://hai.stanford.edu/policy/what-makes-a-good-ai-benchmark){:target="hai"} from Stanford's Human-Centered Artificial Intelligence project for a careful analysis of the qualities of good benchmarks, along with assessments of many well-known, public benchmarks. See also their [BetterBench](https://betterbench.stanford.edu/){:target="bb"} repository of assessments.

Some of the criteria pertain to documentation, ease of adoption, and feedback mechanisms, which may be less important for small-scale and especially private benchmarks, like _unit benchmarks_ discussed here. Other criteria are more applicable, such as clearly defining the goals of the benchmark, how those goals are implemented by the benchmark, how to interpret the results, how involved were domain experts in constructing the benchmark, etc.

## Other Tools for Unit Benchmarks

We are using relatively-simple, custom tools for our examples, which work well so far, but may not be as flexible for real-world use in large development teams with diverse skill sets and large evaluation suites. Here are some additional tools to explore. 

Additional tools that have some data synthesis and evaluation capabilities are discussed in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/#other-tools) and [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/#other-tools).

See also [A Working Example]({{site.baseurl}}/working-example) for a discussion of integrating new tools into existing frameworks, like [PyTest](https://docs.pytest.org/en/stable/){:target="_blank"}.

### Adding Additional Sources of Input for Synthetic Data

So far, we have relied on the innate knowledge of the teacher model to generate data. For more sophisticated use cases, such as those highly specific to custom domains, this assumption won't work. In those cases, we need to supplement the model's innate knowledge with supplemental information. 

If this information can be provided concisely as extra context in the prompt, that is a simple way to proceed. More likely, a solution like [Retrieval-Augmented Generation]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"} (RAG) will be necessary.

If you are using an inference service with built-in RAG capabilities, like OpenAI, Anthropic, Bedrock, etc., then the `litellm` invocations we have been using can be modified to use RAG. See the documentation for [`/rag/ingest`](https://docs.litellm.ai/docs/rag_ingest){:target="litellm"} and [`/rag/query`](https://docs.litellm.ai/docs/rag_query){:target="litellm"}. 

{: .warning}
> **WARNING:** Be careful about uploading sensitive, non-public information to hosted services. Most organizations prohibit this activity.

Some of the custom documents might be in formats that are not ideal for inference, like PDF or Word. (The more advanced models have some capabilities for working with such documents.) In this case, it might be desirable to parse the documents into text-only formats, like Markdown, and use those instead. 

A number of tools exist for this purpose. For example, [Docling](https://docling-project.github.io/docling/){:target="docling"} is a powerful tool for parsing many different data formats, with special attention to extracting useful information from tables and diagrams, which are common in technical papers. Hence, your synthetic data pipeline that ingests proprietary data might first parse non-text files and use the outputs for RAG storage. 

### Other Tools for Synthetic Data Generation

If you use synthetic data generation a lot in your organization, it will become necessary to understand some of the potential complexities that you might encounter. 

#### A Survey of Data Synthesis Techniques

[Synthetic Data Generation Using Large Language Models: Advances in Text and Code](https://arxiv.org/abs/2503.14023){:target="_blank"} surveys techniques that use LLMs, like we are doing. 

#### Synthetic Data Kit

Meta's Synthetic Data Kit ([`synthetic-data-kit`](https://github.com/meta-llama/synthetic-data-kit/){:target="_blank"}) focuses on larger-scale data synthesis and processing (such as translating between formats), especially for model [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} with Llama models. It supports text, video, and multimodal data.

Synthetic Data Kit uses one or more documents you specify as sources of information for data generation. It can generate different kinds of data sets: Q&A pairs, Q&A pairs with _chain of thought_ (CoT) reasoning, and summaries. It also uses the [vLLM](https://docs.vllm.ai/){:target="vllm"} inference engine, which is a popular production-scale server and experimental support for Intel and Apple Silicon CPUs. 

#### InstructLab

[InstructLab](https://instructlab.ai){:target="instructlab"} is a project started by [IBM Research](https://research.ibm.com){:target="ibm"} and developed by [RedHat](https://redhat.com){:target="redhat"}. Among its features is synthetic data generation. See the [References]({{site.referencesurl}}/) and [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/) for more details.

#### Older Synthetic Data Tools

[Nine Open-Source Tools to Generate Synthetic Data](https://opendatascience.com/9-open-source-tools-to-generate-synthetic-data/){:target="_blank"} lists several tools that use different approaches for data generation, serving different purposes. For example, several use [Generative Adversarial Networks]({{site.glossaryurl}}/#generative-adversarial-networks){:target="_glossary"}, a technique most popular in the late 2010s.

### More Advanced Benchmark and Evaluation Tools

Similarly, there are other general-purpose tools for authoring, managing, and running benchmarks and evaluations, many with more sophisticated capabilities than we can discuss here.. 

#### PleurAI Intellagent

[Intellagent](https://github.com/plurai-ai/intellagent){:target="_blank"} demonstrates some advanced techniques developed by [Plurai](https://www.plurai.ai/){:target="_blank"} for understanding a project's requirements and interdependencies, then using this _graph_ of information to generate synthetic data sets and tests.

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

## Experiments to Try

There is a lot to explore here:

* Study the Q&A pairs generated. How might you refine the prompts to be more effective at generating good data?
* One way to assist studying the data is to ask the model to also generate a _confidence_ rating for how good it thinks the Q&A pair is for the target unit benchmark and how good it thinks the answer is for the question. Try this experiment using a scale of 1-5, where one is low confidence and five is high confidence. Make sure to also ask for an explanation for why it provided that rating. Review the Q&A pairs with low confidence scores. Should they be discarded automatically below a certain threshold? Do they instead suggest good corner cases for further exploration? If there are a lot of low confidence pairs in the output, could the prompt be improved to provide better clarity about the desired output data set?  
* Try different runs where you vary the requested number of Q&A pairs in the prompts from tens of pairs up to many hundreds. What are the impacts for compute resources and time required? Look through the data sets. Can you develop an intuition about which sizes are sufficient large for good coverage? Is there an approximate size beyond which lots of redundancy is apparent? Save these outputs for revisiting in subsequent chapters. 
* Add more unit benchmarks for new behaviors. For example, explore queries about appointments or requests for referrals to specialists.
* Try other models. See how bigger and smaller models perform, especially within the same &ldquo;family&rdquo;.
* How might you modify the example to handle a patient prompt that includes a refill request and other content that requires a response? We have assumed that a prompt with a refill request contains no other content that requires separate handling. In other words, our _classifier_ only returns one label for the prompt. What if it returned a list of labels and a _confidence_ score for each one? Because of _cross pollination_, all the prompts used to generate Q&A pairs for all the unit benchmarks should be modified to support one or more responses (e.g., the requested JSONL format of the &ldquo;answers&rdquo;). However, treat testing for this specific situation as a new unit benchmark.
* For all of the above, note the resource requirements, such as execution times, hardware resources required for the models, service costs if you use an inference service, etc.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/).

---
