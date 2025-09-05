---
layout: default
title: Test-Driven Development
nav_order: 210
parent: Architecture and Design for Testing
has_children: false
---

# Test-Driven Development

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

[^1]: We define what we really mean by the term _unit benchmark_ [here]({{site.baseurl}}/testing-strategies/unit-benchmarks/).

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

### Ways that LLMs Make Our Jobs Easier

Let's explore the first two questions:

* For those questions and desired answers that have a placeholder _P_ for the drug, how do we handle testing any conceivable drug?
* What should happen if the request doesn't appear to be a refill request?

It turns out this is often easier to address than it might appear at first. Before LLMs, we would have to think about some sort of language _parser_ that finds key values and lets us use them when forming responses. With LLMs, all we will need to do is to specify a good [System Prompt]({{site.glossaryurl}}/#system-prompt) that steers the LLM towards the desired behaviors. Let's see an example of how this works.

First, LLMs have been trained to recognize prompt strings that might contain a system prompt along with the user query. This system prompt is usually a static, application-specific string that provides fixed context to the model. For our experiments with this example, we used two, similar system prompts. Here is the first one:

```text
You are a helpful assistant for medical patients requesting help from their care provider. Some patients will request prescription refills. Here are some examples, where _P_ would be replaced by the name of the prescription the user mentions:

- "I need my _P_ refilled."
- "I need my _P_ drug refilled."
- "I'm out of _P_. Can I get a refill?"
- "My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?"

Whenever you see a request that looks like a prescription refill request, always reply with the following text, where _P_ is replaced by the name of the prescription:

- Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.

If the request doesn't look like a refill request, reply with this message:

- I have received your message, but I can't answer it right now. I will get back to you within the next business day.
```

We found that providing examples wasn't actually necessary in this case, at least for the two, modestly-sized models we used in our tests; the following shorter system prompt worked just as well:

```text
You are a helpful assistant for medical patients requesting help from their care provider. Some patients will request prescription refills. 

Whenever you see a request that looks like a prescription refill request, always reply with the following text, where _P_ is replaced by the name of the prescription:

- Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day.

If the request doesn't look like a refill request, reply with this message:

- I have received your message, but I can't answer it right now. I will get back to you within the next business day.
```

We tried both system prompts with the models [`gpt-oss:20B`](https://huggingface.co/openai/gpt-oss-20b){:target="hf-gpt-oss"} and [`llama3.2:3B`](https://huggingface.co/meta-llama/Llama-3.2-3B){:target="hf-llama32"}, served locally using [`ollama`](https://ollama.com/){:target="ollama"} with a number of prompts. First, a set of refill requests:

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

### Try This Yourself!

We used `zsh` scripts for Linux or MacOS. Clone the project [repo](https://github.com/The-AI-Alliance/ai-application-testing/) and run commands in the `src` directory. 

#### Running with `make`

You can run the scripts directly or use `make`. Switch to the `src` directory and run this `make` command:

```shell
make one-time-setup run-tdd-example
```

The `one-time-setup` target will `pip install` tools like [`llm`](https://github.com/simonw/llm){:target="llm"}, install _template_ files used by `llm`, etc. The `run-tdd-example` target runs the script `scripts/tdd-example-refill-chatbot.sh`.

Try `make help` for details about the `make` process. There is also a `--help` option for the script.

As the name suggests, you don't need to repeat `one-time-setup`. You can just run `make run-tdd-example` to repeat execution. You can also run the script directly if you prefer, _after using make once_. The reason you need to run `make run-tdd-example` at least once is because it copies some files to `src/temp` that you will need. These files are staged in directories for the website to have them available.

#### Setting up and Running the Tools Individually

Here are some details handled by the `make` process, which you could do yourself, if you prefer.

The `zsh` script, `tdd-example-refill-chatbot.sh`, is in the `src` directory of the repo or you can download it [here]({{site.gh_edit_repository}}/blob/main/src/scripts/tdd-example-refill-chatbot.sh){:target="_blank"}

Before running the full script, you'll need to install some tools. We used the excellent [`llm` CLI tool](https://github.com/simonw/llm){:target="llm"} from Simon Willison, which can call a variety of services for model inference, including local serving using [`ollama`](https://ollama.com){:target="ollama"}, which we used for these tests. See the `llm` docs for using other options, like OpenAI's or Anthropic's hosted models.

If you install and use [`ollama`](https://ollama.com){:target="ollama"}, install the `llm` plugin using this command: 

```shell
llm install llm-ollama
```

Then install your models of choice. For example, to install the `llama3.2:3B` and `gpt-oss:20b` models we used, run these commands:

```shell
ollama pull llama3.2:3B
ollama pull gpt-oss:20b
```

(Yes, it is `B` for one and `b` for the other, as shown...)

{: .tip}
> **TIP:** If you use a tool like `ollama` for local inference, you will have to pick a model that works on your machine. 
> For example, while testing on Apple computers with M1 Max chips, 32GB of memory was not enough for `gpt-oss:20b` if a normal load of other applications was also running, but there was sufficient memory for `llama3.2:3B`. Having 64GB of memory allowed `gpt-oss:20b` to work well. Pick a small enough model that you can run, but keep in mind that the quality of the output will decrease for smaller models.

The `tdd-example-refill-chatbot.sh` script assumes you have our `llm` &ldquo;templates&rdquo; installed (which is also handled by the `make` process above). To install them yourself, first run the following command to see where `llm` has templates installed on your system: 

```shell
llm templates path
```

On MacOS, it will be `$HOME/Library/Application Support/io.datasette.llm/templates`. Now download the following two files and copy them to the correct location:

* [`q-and-a_patient-chatbot-prescriptions.yaml`]({{site.gh_edit_repository}}/blob/main/src/llm/templates/q-and-a_patient-chatbot-prescriptions.yaml){:target="_blank"} 
* [`q-and-a_patient-chatbot-prescriptions-with-examples.yaml`]({{site.gh_edit_repository}}/blob/main/src/llm/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml){:target="_blank"} 

{: .highlight}
> If you aren't using a Linux or MacOS system or you can't use `llm` for any reason, you can use any inference service at your disposal with the system prompts in those YAML files and user prompts shown above. If the service doesn't provide a way to specify the system prompt separately, just combine it with the user prompt, e.g.,
>
> ```text
> system:
>   You are a helpful assistant for medical patients requesting help from their care provider. Some patients will request prescription refills. 
>   ...
>   
> prompt: I need a refill for my miracle drug.
> ```

Back to our results above; we effectively created _deterministic_ outputs for a narrow range of particular inputs! This suggests a design idea we should explore next.

### Idea: Handling Frequently Asked Questions

In this app, asking for a prescription refill is a _frequently asked question_ (FAQ). We observed that even small models, with a good system prompt, were able to &ldquo;map&rdquo; a range of similar questions to the same answer and even do appropriate substitutions in the text, the prescription in this case.

What other FAQs are there? Analyzing historical messages sent to providers is a good way to find other potential FAQs that might benefit from special handling, such as through the system prompt. When doing that historical analysis, you could use an LLM to group related questions, just like we did in our example, effectively. For other applications, there may very common prompts sent to a model that can benefit from special treatment.

A next, more sophisticated step in the design could be to build a _classifier_ model (see [Evaluation]({{site.glossaryurl}}/#evaluation) for a description), through which all messages are first passed. These tend to be small, efficient models, because they only need to output one or possibly more known labels, based on the input, and not output generated text. The model classifies each message into one of a fixed set of labels, one label for each FAQ and one for &ldquo;other&rdquo; messages, covering everything else. 

When a FAQ label is returned, a router sends the message to a low-cost model tuned specifically just for that FAQ. Or it might be sufficient to tune one model to handle all the FAQs, like we discovered meet our example's needs without requiring any special tuning. In contrast, the &ldquo;other&rdquo; messages would be routed to a smarter (and more expensive) model better able to handle more diverse content.

Finally, thinking in terms of a classifier suggests that we don't necessarily want to hard-code in the system prompt the deterministic answer the model should return. Instead, we should return just the label and any additional data of interest, like the drug name in our example. This answer could be formatted in JSONL, like for example the following:

```json
{"label": "refill-request", "drug-name": "miracle drug"}
```

Then the UI that presents the response to the user could format the actual response we want to show, where the format would be specified in a configuration file or runtime configuration option, so it is easy to change the response without changing the system prompt, etc. This would also make _internalization_ easier, where a configuration file with German strings is used for a German-speaking audience, for example. For internationalization, we may have to pick a properly _localized_ model for each target language our deployments support.

### Creating and Using Unit Benchmarks

The remaining four questions we posed above are these:

* How do we create these Q&A pairs?
* How do we run this &ldquo;unit test&rdquo;?
* How do we validate the resulting answers?
* How do we define &ldquo;pass/fail&rdquo; for this test?

In addition, we just discovered that we could have our models return a desired, _deterministic_ response for particular &ldquo;classes&rdquo; of prompts, like various ways of asking for prescription refills. This suggests two additional questions for follow up:

* How _diverse_ can the prompts be and still be correctly &ldquo;mapped&rdquo; by the LLM to the same desired response?
* If those edge cases aren't properly handled, what should we do?

Several of these questions share the requirement that we need a scalable and efficient way to create lots of high-quality Q&A pairs. One drawback to our experiment above was the way we manually created good Q&A pairs for testing. They were not comprehensive and it doesn't scale well for humans to do this work.

We need automated techniques for data _synthesis_ to scale up our tasks beyond the ad hoc approach we used above, especially as we add more and more tests. We also need automated techniques for validating the quality of our synthetic test data.

In [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks), we will explore these techniques and also discuss there how to run the unit benchmarks we create.

To automatically check the quality of synthetic Q&A test pairs, including how well each answer aligns with its question, we will explore techniques like [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) and [External Tool Verification]({{site.baseurl}}/testing-strategies/external-verification/).

Finally, [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests/) will help us decide what &ldquo;pass/fail&rdquo; means. We got _lucky_ in our example above; for our hand-written Q&A pairs, we were able to achieve a 100% pass rate (as long as it was okay to ignore capitalization of some words!). This convenient _certainty_ won't happen very often, especially if when we encounter edge cases.

---

Review the [highlights](#highlights) summarized above, then proceed to our discussion of [Component Design]({{site.baseurl}}/arch-design/component-design), a look at _coupling_ and _cohesion_ principles, and specific considerations for AI _components_.
