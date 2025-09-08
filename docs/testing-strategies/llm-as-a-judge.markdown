---
layout: default
title: LLM as a Judge
nav_order: 320
parent: Testing Strategies and Techniques
has_children: false
---

# LLM as a Judge

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

In _LLM as a Judge_, a separate model serves as a _judge_ of the quality of data or model outputs. In this guide, we are using a judge to evaluate the quality of the Q&A pairs we synthesized for [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark), as discussed in the [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks) chapter. An LLM could also be used to judge model outputs in a production setting, as a &ldquo;sanity check&rdquo; before returning them to a user or performing further processing.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Human evaluation of synthetic data and production model responses don't scale and are error prone. 
> 1. Let one or more &ldquo;smart&rdquo; _teacher models_ do the judging.
> 1. Small models don't make very good judges, but using more than one with _majority wins_ or _average scores_ provides more resiliency and can be used when a single large, expensive model isn't a viable choice.

Normally, a chosen judge model is considered very &ldquo;smart&rdquo; or capable for evaluating the content in question. It may also be large and expensive to use or otherwise considered not suitable for production use in the application. As for one-time data synthesis, one-time judging of the data can be a cost-effective way to maximize application quality while keeping production costs as low as possible.

Since diversity of perspectives is important here, you would normally not use the _same_ model as a judge that was used to synthesize data! However, we'll see below that sometimes the same model will rate a Q&A pair poorly that it generated itself!

Like using an LLM to synthesize benchmark data, using an LLM to judge content addresses the limitations of human evaluation: expensive, not scalable, and error prone.

## Scoring

The judge could issue a &ldquo;pass/fail&rdquo; ruling, but given the somewhat subjective nature of the task, a rating can be more informative. In our example below, we will ask the judge to rate the quality of a Q&A pair from one to five, from bad to excellent, and to also provide a _reason_ for the judgement. 

So, when using LLM as a judge as part of the process of creating unit benchmark datasets, it is a good idea for _humans_ to review of any ratings below four or five. Is the rating accurate? If a datum scored poorly, should it be discarded? If you have a lot of poorly-rated data, should you review and refine how it was created in the first place? Perhaps the prompts used for synthetic data generation could be more precise and descriptive about the expectations for the data?

Alternatively, do low-scoring data represent good corner cases, such as ambiguous input, that might be useful for developing special handling of and testing for such corner cases? 

