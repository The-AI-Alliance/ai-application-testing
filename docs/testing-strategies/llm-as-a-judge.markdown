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

In _LLM as a Judge_, a separate model serves as a _judge_ of the quality of data or model outputs. In the context of testing, a judge can be used for two purposes:

1. Evaluate the quality of the Q&A pairs synthesized for [Unit Benchmarks]({{site.glossaryurl}}/#unit-benchmark), as discussed in the [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks) chapter. 
2. Evaluate the quality of model responses during test runs.

In production deployments, an LLM could also be used to judge model responses during inference, as a &ldquo;sanity check&rdquo;, before allowing the response to be used in further processing or returned to a user. 

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Manual evaluation of synthetic data and model responses (during testing and inference) doesn't scale and is error prone. 
> 1. Let one or more &ldquo;smart&rdquo; _teacher models_ do the judging.
> 1. Small models don't make very good judges, but using a &ldquo;panel&rdquo; of judges with _majority wins_ or _average scoring_ provides more resiliency and can be used when a single large, expensive model isn't a viable choice.
> 1. Deciding on appropriate pass/fail thresholds will require studying actual content, continued experiments, and a growing intuition about what is required. Different values will emerge for use in data validation, test runs, and possibly production judging of generated responses.

Normally, a judge model is chosen because it is considered very &ldquo;smart&rdquo; or capable for evaluating the content in question. It may also be large and expensive to use or otherwise considered not suitable for production use in the application. As for one-time data synthesis, one-time judging of the data can be a cost-effective way to maximize application quality while keeping production costs as low as possible.

Since diversity of perspectives is important here, we should normally use different models as judges than the models used to synthesize data or do inference in production runs. However, this doesn't mean that the same model will always rate responses highly. We will see below that sometimes the same model will rate a Q&A pair poorly that it generated itself!

Like using an LLM to synthesize benchmark data, using an LLM to judge content addresses the limitations of human evaluation: slow, not scalable, and error prone.

## Scoring

The judge could issue a &ldquo;pass/fail&rdquo; ruling, but given the somewhat subjective nature of the task, a rating can be more informative. In our example below, we will ask the judge to rate the quality of a Q&A pair from one to five, from bad to excellent, and to also provide a _reason_ for the judgement. 

So, when using LLM as a judge as part of the process of creating unit benchmark datasets, it is a good idea for _humans_ to review any ratings below four or five. Is the rating accurate? If a datum scored poorly, should it be discarded? If we have a lot of poorly-rated data, should we review and refine how it was created in the first place? Perhaps the prompts used for synthetic data generation could be more precise and descriptive about the expectations for the data? Do we need to use more capable models for data generation?

Alternatively, do low-scoring pairs indicate good corner cases, such as ambiguous input, that might be useful for developing new unit benchmarks and implementation logic for testing and handling such corner cases? 

{: .attention}
> Corner (or edge) cases in any software are a frequent source of bugs and production failures when they are unanticipated and poorly handled. They are even more likely to occur when using generative AI, where the _space_ of possible prompts and responses is large. Therefore, the effort spent to detect and test corner cases is usually well spent.

### A Potential Design Refinement

This suggests a potential design refinement in our healthcare ChatBot, which we suggested as an [Experiment to Try]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try) in the [Unit Benchmark's]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter. Suppose when we do data generation, we also ask the model to provide a _confidence_ rating for how good it thinks the Q&A pair is for the target unit benchmark and how well it thinks the answer responds to the question?

In this enhancement, the judge could compare its rating and explanation with the one the generation model provided. There is a catch to be wary of, however; we _shouldn't_ pass the synthetic pair's confidence rating and explanation to the judge _before_ the judge has rendered its opinion. Otherwise, we will bias its answer! 

However, note that this enhanced judging approach would require at least two inference calls for judging each Q&A pair, the second call being used to compare the confidence and ratings scores. Without this comparison enhancement, only the single inference call to judge the pair is needed. That extra overhead might not be justified.

On the other hand, this enhanced judging approach could improve our effectiveness at surfacing and exploring potential corner cases. So, if this enhanced approach is to expensive to use for all Q&A pairs, the extra overhead might be justified if we use it only for pairs where the generating model had low confidence, the judge provided a low rating, or both.

## Variations of LLM as a Judge

Two variations complement the core features of this practice:

### Panel of LLMs as Judges

Suppose we use a _panel_ of judges instead of a single judge? For pass/fail verdicts, the majority vote would prevail. For a ratings system, the average of the judges' ratings could be more accurate and resilient than the opinion of a single judge. We could even weight each judge's score based on how good the judge is perceived to be.

This approach is a good way to leverage smaller, more cost-effective models, rather than rely on a large, potentially expensive model. When we don't have the budget to use a third-party service's large models (e.g., from OpenAI or Anthropic) and we can't run a large, open-access model in our own environment (like the larger Llama models), using a panel of small models can provide good results economically. A panel of diverse models helps compensate for the weaknesses of any one, relatively-weak model.

### Using External Tools for Evaluation

In [A Variation of LLM as a Judge?]({{site.baseurl}}/testing-strategies/external-verification/#a-variation-of-llm-as-a-judge) in the [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/) chapter, we discuss the idea of leveraging the feedback of external tools for validation, where the  &ldquo;judge&rdquo; model doesn't do the validation itself, but instead it invokes other tools for validation and then interprets the results appropriately.

## Evaluating the Synthetic Data

In [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/), we generated synthetic data, but left the question open how we can validate its quality, other than relying solely on manual inspection (which is still very useful when feasible!). _LLM as a judge_ is one of the best automation tools for this purpose.

The [project repo]({{site.gh_edit_repository}}/){:target="_blank"} contains a tool [`src/scripts/unit-benchmark-data-validation.py`]({{site.gh_edit_repository}}/blob/main/src/scripts/unit-benchmark-data-validation.py/){:target="_blank"} that uses an LLM to rate each synthetic Q&A pair for the three unit benchmarks we generated previously, which are listed in a table in [Running the Data Synthesis Tool]({{site.baseurl}}/testing-strategies/unit-benchmarks/#running-the-data-synthesis-tool).

In this case, we don't use a separate prompt for each unit benchmark. Instead, one prompt works for all cases, as it doesn't mention the benchmark details; it just asks the LLM to judge if the answer is suitable for the question in the Q&A pair. It returns a rating, 1-5, as discussed above, and its reasoning for the rating.

The template file used is [`synthetic-q-and-a_patient-chatbot-data-validation.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml){:target="_blank"}. The system prompt in the file is the following:

```text
You are a teacher model that evaluates the quality of synthetic question and answer (Q&A) pairs
for testing a healthcare ChatBot that allows medical patients to request help from their 
care provider. Some patients will request prescription refills, some patients will actually 
need urgent care and be told to call 911 instead, and the rest of the messages will be for
other purposes. The prompt will contain a question and a label classifying the type of question.
The format of the prompt will be the following:

- \"{"question": question, "label": label}\"

In the question in the prompt, you may see the string _P_ as a placeholder for any mention
of a prescription's name and the string _B_ for any mention of a patient's body part. 
The label will be one of these values:

- emergency, if the question appears to show that the patient is having an urgent
  or emergency situation for which they should dial 911 instead of using this ChatBot.
- refill, if the question is requesting a prescription refill.
- other, for any other question or message.

Your job is to output a score from 1 to 5, where 1 means the label is a poor match for the 
question and 5 means it is an excellent match. You will also provide a reason for your rating.
Use the following JSONL format for your reply:

- \"{"question": question, "label": label, "rating": rating, "reason": reason}\" 

Do not write any comments around the JSONL lines and do not wrap the JSONL in Markdown or 
other markup syntax. Just print the JSONL lines.
```

Each Q&A pair is passed to the judge model as the prompt along with this system prompt.

### Running the Data Validation Tool

Although we said above that it is better to pick a different model for a judge, for simplicity we used the same models that were used in data synthesis, which is adequate for our learning purposes. 

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

In this case, the `--data` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory. We saved the output of example runs under the same [`src/data/examples`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/){:target="_blank"} directory:

| Validation Data File | `gpt-oss:20b` | `llama3.2:3B` |
| :---- | :---- | :---- |
| `synthetic-q-and-a_patient-chatbot-emergency-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.json){:target="_blank"} |
| `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json` | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json){:target="_blank"} | [example](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.json){:target="_blank"} |

These files rate each Q&A pair from 1 (bad) to 5 (great) and provide reasoning for each rating.
Also, summary statistics are written by the tool to `stdout` and to the output file `temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out` for `gpt-oss:20b`. (Example output files are also saved to [`src/data/examples`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/){:target="_blank"}.) We show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. Here are the statistics for a test runs with `gpt-oss:20b` and `llama3.2:3B`:

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
> **NOTE:** Even though we used the _same_ model to both synthesize and validate Q&A pairs, the models did not always rate all the pairs they generated themselves very highly!

The teacher model is asked to provide _reasoning_ for its ratings, too. It is instructive to look at the output `*-validation.json` files linked above, particularly the reasons given for the low ratings.

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). Exploring each of the poorly-rated Q&A pairs often reveals corner cases that justify more careful handling.

Recall in the [Unit Benchmarks]({{site.baseurl}}/unit-benchmarks/) section [Evaluating the Synthetic Data]({{site.baseurl}}/unit-benchmarks/#evaluating-the-synthetic-data), we said we want to evaluate the synthetic data based on a few criteria:

* Is the question relevant to the purpose of this test?
* If the question is relevant, is the supplied answer correct?

In fact, the prompt for the validation program deliberately ignores the first question: is a particular Q&A pair relevant to the benchmark? In in our case, it is quite easy to answer this question _without_ using AI; we can just check if the label for a Q&A pair matches the benchmark data file where it appears! For example, we had runs where the _emergency_ file contained some pairs labeled _refill_ and _other_. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. We could decide to regroup the files by label to keep the use cases cleanly separated or we could concatenate all the Q&A pairs into one big set. 

We recommend the first choice. First, keeping the files separate is more in the spirit of how focused, automated tests are supposed to work. Second, if we mixed the files, we would lose this information about relevancy! However, since we used separate prompts for each use case to synthesize the data, we should investigate improving the prompts to minimize this &ldquo;cross pollination&rdquo;.

Nevertheless, as our data synthesis grows more sophisticated for more benchmarks, we may decide that having a judge evaluate relevancy is a useful additional validation step, especially as we can no longer just rely on classification, but we start generating and evaluating text answers in our synthetic Q&A pairs. 

So, our validation tool only considers the second question, whether or not the label shown in the answer the best label for the question, independent of which data file the Q&A pair appears.

Let's look at some poorly-rated Q&A pairs. Here are the nine (out of 36, so 25%) _emergency_ pairs for `llama3.2:3B` that were rated under four in the example [validation data file](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/llama3.2_3B/data/synthetic-q-and-a_patient-chatbot-emergency-data-validation.json){:target="_blank"}:

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

While a few of the ratings are accurate, the reasons shown for others don't build confidence! We can see that the model is confused at times about what label it is reviewing; is it the _file's_ label or the Q&A pair's label? Our system prompt told the model to ignore the file. Also, the last record was rated poorly, because the model assumed the question has to explicitly mention an emergency situation, etc., when in fact the goal is to interpret whether or not what the user says indicates that urgent or emergency care is required. If we really want to rely on a small model like `llama3.2:3B` as a judge, it would be good to use it in a panel of judges with other small models from different model families.

### What Is &ldquo;Good Enough&rdquo;?

We are still in the process of _creating_ our unit benchmarks, specifically the validation of the test datasets we will use. Therefore, when feasible, we should carefully inspect the data and the validation results to answer a few questions about how well the process is working. After gaining experience, we might decide that highly-rated Q&A pairs are probably good and don't need manual inspection. If so, we can focus our attention on Q&A pairs with low ratings.

Where we believe a low rating is incorrect, we can simply ignore the rating and continue to use the pair, but we should explore if there are improvements that could be made to how pairs are rated (e.g., in the system prompt), so that _false negatives_ are less likely in the future.

Where a low rating is valid, do we discard the pair or consider it suitable for exploring edge-case behaviors? If we keep it, we should consider creating separate unit benchmarks for corner cases, because each unit benchmark is supposed to be very focused on single purposes and, for practical reasons, we might need to define a different &ldquo;pass/fail&rdquo; threshold _for each unit benchmark_. This will happen when we decide that a benchmark is hard for our system to do well on, but it is still informative enough to continue using, and lower scores are &ldquo;tolerable&rdquo;.

Finally, with the pairs filtered, do we think the dataset is comprehensive overall, with sufficient coverage, but not so large that it contains excess redundancy?

#### What Constitutes &ldquo;Pass/Fail&rdquo;

For reasonably straightforward behaviors, like our prescription refill _FAQ_, we found we could expect a high level of reliable performance, so a passing score can be _near_ 100%, if not exactly 100%. Unfortunately, we will rarely have the &ldquo;luxury&rdquo; of expecting the traditional testing standard: 100% must pass or the test run fails. 

We saw that sensing urgent or emergency situations was much more ambiguous. What is pass/fail here? We might except a lower threshold for passing. Or we might decide that the use case can't be implemented this way, because our handling can't be precise enough to be trusted. We may have to explore a much different alternative. For this use case, the alternative might be to _always_ return as part of the first response to a user, "If this is an emergency, please leave this app and call 911."

Testing for edge cases is a similar challenge. Can we really be confident in our replies for these queries. The safest strategy, especially for new projects or features is to be conservative and only accept model responses with a confidence rating either from the inference model or a judge model that evaluates the response to the patient query. Log all less certain responses for follow-up offline and _fail over_ to a safe response, such what we used in the TDD example for _other_ queries, &ldquo;I have received your message, but I can't answer it right now. I will get back to you within the next business day.&rdquo; A less cautious reply would be "I'm not sure I understand you message. Can you rephrase it?".

Ultimately, as well learn, we will adjust the pass thresholds for response confidence during production runs and pass/fail acceptance during tests and data validation, based on our experience and our developing confidence about acceptable levels of performance, _per use case_, and how confidence develops in our system's ability to meet expectations. Fortunately, with good fallback options, like our _other_ queries and deterministic response, we can start off cautiously and gradually improve our system's ability to provide better and better responses to a wider range of queries. 

Of course, we have to balance user satisfaction. If they feel like the ChatBot can't do anything, that can be worse than just relying on older approaches like asking them to send an email or leave a voice message.

#### Checklist for Each Unit Benchmark

To conclude, for _each_ unit benchmark, based in part on the complexity of the behavior being tested:

* Is there a sufficient number of Q&A pairs for good coverage, but not so many that we have too much wasteful redundancy?
* What is the threshold for pass/fail? The thresholds may be different for synthetic data validation, test runs, and even judging of responses during production, if implemented?
* How do we identify, test, and handle edge cases?

## Evaluating Responses During Tests and Production

Using LLM as a judge to validate synthetic data is one use of this technique for testing. A second use is to evaluate model responses during test execution.

The process is very similar to how we evaluated synthetic data, except this time inference calls are are made with test questions and the judge evaluates the responses. This technique is most useful when the response includes generated text, not just labels.  

We can use the same implementation in the production system, where the judge critiques each response before allowing downstream processing. Most likely, _human in the loop_ checking won't be feasible, although information should be logged for &ldquo;post mortem&rdquo; analysis. Since we have to rely on the judge to do a good job, thresholds for acceptable replies may need to be more stringent.

TODO: Provide an example of using LLM as a Judge during test runs (see [issue #25](https://github.com/The-AI-Alliance/ai-application-testing/issues/25){:target="_blank"}). As always, [help is welcome]({{site.baseurl}}/contributing)!

## Issues We Have to Consider

Let's recap a few issues we discussed.

1. How do we validate that the judge is accurately evaluating the synthetic data, test results or runtime inference checks (when implemented)? Some manual inspection of the data and judgements will be necessary until sufficient confidence is established to trust the processes. 
1. How do we decide on acceptable thresholds for passing for these different uses of judges?
1. Are we using a small model as a judge? Instead, we should consider using a panel of judges of similar models from different model families to complement each other's strengths and weaknesses, so we can improve our confidence in the judgements. 
1. What should we do with low-rated pairs? Discard them or use them to help explore corner cases? 
3. If the judge model is expensive or slow, how do we use it economically? On the other hand, if we aren't using this model during normal inference, but just for the process of judging, are the higher inference costs manageable? See also the [Experiments to Try](#experiments-to-try).

<a id="other-tools"/>

## Other Tools for LLM as a Judge

We discussed several popular frameworks for implementing [_evaluations_](https://the-ai-alliance.github.io/trust-safety-evals/){:target="tsei"} in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/). Here is an additional tool that focuses on making use of _LLM as a Judge_ easier and more robust.

### EvalAssist

[EvalAssist](https://ibm.github.io/eval-assist/){:target="eval-assist"} ([paper](https://arxiv.org/abs/2410.00873v2){:target="_blank"}) is designed to make LLM as a Judge evaluations of data easier for users, including incremental refinement of the evaluation criteria using a web-based user experience. EvalAssist supports direct assessment (scoring) of data individually, which we used above, or pair-wise comparisons, where the best of two answers is chosen. With pair-wise comparisons, several forms of judgement bias can occur: 

1. **Positional bias**, where the judge tends to pick the first or second option preferentially.
2. **Self-enhancement bias**, where an LLM prefers its own responses.
3. **Verbosity bias**, where an LLM judge favors longer responses even if they are not the best choice.

EvalAssist uses [Unitxt](https://www.unitxt.ai){:target="unitxt"} (first discussed in [Unit Benchmarks](testing-strategies/unit-benchmarks/#unitxt)) to implement evaluations. 

## Other Examples

Other examples of using an LLM as a judge can be found in the [IBM Granite Community](https://github.com/ibm-granite-community){:target="igc"}, in the [Granite &ldquo;Snack&ldquo; Cookbook](https://github.com/ibm-granite-community/granite-snack-cookbook){:target="igc-snack"} repo, under the [`recipes/Evaluation`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation){:target="igc-snack-eval"} folder. The _recipes_ in this folder use `unitxt`. They only require running [Jupyter](https://jupyter.org/){:target="jupyter"} locally, because all inference is done remotely by the community's back-end services:

* [`Unitxt_Granite_as_Judge.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Granite_as_Judge.ipynb){:target="igc-snack-eval3"}

In addition, these notebooks demonstrate other aspects of using `unitxt`:

* [`Unitxt_Quick_Start.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Quick_Start.ipynb){:target="igc-snack-eval1"} - A quick introduction to `unitxt`.
* [`Unitxt_Demo_Strategies.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Demo_Strategies.ipynb){:target="igc-snack-eval2"} - Various ways to use `unitxt`.

## Experiments to Try

* While we used the same models for data synthesis and judging, for simplicity, try using a different LLM for judging than you used for data synthesis. What insights do you learn about weaknesses in the generation process (e.g., the prompts or models used) as you review the judgements?
* If you can, try different judge models of different sizes in the same model family. How do the judgments compare? Considering the cost vs. quality trade offs, can you determine a good &ldquo;sweet spot&rdquo; model that best balances these trade offs?
* Try using a panel of judges with several small models. How do the results compare to using just one of the small models or using a single, more powerful model? How do the resource costs compare?
* In our experiments, the judging process was more time- and compute-consuming than the data generation process. A contributing factor is how we run a separate inference invocation for each Q&A pair. Try modifying the process to pass groups of Q&A pairs per inference invocation. Try a set of five, ten, etc. pairs, per invocation; even all the pairs at once. Do you hit a computation limit beyond a certain number of pairs, e.g., the context window size for your model? Are the rating results independent of this set size or is there a clear advantage with some sizes vs. others? Looking at the examples we showed above for poor ratings, where some of the ratings were themselves not very good, does grouping pairs tend to improve the overall quality of the ratings, in general?
* In [A Potential Design Refinement](#a-potential-design-refinement) above, we discussed asking for a confidence rating and explanation during data synthesis and also asking the judge to compare its rating with the generated rating, etc. Try this and see what happens. Note the caveat mentioned in the discussion about biasing the judge! Does this enhanced analysis produce better results that justify the extra time and cost? Does it help you identify more corner cases.  We mentioned the idea of only using the technique for Q&A pairs where the generating model has low confidence, the judge provides a low rating, or both. What does it suggest if the generating model had high confidence, but the judge provided a low rating, or vice-versa? Is that more interesting than when they agree with each other?
* In the [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/) chapter, we briefly considered the question of [how many Q&A pairs do we need?]({{site.baseurl}}/testing-strategies/unit-benchmarks/#how-many-qa-pairs-do-we-need). We suggested a &ldquo;preliminary&rdquo; exploration of this question in [Experiments to Try]({{site.baseurl}}/testing-strategies/unit-benchmarks/#experiments-to-try) in that chapter. Now run the validation tool on the different-sized datasets you created. When you look at the statistics output (e.g., like in the example tables above), do the statistics improve with larger datasets? Looking at particular ratings for Q&A pairs, what intuitions can you form about the overall quality and coverage for each use case?

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).

---
  