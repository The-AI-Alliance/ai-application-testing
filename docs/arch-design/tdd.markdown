---
layout: default
title: Test-Driven Development
nav_order: 220
parent: Architecture and Design for Testing
has_children: false
---

# Test-Driven Development

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

In [Testing Problems Caused by Generative AI Nondeterminism]({{site.baseurl}}/testing-problems/), we discussed how Generative AI introduces new forms of [Nondeterminism]({{site.glossaryurl}}/#determinism) into applications that break our traditional reliance on deterministic behavior, for reasoning about how the system behaves, during design and implementation, and for writing tests that are repeatable, comprehensive, and automated.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. When testing a generative AI [Component]({{site.glossaryurl}}/#component), like a model, you have to write a test using tools designed for evaluating [Stochastic]({{site.glossaryurl}}/#statistic) processes, such as the tools used for [Benchmarks]({{site.glossaryurl}}/#benchmark).
> 1. We build our first example exploring this approach.
> 1. For efficiency, experiment with the [System Prompt]({{site.glossaryurl}}/#system-prompt) to find the minimally-sufficient content that provides the best results. [Prompt]({{site.glossaryurl}}/#prompt) design, including system prompts, is still something of a _black art_.
> 2. When it is feasible, mapping a range of similar prompts to the same response, like FAQs, makes those scenarios _semi-deterministic_, and therefore much easier to design and test.
> 3. Think about ways to further process responses to make them even more consistent (like normalizing letter case), while still preserving utility. For example, an application that generates street addresses could be passed through a transformer that converts them to a uniform, post-office approved format.
> 4. Include robust fall-back handling when a good response is not obvious. Spend time on designing for edge cases and _graceful recovery_.
> 5. For early versions of an application, bias towards conservative handling of known scenarios and falling-back to human intervention for everything else. This lowers the risks associated with unexpected inputs and undesirable results, makes testing easier, and allows you to build confidence incrementally as you work to improve the breadth and resiliency of the prompt and response handling in the application.  

Let us talk about &ldquo;traditional&rdquo; testing first, and introduce our first example of how to test an AI component. In our subsequent discussion about architecture and design, we will refer back to this example. 

## What We Learned from Test-Driven Development

The pioneers of [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development) (TDD) several decades ago made it clear that TDD is really a _design_ discipline as much as a _testing_ discipline. When you write a test before you write the code necessary to make the test pass, you are in the frame of mind of specifying the expected [Behavior]({{site.glossaryurl}}/#behavior) of the new code, expressed in the form of a test. This surfaces good, minimally-sufficient abstraction boundaries organically, both the [Component]({{site.glossaryurl}}/#component) being designed and implemented right now, but also dependencies on other components, and how dependencies should be managed. 

We will discuss the qualities that make good components in [Component Design]({{site.baseurl}}/arch-design/component-design/), such as [The Venerable Principles of Coupling and Cohesion]({{site.baseurl}}/arch-design/component-design/#coupling-cohesion). For now, let us focus on how TDD promotes those qualities.

The coupling to dependencies, in particular, led to the insight that you need to [Refactor]({{site.glossaryurl}}/#refactor) the current code, and maybe even some of the dependencies or their abstraction boundaries, in order to make the code base better able to accept the changes planned. This is a _horizontal_ change; all features remain _invariant_, with no additions or removals during this process. The existing test suite is the safety net that catches any regressions accidentally introduced by the refactoring.

Hence, the application design also evolves incrementally and iteratively, and it is effectively maintained to be _optimal_ for the _current_ feature set, without premature over-engineering that doesn't support the current working system. However, refactoring enables the system to evolve as new design requirements emerge in subsequent work.

After refactoring, only then is a new test written for the planned feature change and then the code is implemented to make the test pass (along with all previously-written tests). The iterative nature of TDD encourages you to make minimally-sufficient and incremental changes as you go.

That doesn't mean you proceed naively or completely ignore longer-term goals. During this process, the software design decisions you make reflect the perspective, intuition, and idioms you have built up through years of experience.

This methodology also leans heavily on the expectation of [Deterministic]({{site.glossaryurl}}/#Determinism) behavior, to ensure repeatability, including the need to handle known sources of nondeterminism, like [Concurrency]({{site.glossaryurl}}/#concurrency). 

## TDD and Generative AI

So, how can we practice TDD for tests of stochastic components? First, to be clear, we are not discussing the use of generative AI to generate traditional tests for source code. Rather, we are concerned with how to use TDD to test generative AI itself!

First, what aspects of TDD _don't_ need to change? Let's use a concrete example. Suppose we are building a [ChatBot]({{site.glossaryurl}}/#chatbot) for patients to send messages to a healthcare provider. In some cases, an immediate reply will be generated automatically. In the rest of the cases, a response will be returned to the use that the provider will have to respond personally as soon as possible. 

{: .warning}
> **DISCLAIMER:** We will use this healthcare ChatBot example throughout this guide. Needless to say, but we will say it anyway, a ChatBot is notoriously difficult to implement successfully, because of the free form prompts from users and the many possible responses models can generate. A healthcare ChatBot is even more challenging because of the risk it could provide bad responses that lead to poor patient outcomes, if applied. Hence, this example _must_ only be used for educational purposes. It is not at all suitable for use in real healthcare settings.

Let's suppose the next &ldquo;feature&rdquo; we will implement is to respond to a request for a prescription refill. (Let's assume any necessary refactoring is already done.)

Next we need to write a first [Unit Test]({{site.glossaryurl}}/#unit-test). A conventional test relying on fixed inputs and fixed corresponding responses won't work. We don't want to require a patient to use a very limited and fixed format [Prompt]({{site.glossaryurl}}/#prompt). So, let's write a &ldquo;unit benchmark&rdquo;[^1], an analog of a unit test. This will be a very focused set of Q&A pairs, where the questions should cover as much variation as possible in the ways a patient might request a refill, e.g.,

* &ldquo;I need my _P_ refilled.&rdquo;
* &ldquo;I need my _P_ drug refilled.&rdquo;
* &ldquo;I'm out of _P_. Can I get a refill?&rdquo;
* &ldquo;My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?&rdquo;
* ...

[^1]: We define what we really mean by the term _unit benchmark_ [here]({{site.baseurl}}/testing-strategies/unit-benchmarks/). See also the [glossary definition]({{site.glossaryurl}}#unit-benchmark).

We are using _P_ as a placeholder for any prescription.

For this first iteration, the answer parts of the Q&A pairs might be identical for all cases:[^2] 

* &ldquo;Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.&rdquo;

[^2]: A future feature might be able to check the patient's records to confirm if the refill is allowed, respond immediately with an answer, and start the refill process if it is allowed.

Now we have to answer these questions:

* For those questions and desired answers that have a placeholder _P_ for the drug, how do we handle testing any conceivable drug?
* What should happen if the request doesn't appear to be a refill request?
* How do we create these Q&A pairs?
* How do we run this &ldquo;unit test&rdquo;?
* How do we validate the resulting answers?
* How do we define &ldquo;pass/fail&rdquo; for this test?

## Ways that LLMs Make Our Jobs Easier

Let's explore the first two questions:

* For those questions and desired answers that have a placeholder _P_ for the drug, how do we handle testing any conceivable drug?
* What should happen if the request doesn't appear to be a refill request?

It turns out this is often easier to address than it might appear at first. Before LLMs, we would have to think about some sort of language _parser_ that finds key values and lets us use them when forming responses. With LLMs, all we will need to do is to specify a good [System Prompt]({{site.glossaryurl}}/#system-prompt) that steers the LLM towards the desired behaviors. Let's see an example of how this works.

First, LLMs have been trained to recognize prompt strings that might contain a system prompt along with the user query. This system prompt is usually a static, application-specific string that provides fixed context to the model. For our experiments with this example, we used two, similar system prompts. Here is the first one:

```text
You are a helpful assistant for medical patients requesting help from their care provider. 
Some patients will request prescription refills. Here are some examples, where _P_ would 
be replaced by the name of the prescription the user mentions:

- "I need my _P_ refilled."
- "I need my _P_ drug refilled."
- "I'm out of _P_. Can I get a refill?"
- "I need more _P_."
- "My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?"

Whenever you see a request that looks like a prescription refill request, always reply
with the following text, where _P_ is replaced by the name of the prescription:

- Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.

If the request doesn't look like a refill request, reply with this message:

- I have received your message, but I can't answer it right now. I will get back to you within the next business day.
```

We found that providing examples wasn't necessary to achieve good results, at least for the two, modestly-sized models we used in our tests (GPT-OSS 20B and Llama 3.2 3B); the following, shorter system prompt _usually_ worked just as well:

```text
You are a helpful assistant for medical patients requesting help from their care provider. 
Some patients will request prescription refills. Whenever you see a request that looks like
a prescription refill request, always reply with the following text, where _P_ is replaced 
by the name of the prescription:

- Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.

If the request doesn't look like a refill request, reply with this message:

- I have received your message, but I can't answer it right now. I will get back to you within the next business day.
```

We tried both system prompts with the models [`gpt-oss:20b`](https://huggingface.co/openai/gpt-oss-20b){:target="hf-gpt-oss"} and [`llama3.2:3B`](https://huggingface.co/meta-llama/Llama-3.2-3B){:target="hf-llama32"}, served locally using [`ollama`](https://ollama.com/){:target="ollama"} with a number of prompts (more details below). First, a set of refill requests:

* `I need my _P_ refilled.`
* `I need my _P_ drug refilled.`
* `I'm out of _P_. Can I get a refill?`
* `I need more _P_.`
* `My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?`

We also tried other requests that aren't related to refills:

* `My prescription for _P_ upsets my stomach.`
* `I have trouble sleeping, ever since I started taking _P_.`
* `When is my next appointment?`

We ran separate queries for `_P_` replaced with `prozac` and `miracle drug`.

For both models, both drugs, and all refill requests, the expected answer was always returned, `Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.`, with `_P_` replaced by the drug name, although sometimes the model would write `Prozac`, which is arguably more correct, rather than what the &ldquo;user&rdquo; entered, `prozac`. When checking the results, the script described shortly would do a case-insensitive comparison, when necessary.

Similarly, for the other prompts, the expected response was always returned: `I have received your message, but I can't answer it right now. I will get back to you within the next business day.`

If you want to try our code yourself, see [Try This Yourself!](#try-this-yourself) below.

To recap what we have learned so far, we effectively created more or less _deterministic_ outputs for a narrow range of particular inputs! This suggests a design idea we should explore next.

## Idea: Handling Frequently Asked Questions

In this app, asking for a prescription refill is a _frequently asked question_ (FAQ). We observed that even small models, with a good system prompt, were able to &ldquo;map&rdquo; a range of similar questions to the same answer and even do appropriate substitutions in the text, the prescription in this case.

What other FAQs are there? Analyzing historical messages sent to providers is a good way to find other potential FAQs that might benefit from special handling, such as through the system prompt. When doing that historical analysis, you could use an LLM to find groups of related questions. These groups could be the start of a Q&A pairs dataset for testing. For different applications, there may very common prompts sent to a model that can benefit from this special treatment.

This suggests a next, more sophisticated step to explore. Should we build a _classifier_ model (see [Evaluation]({{site.glossaryurl}}/#evaluation) for a description), through which all messages are first passed? These models tend to be small and efficient, because they only need to output one or possibly more known labels based on the input, and not output generated text. The idea is that the classifier would first label each message with one of a fixed set of labels. So far in our example, we have one label for the prescription refill &ldquo;FAQ&rdquo; and one for &ldquo;other&rdquo; messages, covering everything else. 

When a FAQ label is returned, our application can route the message to a low-cost model [Tuned]({{site.glossaryurl}}/#tuning) specifically for our known FAQs, or we perform other special handling that doesn't use generative AI. So far, we found we don't even need to tune a special model for our FAQ detection.

In contrast, the &ldquo;other&rdquo; messages would be routed to a smarter (and less cost-effective) model that is better able to handle more diverse prompts.

Finally, thinking in terms of a classifier suggests that we don't necessarily want to hard-code in the system prompt the deterministic answer the model should return, like we did above. Instead, we should return just the label and any additional data of interest, like a drug name that is detected. This answer could be formatted in JSONL:

```json
{"question": "...", "label": "refill-request", "drug-name": "miracle drug"}
```

Then the UI that presents the response to the user could format the actual response we want to show, where the format would be specified in a configuration file, so it is easy to change the response without changing the system prompt, etc. This would also make _internalization_ easier, where a configuration file with German strings is used for a German-speaking audience, for example. 

{: .note}
> **NOTE:** For internationalization, we will need to choose an LLM that is properly _localized_ for each target language we intend to support.

## Creating and Using Unit Benchmarks

The remaining four questions we posed above are these:

* How do we create these Q&A pairs?
* How do we run this &ldquo;unit test&rdquo;?
* How do we validate the resulting answers?
* How do we define &ldquo;pass/fail&rdquo; for this test?

In addition, we just discovered that we could have our models return a desired, _deterministic_ response for particular &ldquo;classes&rdquo; of prompts, like various ways of asking for prescription refills. This suggests two additional questions for follow up:

* How _diverse_ can the prompts be and still be correctly labeled by the LLM we use for classification?
* If those edge cases aren't properly handled, what should we do to _fail gracefully_?

Several of these questions share the requirement that we need a scalable and efficient way to create lots of high-quality Q&A pairs. One drawback of our experiment above was the way we manually created a few Q&A pairs for testing. The set was not at all comprehensive. Human creation of data doesn't scale well and it is error prone, as we are bad at exhaustively exploring all possibilities, especially edge cases.

Hence, we need automated techniques for data _synthesis_ to scale up our tasks beyond the ad hoc approach we used above, especially as we add more and more tests. We also need automated techniques for validating the quality of our synthetic test data.

In [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks), we will explore automated data synthesis techniques and we will also discuss how to run the unit benchmarks we create, moving towards the automated test suites we desire.

To automatically check the quality of synthetic Q&A test pairs, including how well each answer aligns with its question, we will explore techniques like [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) and [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).

Finally, [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests/) will help us decide what &ldquo;pass/fail&rdquo; means. We got _lucky_ in our example above; for our hand-written Q&A pairs, we were able to achieve a 100% pass rate, at least _most of the time_, as long as it was okay to ignore capitalization of some words and some other _insignificant_ differences! This convenient certainty won't happen very often, especially if when we explore edge cases.


## Try This Yourself!

Our examples are written as Python tools. They are run using `make` commands. 

Clone the project [repo]({{site.gh_edit_repository}}/){:target="_blank"} and see the [`README.md`]({{site.gh_edit_repository}}/){:target="_blank"} for setup instructions, etc. Much of the work can be done with `make`. Try `make help` for details. All of the Python tools have their own `--help` options, too.

### Running with `make`

After completing the setup steps described in the [`README.md`]({{site.gh_edit_repository}}/){:target="_blank"}, run this command to execute the code used above:

```shell
make run-tdd-example-refill-chatbot
```

This target runs the following command:

```shell
time uv run src/scripts/tdd-example-refill-chatbot.py \
  --model ollama/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir src/prompts/templates \
  --output temp/output/ollama/gpt-oss_20b/tdd-example-refill-chatbot.out \
  --data temp/output/ollama/gpt-oss_20b/data
```

{: .tip}
> **Tip:** To see this command without running anything, pass the `-n` or `--dry-run` option when &ldquo;making&rdquo; any target.

The `time` command returns how much system, user, and "wall clock" times were used for execution on MacOS and Linux systems. Note that [`uv`](https://docs.astral.sh/uv/) is used to run this tool (discussed in the README) and all other tools we will discuss later. The arguments are used as follows:

| Argument | Purpose |
| :------- | :------ |
| `--model ollama/gpt-oss:20b` | The model to use. |
| `--service-url http://localhost:11434` | Only used for `ollama`; the local URL for the `ollama` server. |
| `--template-dir src/prompts/templates` | Where we have prompt templates we use for all the examples. They are `llm` compatible, too. See the Appendix below. |
| `--output temp/output/ollama/gpt-oss_20b/tdd-example-refill-chatbot.out` | Where console output is captured. |
| `--data temp/output/ollama/gpt-oss_20b/data` | Where any generated data files are written. (Not used by all tools.) |

{: .tip}
> **Tips:**
> 1. The [`README.md`]({{site.gh_edit_repository}}/){:target="_blank"}'s setup instructions explain how to use different models, e.g., `make MODEL=ollama/llama3.2:3B some_target`, instead of the default `ollama/gpt-oss:3.2:3B`.
> 1. If you want to save the output of a run to `src/data/examples/`, run the target `make save-examples`. It will create a subdirectory for the model used. Hence, you have to specify the desired model, e.g., `make MODEL=ollama/llama3.2:3B save-examples`. We have already saved example outputs for `ollama/gpt-oss:20b` and `ollama/llama3.2:3B`. See also the `.out` files that capture "stdout".

The script runs two experiments, each with these two templates files:

* [`q-and-a_patient-chatbot-prescriptions.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions.yaml){:target="_blank"} 
* [`q-and-a_patient-chatbot-prescriptions-with-examples.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml){:target="_blank"}

The only difference is the second file contains embedded examples in the prompt, so in principal the results should be better, but in fact, they are often the same.

{: .note}
> **NOTE:** These template files are designed for use with the `llm` CLI (see the Appendix in [`README.md`]({{site.gh_edit_repository}}/){:target="_blank"}). In our Python scripts, [LiteLLM](https://docs.litellm.ai/#basic-usage) is used to invoke inference and we extract the content we need from these files and use it to construct the prompts we send through LiteLLM.

This program passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. You can see example output for [`ollama/gpt-oss:20b`]({{site.gh_edit_repository}}/){:target="_blank"}

Examples of the output can be found in the repo for [`gpt-oss_20b`]({{site.gh_edit_repository}}/blob/main/src/data/examples/ollama/gpt-oss_20b/tdd-example-refill-chatbot.out){:target="_blank"} and for [`llama3.2_3B`]({{site.gh_edit_repository}}/blob/main/src/data/examples/ollama/llama3.2_3B/tdd-example-refill-chatbot.out){:target="_blank"} (Yes, the `ollama` names for the models mix upper- and lower-case `b`.) 

You will see some reported errors, especially for `llama3.2:3B`, but often the wording differences are trivial. How could we do more robust comparisons?

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to our section on [Testing Strategies]({{site.baseurl}}/testing-strategies), in particular the chapter on [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/).

---
