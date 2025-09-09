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

Currently, when testing AI applications with their nondeterministic model behaviors, an ad-hoc combination of existing [Benchmarks]({{site.glossaryurl}}/#benchmark) and ad hoc manual testing are used. This is a step backwards from the rigor of testing practices for non-AI applications, where deterministic, repeatable, and automated tests are the norm, covering [Unit Testing]({{site.glossaryurl}}/#unit-test) for fine-grained behavior, [Integration Testing]({{site.glossaryurl}}/#integration-test) for verifying that units work correctly together, and [Acceptance Testing]({{site.glossaryurl}}/#acceptance-test) for final validation that the [Behaviors]({{site.glossaryurl}}/#behavior) of [Features]({{site.glossaryurl}}/#feature) and [Use Cases]({{site.glossaryurl}}/#use-case) are correctly implemented.

_Unit benchmarks_ are an adaptation of benchmarking tools and techniques for the same kinds of focused tests that traditional tests provide, this time for AI components.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. We can adapt benchmark concepts to be appropriate for unit, integration, and acceptance testing of AI components.
> 2. Benchmarks require good datasets with prompts designed to probe how the model behaves in a certain area of interest, along with responses that represent acceptable answers. We will use the term question and answer (Q&A) pairs for these prompts and responses, following conventional practice.[^1]
> 3. A [Teacher Model]({{site.glossaryurl}}/#teacher-model) can be used as part of a process of generating synthetic Q&A pairs, and also validating their quality.
> 4. You will have to experiment to determine a suitable number of Q&A pairs for good test coverage.
> 4. Benchmark tools can be called from tests written using Python test frameworks, like [PyTest](https://docs.pytest.org/en/stable/){:target="_blank"}, so they are executed as part of an application's test suites.
> 5. There are many third-party, production-grade tools you can use for evaluation and benchmark creation and execution.

[^1]: Not all benchmarks use Q&A pair datasets like this. For example, some use a specially trained model to evaluate responses. We will only consider benchmarks that work with Q&A pairs.

Benchmarks are a popular tool for evaluating how well models perform in &ldquo;categories&rdquo; of activity with broad scope, like code generation, Q&A (question and answer sessions), instruction following, Mathematics, avoiding hate speech, avoiding hallucinations, etc. A typical benchmark attempts to provide a wide range of examples across the category and report a single number for the evaluation, usually scaled as a percentage of passing results between 0 and 100%. 

In contrast, good software tests are very specific, examining one specific [Behavior]({{site.glossaryurl}}/#behavior), while keeping everything else _invariant_. The scope of the test will vary from fine grained for unit tests, to unit and component combinations for integration tests, to whole-application for acceptance tests.

Why not write more focused benchmarks? In other words, embrace the nondeterminism of models and use the benchmark concept, just focused narrowly for each particular scope?

## Revisiting our TDD Example

In [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/), we discussed a hypothetical healthcare ChatBot and wrote an informal [unit benchmark]({{site.baseurl}}/arch-design/tdd/#tdd-and-generative-ai) for it. We created a handful of Q&A pairs for testing, but we also remarked that this manual curation is not scalable and it is error prone, as it is difficult to cover all the ways someone might request a refill, including potential corner cases, such as ambiguous messages.

So, we need a better dataset of Q&A pairs. A real healthcare organization will likely have many patient &ldquo;portal&rdquo; conversations logged that can be used for this purpose. They might also be used to [Tune]({{site.glossaryurl}}/#tune) a &ldquo;generic&rdquo; model to be better at healthcare Q&A. Some manual curation of the data will likely be necessary, but LLMs can also be very useful for analyzing these logs and extracting useful content.

Generating synthetic data is another tool, which we will explore in depth below. First, let's discuss a few other considerations for these tests we are building.

What about the cost of running lots of examples through your LLM? Say you have 100 examples in each fine-grained unit benchmark and you have 100 of those benchmarks. How long will each full test run take for those 10,000 invocations and how expensive will they be? You will have to benchmark these runs to answer these questions. If you use a commercial service for model inference during your tests, you'll need to watch those costs.

For traditional unit testing, your development environment usually only invokes the unit tests associated with the source files that have just changed, saving full test runs for occasional purposes, such as part of the pull request process in your version control system. Runs of the integration and acceptance tests, which are relatively slow and expensive, are typically run a few times per day. We can develop a similar strategy here, where only a subset of our unit benchmarks are invoked for incremental updates, while the full suite is only invoked occasionally. 

To reduce testing time and costs, you will want to experiment with model choices, both for the production deployments and for development purposes. For example, if you have picked a production version of a model, there may be smaller versions you can use successfully during development. You might trade off the quality of responses, but perhaps the results during testing will be &ldquo;good enough&rdquo;. Since acceptance tests are designed to confirm that a feature is working, use the full production models for those tests. Another benefit of using smaller models is the ability to do inference on development machines, with sufficient compute capability, rather than having to call a inference service for every invocation, which is slower and more expensive.

Back to the TDD example, while there are a many available ChatBot benchmarks, they tend to be very broad, covering overall conversational abilities. Rarely do they cover specific domains, and none are fine-grained in the ways that we need.

In contrast, our narrowly-focused unit benchmark exercised one behavior, a prescription refill request or &ldquo;other&rdquo; message, and left other behaviors to be exercised by separate unit benchmarks. For each of those unit benchmarks, a separate suite of Q&A pairs is created. For example, in this section, we will add a new benchmark data set for detecting situations where the patient appears to require urgent or emergency care, in which case we want the response to be that they should call 911 (in the USA) immediately[^1].

[^1]: Anyone who has called a doctor's office in the USA has heard the automated message, "If this is a medical emergency, please hang up and dial 911."

Let's look at more systematic approaches to creating and executing unit benchmarks:

1. Synthetic data generation and validation.
2. Integration into a standard testing framework.

## Synthetic Data Generation and Validation

In our TDD example, we wrote the Q&A pairs by hand for our unit benchmark. This has two disadvantages:

1. It is time consuming, so it doesn't scale well for large applications.
2. Covering the whole &ldquo;space&rdquo; of possible questions and answers is difficult and error prone, especially for edge cases.

The solution is to use an LLM to generate a lot of diverse Q&A pairs. We will need a way to ensure that generated data is of good quality, which we will explore.

### Generating the Synthetic Data

The [project repo]({{site.gh_edit_repository}}/){:target="_blank"} contains a tool [`src/scripts/unit-benchmark-data-synthesis.py`]({{site.gh_edit_repository}}/blob/main/src/scripts/unit-benchmark-data-synthesis.py/){:target="_blank"} that uses an LLM to generate Q&A pairs for three unit benchmarks, each corresponding to the `prompt` from the following `llm`-compatible template files:

| Unit Benchmark | Template File | 
| :------------- | :------------ | 
| Prescription refill requests | [`synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml){:target="_blank"} |
| Apparent emergencies | [`synthetic-q-and-a_patient-chatbot-emergency-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency-data.yaml){:target="_blank"} |
| Other messages | [`synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`]({{site.gh_edit_repository}}/blob/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml){:target="_blank"} |

The _emergency_ use case attempts to detect when the patient needs urgent or emergency care, such as saying she is in extreme pain or she has trouble breathing, in which case the patient is directed to call 911 (in the US) instead.

Here is the prompt for that use case:

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

The other two prompts are similar.

### How Many Q&A Pairs Do We Need?

The prompts above ask for _at least 100_ Q&A pairs. This is an arbitrary number. The well-known, broad benchmarks for AI typically often have many thousands of Q&A pairs (or their equivalents).

For fine-grained _unit_ benchmarks, a suitable number could vary between tens of pairs, for simpler cases, to hundreds of pairs on average, to thousands of pairs for more complex test scenarios. It could also vary from one unit benchmark to another. 

There aren't any hard and fast rules; you will have to experiment to determine what works best for you. More specifically, what number of pairs gives you sufficient confidence for _this particular_ benchmark? 

Because the corresponding _integration benchmarks_ and _acceptance benchmarks_ have broader scope, by design, they will usually require larger testing datasets.

### Running the Data Synthesis Tool

You can run this tool yourself using `make`. See the [Try It Yourself!]({{site.baseurl}}/arch-design/tdd/#try-it-yourself) section in the chapter on [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/) for details on setting up the tools. See also the project repo's [README]({{site.gh_edit_repository}}/){:target="_blank"}). Here is the `make` command to run the data synthesis tool with the default model, `ollama/gpt-oss:20b`:

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

A different model could be specified, as discussed in the README and also in [Running the TDD Tool]({{site.baseurl}}/arch-design/tdd/#running-the-tdd-tool). Note the arguments for where output is captured (`--output`) and the data Q&A pairs files are written (`--data`). Specifically, the following data files are written, examples of which can be found [here](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama){:target="_blank"} (for both `gpt-oss:20b` and `llama3.2:3B`):

| Synthetic Data File | `gpt-oss:20b` | `llama3.2:3B` |
| :---- | :---- | :---- |
| `synthetic-q-and-a_patient-chatbot-emergency-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-emergency-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data.json){:target="_blank"} |

They cover three _unit-benchmarks_:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should stop using the ChatBot and call 911 (in the US) immediately.
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

Note that the answer has the identified prescription (placeholder `_P_`) and body part found in the question.

Examples from our runs can be found in the [`src/data/examples/`]({{site.gh_edit_repository}}/blob/main/src/data/examples/){:target="_blank"} directory in the project repo for `gpt-oss:20b`, `llama3.2:3B`, and `llama3.3:70b`.

Each of these data files are generated with a single inference invocation, using the prompt in the corresponding template file discussed above. In some cases, output Q&A pairs don't actually fit the use case. There are times when a _prescription refill_ Q&A pair is labeled as an emergency, times when an _emergency_ Q&A pair is labeled a _refill_, etc. This is more likely to happen with smaller models. We will discuss this topic in [LLM as a Judge]({{site.baseurl}}/testing-strategies/LLM-as-a-Judge), when we discuss methods for validating the quality of the synthetic Q&A pairs.

Finally, even though the system prompt emphasizes that we want _at least_ 100 Q&A pairs, we rarely got that many in the actual results with `llama3.2:3B`, while using `gpt-oss:20b` over delivered. This is probably more of a quick of using a small model than a reflection of any &ldquo;defects&rdquo; or advantages of one model architecture vs. the other.

## Evaluating the Synthetic Data

In the TDD example, we used a system prompt to cause the LLM to _almost_ always return a deterministic answer for the two cases, a prescription refill request and everything else. When you have a design like this, it simplifies evaluating the Q&A pair. Essentially, we ask the teacher model, "For each question, is the corresponding answer correct?"

In the more general case, where the output isn't as deterministic, but more [Stochastic]({{site.glossaryurl}}/#stochastic), we have to lean on other techniques.

One of these techniques is rely on a [Teacher Model]({{site.glossaryurl}}/#teacher-model) to evaluate synthetic data on a few criteria:

* Is the question relevant to the purpose of this test?
* If the question is relevant, is the supplied answer correct?

We examine this process in [LLM as a Judge]({{site.baseurl}}/testing-strategies/LLM-as-a-Judge). Other techniques we will explore include [External Tool Verification]({{site.baseurl}}/external-verification/), and [Statistical Evaluation]({{site.baseurl}}/statistical-tests/).

## Adapting Third-Party, Public, Domain-Specific Benchmarks

While the best-known benchmarks tend to be broad in scope, there is a growing set of domain-specific benchmarks that could provide a good starting point for your more-specific benchmarks.

Here is a partial list of some domain-specific benchmarks that we know of. [Let us know

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

* Stanford [LegalBench](https://hazyresearch.stanford.edu/legalbench/){:target="legalbench"} ([paper](https://arxiv.org/abs/2308.11462){:target="arxiv"})

### Education

* The [AI for Education](https://ai-for-education.org/){:target="ai4e"} organization provides lots of useful guidance on how to evaluate AI for different education use cases and select benchmarks for them. See also their [Hugging Face page](https://huggingface.co/AI-for-Education){:target="ai4e-hf"}.

### Other Domains?

What other domains should we list here?

## Integration of Unit Benchmarks into Standard Testing Frameworks

TODO. We will fill in this section with tips on adding our testing tools for:

* Ad hoc execution in your development workflows.
* Automation using PyTest and other Python test frameworks.

[Contributions are welcome!]({{site.baseurl}}/contributing). See this [issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/21){:target="_blank"} for details.

## More Advanced Benchmark and Evaluation Tools

We are still using custom tools for our examples, which work well so far, but may not be as flexible for real-world use in large development teams with large and diverse evaluation suites. Here are a few tools to explore. Additional tools are discussed in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/).

TODO: We intend to provide more coverage of them as this user guide evolves. [Contributions are welcome!]({{site.baseurl}}/contributing). See this [issue](https://github.com/The-AI-Alliance/ai-application-testing/issues/22){:target="_blank"} for details.

### PleurAI Intellagent

See [Intellagent](https://github.com/plurai-ai/intellagent) for some advanced techniques for synthetic dataset and test generation.

TODO: More details...

### LM Evaluation Harness Installation

[LM Evaluation Harness](https://www.eleuther.ai/projects/large-language-model-evaluation){:target="lm-site"} is a de facto standard tool suite for defining and running _evaluations_.

It also supports execution of evaluations written using [Unitxt](#unitxt).

### Unitxt

[Unitxt](https://www.unitxt.ai){:target="unitxt"} makes it easy to generate evaluations with minimal code.

Some examples using `unitxt` are available in the [IBM Granite Community](https://github.com/ibm-granite-community){:target="igc"}, e.g., in the [Granite &ldquo;Snack&rdquo; Cookbook](https://github.com/ibm-granite-community/granite-snack-cookbook){:target="igc-snack"} repo. See the [`recipes/Evaluation`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation){:target="igc-snack-eval"} folder. These examples only require running [Jupyter](https://jupyter.org/){:target="jupyter"} locally, because all inference is done remotely by the community's back-end services. Here are the specific Jupyter notebooks:

* [`Unitxt_Quick_Start.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Quick_Start.ipynb){:target="igc-snack-eval1"} - A quick introduction to `unitxt`.
* [`Unitxt_Demo_Strategies.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Demo_Strategies.ipynb){:target="igc-snack-eval2"} - Various ways to use `unitxt`.
* [`Unitxt_Granite_as_Judge.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Granite_as_Judge.ipynb){:target="igc-snack-eval3"} - Using `unitxt` to drive the _LLM as a judge_ pattern.

#### Using LM Evaluation Harness and Unitxt Together

Start on this [Unitxt page](https://www.unitxt.ai/en/latest/docs/lm_eval.html){:target="unitxt-lm-eval"}. Then look at the [`unitxt` tasks](https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/unitxt){:target="unitxt-lm-eval2"} described in the [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness){:target="lm-eval"} repo.

### Final Thoughts on Advanced Benchmark and Evaluation Tools

See also [Tuning Tools]({{site.baseurl}}/testing-strategies/from-testing-to-tuning/#tuning-tools) in [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning/).

Be careful to check the licenses for any benchmarks or tools you use, as some of them may have restrictions on use. Also, you can find many proprietary benchmarks that might be worth the investment for your purposes. See also the [references]({{site.baseurl}}/references) for related resources.

[Let us know]({{site.baseurl}}/contributing/#join-us) of any other tools that you think we should discuss here!

## Experiments to Try

There is a lot to explore here:

* Study the Q&A pairs generated. How might you refine the prompts to be more effective at generating good data?
* One way to assist studying the data is to ask the model to also generate a _confidence_ rating for how good it thinks the Q&A pair is for the target unit benchmark and how good it thinks the answer is for the question. Use a scale of 1-5, where one is low confidence and five is high confidence. Also ask for an explanation for why it provided that rating. Review the Q&A pairs with low confidence scores. Should they be discarded automatically below a certain threshold? Do they instead suggest good corner cases for further exploration? If there are a lot of low confidence pairs in the output, could the prompt be improved to provide better clarity about the desired output dataset? Note: the more output you generate, the more time and resources will be required for the data synthesis process. We will revisit this idea in [Statistical Evaluation]({{site.baseurl}}/testing-strategies/statistical-tests/). 
* Do different runs where you vary the number of Q&A pairs requested from tens of pairs up to many hundreds. What are the impacts for compute resources and time required? Look through the data sets. Can you develop an intuition about which sizes are sufficient large for good coverage? Is there an approximate size beyond which lots of redundancy is apparent? Save these outputs for revisiting in subsequent chapters.
* Add more unit benchmarks for new use cases. For example, explore requests for referrals to specialists.
* Try other models. See how bigger and smaller models perform, especially within the same &ldquo;family&rdquo;, like Llama.
* How might you modify the example to handle a patient prompt that includes a refill request and other content that requires a response? We have assumed that a prompt with a refill request contains no other content that requires separate handling. In other words, our _classifier_ only returns one label for the prompt. What if it returned a list of labels and a _confidence_ score for each?
* For all of the above, note the resource requirements, such as execution times, hardware resources required for the models, service costs if you use an inference service, etc.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/).

---