This suggests a potential design refinement in our healthcare ChatBot, which we suggested in the [Unit Benchmark's]({{site.baseurl}}/testing-strategies/unit-benchmarks/) section [Experiments to Try]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try). Suppose when we do data generation, we also ask the model to  provide a _confidence_ rating for how good it thinks the Q&A pair is for the target unit benchmark and how good it thinks the answer is for the question. We also suggested asking for an explanation for why the model provided this rating.

The judge could compare its rating and explanation with the one the generation model provided. There is a catch to be wary of, however; _don't_ pass the confidence rating and explanation to the judge _before_ it has rendered its opinion. Otherwise, you will bias its answer!

This exercise can also be a good way to explore potential corner cases, such as ambiguous prompts, and how to handle them effectively.

## Panel of LLMs as Judges

Suppose we use a _panel_ of judges instead of a single judge? For pass/fail verdicts, the majority vote would prevail. For a ratings system, the average of the judges' ratings could be more accurate and resilient than the opinion of a single judge.

This approach is a good way to leverage smaller, more cost-effective models, rather than rely on a large, potentially expensive model. If you don't have the budget to use a third-party service's large models (e.g., from OpenAI or Anthropic) nor can you run a large, open-access model in your environment, like the larger Llama models, using a panel of small models can provide good results economically. A panel of diverse models helps compensate for the weaknesses of any single, small model.

## Evaluating the Synthetic Data

In [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/), we generated synthetic data, but left the question open how we can validate its quality, other than relying solely on manual inspection (which is still very useful!). LLM as a judge is our automation tool for this purpose.

The [project repo]({{site.gh_edit_repository}}/){:target="_blank"} contains a tool [`src/scripts/unit-benchmark-data-validation.py`]({{site.gh_edit_repository}}/blob/main/src/scripts/unit-benchmark-data-validation.py/){:target="_blank"} that uses an LLM to rate each synthetic Q&A pair for the three unit benchmarks we generated previously, which are listed in a table in [Running the Data Synthesis Tool]({{site.baseurl}}/testing-strategies/unit-benchmarks/#running-the-data-synthesis-tool).

In this case, we don't use a separate prompt (stored in a template file) for each unit benchmark. Instead, one prompt works for all cases, as it doesn't mention the benchmark details; it just asks the LLM to judge if the answer is suitable for the question in the Q&A pair. It returns a rating, 1-5, as discussed above, and its reasoning for the rating.

The template file used is `synthetic-q-and-a_patient-chatbot-data-validation.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml)

### Running the Data Validation Tool

Although we said above that it is better to pick a different model for a judge, we used the same models that were used in data synthesis, for simplicity. 

```shell
make run-unit-benchmark-data-validation
```

After some setup, the following command is executed, which uses the same arguments we used for data synthesis:

```shell
time uv run src/scripts/unit-benchmark-data-validation.py \
  --model ollama/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir src/prompts/templates \
  --output temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out \
  --data temp/output/ollama/gpt-oss_20b/data
```

In this case, the `--data` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file will be written back to the same directory. We saved the output of example runs:

| Validation Data File | `gpt-oss:20b` | `llama3.2:3B` |
| :---- | :---- | :---- |
| `synthetic-q-and-a_patient-chatbot-emergency-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json){:target="_blank"} |

These files rate each Q&A pair from 1 (bad) to 5 (great) and provide reasoning for each rating.
Also, summary statistics are written by the tool to `stdout` and to the output file `temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out`. We show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. (For simplicity, we used the same `gpt-oss:20b` model as the _teacher_ that we used for generation). Here are the statistics for a few test runs:

**`gpt-oss:20b`**

| Synthetic Q&A Pairs File                                                |    1   |    2   |    3   |    4   |    5    | Total   |
| :------                                                                 | -----: | -----: | -----: | -----: | ------: | ------: |
| `synthetic-q-and-a_patient-chatbot-emergency-data.json`                 |    0   |    4   |    7   |   12   |   168   |   191   |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data.json`      |    0   |    0   |    0   |    0   |   108   |   108   |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json`  |    2   |    2   |    0   |    1   |   168   |   173   |
| **Totals:**                                                             |  **2** |  **6** |  **7** | **13** | **444** | **472** |

Total count: 475 (includes errors), total errors: 3

**`llama3.2:3B`**

| Synthetic Q&A Pairs File                                                |    1   |    2   |    3   |    4   |    5    | Total   |
| :------                                                                 | -----: | -----: | -----: | -----: | ------: | ------: |
| `synthetic-q-and-a_patient-chatbot-emergency-data.json`                 |    8   |    0   |    1   |    1   |    26   |    36   |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data.json`      |    0   |    1   |    1   |    0   |    12   |    14   |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json`  |    4   |    1   |    2   |    2   |    18   |    27   |
| **Totals:**                                                             | **12** |  **2** |  **4** |  **3** |  **56** |  **77** |

Total count: 78 (includes errors), total errors: 1

{: .note}
> **NOTE:** Even though we used the _same_ model to both synthesize and validate Q&A pairs, the models did not always rate all the pairs highly!

The teacher model is asked to provide _reasoning_ for its ratings. It is instructive to look at the output `*-validation.json` files linked above.

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). Exploring each of the poorly-rated Q&A pairs often reveals corner cases that justify more careful handling.

In fact, the program deliberately ignores the actual file where the Q&A pair appears. For example, we had runs where the _emergency_ file contained some _refill_ and _other_ questions. Only the actual label in the answer corresponding to a question was evaluated by the tool. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. You could decide to regroup the files by label to keep the use cases separate or you could just concatenate all the Q&A pairs into one big set. We think the first choice is more in the spirit of how focused, automated tests are supposed to work. Since we used separate prompts for each use case to synthesize the data, could the prompts be improved to minimize this &ldquo;cross pollination&rdquo;? 

Let's look at some poorly-rated Q&A pairs. Here are the nine (out of 36) _emergency_ pairs for `llama3.2:3B` that were rated under four, from the [validation data file](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"}:

```json
{
  "question": "My B has been feeling extremely painful since I started taking my prescription for P, and I need help.",
  "label": "refill",
  "rating": 1,
  "reason": "The question is actually about a patient's body part (B) experiencing pain, which doesn't match the emergency label provided."
}
{
  "question": "I have been taking P and have developed hives all over my skin.",
  "label": "emergency",
  "rating": 3,
  "reason": "The label 'emergency' is a good match because the patient mentions an urgent situation (hives) but it does not contain any specific medical request for P, which suggests that the question requires more context to be classified as 'refill'."
}
{
  "question": "My doctor prescribed me P to help with swelling in my B, but I need a referral to a specialist.",
  "label": "emergency",
  "rating": 1,
  "reason": "The question is asking for a referral to a specialist, which does not match the provided answer's emergency label."
}
{
  "question": "Since I started taking my prescription for P, I have severe stomach cramps.",
  "label": "emergency",
  "rating": 1,
  "reason": "The label 'emergency' seems like a poor match because the question describes severe stomach cramps, which are unlikely to be an emergency situation that requires calling 911."
}
{
  "question": "My B has been feeling extremely painful since I started taking my prescription for P, and I think I might be allergic.",
  "label": "emergency",
  "rating": 1,
  "reason": "The label 'emergency' is a poor match because the question does not describe an urgent situation that requires dialing 911; instead, it mentions potential side effects of a medication."
}
{
  "question": "My B has been feeling extremely painful since I started taking my prescription for P, and I think I might be having an allergic reaction.",
  "label": "refill",
  "rating": 1,
  "reason": "The question mentions a body part (B) and a prescription (P), but the language suggests a possible allergic reaction, which is not typical of refill requests."
}
{
  "question": "Since I started taking my prescription for P, I have severe swelling in my B.",
  "label": "emergency",
  "rating": 1,
  "reason": "The question explicitly mentions a symptom (swelling) that is concerning enough to warrant an emergency response."
}
{
  "question": "My doctor prescribed me P to help with swelling in my B, but I need a referral to a specialist.",
  "label": "refill",
  "rating": 1,
  "reason": "The question is about obtaining a prescription refill, not a referral to a specialist or an emergency situation."
}
{
  "question": "Since I started taking my prescription for P, I have severe swelling in my B.",
  "label": "emergency",
  "rating": 1,
  "reason": "The label 'emergency' seems to be a poor match as the question describes a medical issue but does not explicitly state that it is an emergency situation that requires calling 911."
}
```

While a few of the ratings are accurate, the reasons shown for others don't build confidence! You can see that the model is confused at times about what label it is reviewing; is it the _file's_ label or the Q&A pair's label? It should ignore the file. Also, the last record was rated poorly, because the model assumed the question has to explicitly mention an emergency situation, etc., when in fact the goal is to interpret what the user says as signs that urgent or emergency care is required. If we really wanted to rely on a small model like `llama3.2:3B` as a judge, it would be very good to at least use it in a panel of judges with other small models in different model families.

## Issues You Have to Consider

Let's recap a few issues we discussed.

1. How do you validate that the judge model is producing good Q&A pairs or accurately evaluating the student model's results, depending on the usage pattern? Most likely, some human inspection of the Q&A pairs and possibly some test results will be necessary, until sufficient confidence is established. Using a panel of judges can also improve confidence in the results. [Statistical techniques]({{site.baseurl}}/testing-strategies/statistical-tests) will be useful in establishing confidence. 
2. If the judge model is expensive or slow, how do you use it economically? On the other hand, it won't be used during normal inference, just for the process of validating synthetic data, so the higher inference costs may not really matter. See also the [Experiments to Try](#experiments-to-try).

## Other Tools and Examples

We discussed several popular frameworks for implementing [_evaluations_](https://the-ai-alliance.github.io/trust-safety-evals/){:target="tsei"} in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/). Here is an additional tool that focuses on making use of _LLM as a Judge_ easier and more robust.

### EvalAssist

[`EvalAssist`](https://ibm.github.io/eval-assist/){:target="eval-assist"} is designed to make writing these kinds of evaluations easier, including incremental development. It uses [Unitxt](https://www.unitxt.ai){:target="unitxt"} to implement evaluations. It also helps users refine evaluation criteria iteratively using a web-based user experience. 

### Other Examples

Other examples of using an LLM as a judge can be found in the [IBM Granite Community](https://github.com/ibm-granite-community){:target="igc"}, in the [Granite &ldquo;Snack&ldquo; Cookbook](https://github.com/ibm-granite-community/granite-snack-cookbook){:target="igc-snack"} repo, under the [`recipes/Evaluation`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation){:target="igc-snack-eval"} folder. The _recipes_ in this folder use `unitxt`. They only require running [Jupyter](https://jupyter.org/){:target="jupyter"} locally, because all inference is done remotely by the community's back-end services:

* [`Unitxt_Granite_as_Judge.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Granite_as_Judge.ipynb){:target="igc-snack-eval3"}

In addition, these notebooks demonstrate other aspects of using `unitxt`:

* [`Unitxt_Quick_Start.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Quick_Start.ipynb){:target="igc-snack-eval1"} - A quick introduction to `unitxt`.
* [`Unitxt_Demo_Strategies.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Demo_Strategies.ipynb){:target="igc-snack-eval2"} - Various ways to use `unitxt`.

## Experiments to Try

There is a lot to explore here:

* While we used the same models for data synthesis and judging, for simplicity, try using a different LLM for judging than you used for data synthesis.
* Try using a panel of judges with several small models. How do the results compare to using just one of the small models or using a single, powerful model? How do the resource costs compare?
* In our experiments, the judging process was more time- and compute-consuming than the data generation process. A contributing factor is how we run a separate inference invocation for each Q&A pair. Try modifying the process to pass groups of Q&A pairs per inference invocation. Try a set of five, ten, etc. pairs, per invocation; even all the pairs at once. Do you hit a computation limit beyond a certain number of pairs, e.g., the context window size for your model? Are the rating results independent of this set size or is there a clear advantage with some sizes vs. others? Looking at the examples we showed above for poor ratings, some of which were not very good, does grouping pairs tend to improve the quality of the ratings, in general?
* We discussed asking for a confidence rating and explanation during data synthesis and also asking the judge to compare its rating with the generated rating, etc. Try this and see what happens. Note the _caveat_ mentioned in the discussion about biasing the judge! As always, the more output you generate, the more time and resources will be required for the data judging process. Does this enhanced analysis produce better results that justify the extra time and cost?

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).

---
