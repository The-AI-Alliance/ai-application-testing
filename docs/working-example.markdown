---
layout: default
title: The Working Example
nav_order: 50
has_children: false
---

# The Healthcare ChatBot Example Application and Exercises

{: .warning}
> **DISCLAIMER:** 
> 
> In this guide, we develop a healthcare ChatBot example application, chosen because it is a _worst case_ design challenge. Needless to say, but we will say it anyway, a ChatBot is notoriously difficult to implement successfully, because of the free-form prompts from users and the many possible responses models can generate. A healthcare ChatBot is even more challenging because of the risk it could provide bad responses that lead to poor patient outcomes, if applied. Hence, **this example is only suitable for educational purposes**. It is not at all suitable for use in real healthcare applications and **_it must not be used_** in such a context. Use it at your own risk.

This chapter summarizes how to run the tools and exercises using the Healthcare ChatBox example application. For convenience, it gathers in one place information spread across other chapters. See also the summary in the repo's [`README`]({{site.gh_edit_repository}}/){:target="readme"}. However, we don't repeat here the **Experiments to Try** sections found in various chapters.

The custom tools used try to strike a balance between being minimally-sufficient, in order to teach the concepts with minimal distractions, vs. being fully engineered for real-world, enterprise development and deployment, where more sophisticated tools would be better and other requirements, such as observability, are important. We have biased towards minimally-sufficient.

We welcome your [feedback](({{site.baseurl}}/contributing)) on our approach, as well as [contributions]({{site.baseurl}}/contributing). Are you able to adapt the tools to your development needs? Have you found it necessary to adopt other tools, but apply the techniques discussed here? How could we improve the tools and examples?

## Setup

{: .note}
> **NOTE:**
> 
> The `make` target processes discussed below assume you are using a MacOS or Linux shell environment like `zsh` or `bash`. However, the tools described below are written in Python, so the commands shown for running them should work on any operating system with minor adjustments, such as paths to files and directories. Let us know about your experiences: [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues){:target="issues"}, [discussions](https://github.com/The-AI-Alliance/ai-application-testing/discussions){:target="discussions"}.

Clone the project [repo](https://github.com/The-AI-Alliance/ai-application-testing/){:target="repo"} and run the following `make` command to do &ldquo;one-time&rdquo; setup steps, such as installing tools required or telling you how to install them. Assuming you are using MacOS or Linux and your current working directory is the repo root directory, run this command:

```shell
make one-time-setup 
```

If `make` won't work on your machine, do the following steps yourself:

* Install [`uv`](https://docs.astral.sh/uv/){:target="uv"}, a Python package manager. 
* Run the setup command `uv env` to install dependencies.
* Install [`ollama`](https://ollama.com){:target="ollama"} for local model inference (optional).

{:.tip}
> **TIPS:**
> 1. Try `make help` for details about the `make` process. There are also `--help` options for all the tools discussed below.
> 1. For any `make` target, to see what commands will be executed without running them, pass the `-n` or `--dry-run` option to `make`.
> 1. The `make` targets have only been tested on MacOS. Let us know if they don't work on Linux. The actual tools are written in Python for portability.
> 1. The repo [README](https://github.com/The-AI-Alliance/ai-application-testing/){:target="repo"} has an Appendix with other tools you might find useful to install.

One of the dependencies managed with `uv` is [`LiteLLM`](https://docs.litellm.ai/){:target="litellm"}, the library we use for flexible invocation of different inference services. See the `LiteLLM` [usage documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for how to set it up to use inference services other than local inference with `ollama`, if that is your preference.

### Pick Your Models

If you install `ollama`, download the models you want to use. In our experiments, we used the four models shown in **Table 1** (see also a similar table [here]({{site.baseurl}}/arch-design/tdd/#table-1)): 

| Model | # Parameters | Notes |
| :---- | -----------: | :---- |
| `gpt-oss:20b` | 20B | Excellent performance, but requires a lot of memory (see below). |
| `llama3.2:3B` | 3B | A small but effective model in the Llama family. Should work on most laptops. |
| `smollm2:1.7b-instruct-fp16` | 1.7B | The model family used in Hugging Face's [LLM course](https://huggingface.co/learn/llm-course/){:target="hf-llm-course"}, which we will also use to highlight some advanced concepts. The `instruct` label means the model was tuned for improved _instruction following_, important for ChatBots and other user-facing applications. |
| `granite4:latest` | 3B | Another small model tuned for instruction following and tool calling. |

**Table 1:** Models used for our experiments.

To install one or more of these models, use these commands (for any operating system and shell environment):

```shell
ollama pull gpt-oss:20b
ollama pull llama3.2:3B
ollama pull smollm2:1.7b-instruct-fp16
ollama pull granite4:latest
```

(Yes, some models use `B` and others use `b`, as shown...)

{: .attention}
> We provide example results for all these models in [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/src/data/examples/ollama){:target="examples"}. 

By default, we use `gpt-oss:20b` as our inference model, served by `ollama`. This is specified in the `Makefile` by defining the variable `MODEL` to be `ollama/gpt-oss:20b`. (Note the `ollama/` prefix.) All four models shown above are defined in the `MODELS` variable.

However, we found that `gpt-oss:20b` is too large for many developer machines. Specifically, we found that Apple computers with M1 Max chips with 32GB of memory were not sufficient for using `gpt-oss:20b` without &ldquo;bogging down&rdquo; the machine, while having 64GB of memory was sufficient. However, acceptable performance, especially for learning purposes, was achieved on 32GB machines when using the other, smaller models, which have 3B parameters or less. We encourage you to experiment with other model sizes and with different model families. Consider also [Quantized]({{site.glossaryurl}}/#quantization){:target="_glossary"} versions of models. Which choices work best for you?

### Changing the Default Model Used

If you don't want to use the default model setting, `gpt-oss:20b`, or you want to use a different inference option than `ollama`, there are two ways to specify your preferred model:

1. Edit [`src/Makefile`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/Makefile){:target="makefile"} and change the definition of `MODEL` to be your preferred choice, e.g., `ollama/llama3.2:3B`. This will make the change permanent for all examples. (The `ollama/` prefix is required if you are using `ollama`.) See the `LiteLLM` [documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for information about specifying models for other inference services.
1. Override the definition of `MODEL` on the command line when you run `make`, e.g., `make MODEL=ollama/llama3.2:3B run-tdd-example-refill-chatbot`. This is the easiest way to do &ldquo;one-off&rdquo; experiments with different models.

If you want to try _all_ four models mentioned above with one command, use `make all-models-...`, where `...` is one of the other make targets, like `all-code`, which runs all the tool invocations for a single model, e.g.,

```shell
make all-models-all-code
```

You can also change the list of models you regularly want to use by changing the definition of the `MODELS` variable in the `Makefile`.

{: .note}
> **NOTE:**
>
> See the [LiteLLM documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for guidance on how to specify models for different inference services. If you use a service other than `ollama`, you will need to be sure the required variables are set in your environment, e.g., API keys, and you may need to change the arguments passed in our Python scripts to the LiteLLM `completion` function. We plan to make this more [&ldquo;automatic&rdquo;](https://github.com/The-AI-Alliance/ai-application-testing/issues/20){:target="issues"}.

## Running the Exercises with `make`

On MacOS and Linux, using `make` is the easiest way to run the exercises. The actual commands are printed out and we repeat them below for those of you on other platforms. Hence, you can also run the Python scripts directly without using `make`. 

{: .tip}
> **TIPS:**
>
> 1. For all the individual tool-invocation `make` commands discussed from now on, you can run each one for _all_ the models by prefixing the target name with `all-models-`, e.g., `all-models-run-tdd-example-refill-chatbot`.
> 1. For a given model (as defined by the `Makefile` variable `MODEL`), you can run all of the tools with one command, `make all-code`. You can run all the examples for all the models discussed above using `make all-models-all-code`.

## Run `tdd-example-refill-chatbot`

This example is explained in the section on [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/).

Run this `make` command:

```shell
make run-tdd-example-refill-chatbot 
```

There are shorthand "aliases" for this target:

```shell
make run-terc
make terc
```

This target first checks the following:

* The `uv` command is installed and on your path.
* Two directories defined by `make` variables exist. If not, they are created with `mkdir -p`, where the option `-p` ensures that missing parent directories are also created:
	* `OUTPUT_LOG_DIR`, where most output is written, which is `temp/output/ollama/gpt-oss_20b/logs`, when `MODEL` is defined to be `ollama/gpt-oss:20b`. (The `:` is converted to `_`, because `:` is not an allowed character in MacOS file system names.) Because `MODEL` has a `/`, we end up with a directory `ollama` that contains a `gpt-oss_20b` subdirectory.
	* `OUTPUT_DATA_DIR`, where data files are written, which is `temp/output/ollama/gpt-oss_20b/data`, when `MODEL` is defined to be `ollama/gpt-oss:20b`. 

If you don't use the `make` command, make sure you have `uv` installed and either manually create the same directories or modify the corresponding paths shown in the next command.

After the setup, the `make` target runs the following command:

```shell
time uv run src/scripts/tdd-example-refill-chatbot.py \
	--model ollama/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir src/prompts/templates \
	--data-dir temp/output/ollama/gpt-oss_20b/data \
	--log-file temp/output/ollama/gpt-oss_20b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log
```

`TIMESTAMP` will be the current time when the `uv` command started, of the form `YYYYMMDD-HHMMSS`.

The `time` command prints execution time information for the `uv` command. It is optional and you can omit it when running this command directly yourself.

The `time` command returns how much system, user, and "wall clock" times were used for execution on MacOS and Linux systems. You can omit it when running this command directly yourself or when using a system that doesn't support it. Note that `uv` is used to run `src/scripts/tdd-example-refill-chatbot.py`. 

The arguments are as follows:

| Argument | Purpose |
| :------- | :------ |
| `--model ollama/gpt-oss:20b` | The model to use, defined by the `make` variable `MODEL`, as discussed above. |
| `--service-url http://localhost:11434` | The `ollama` local server URL. Some other inference services may also require this argument. |
| `--template-dir src/prompts/templates` | Where we keep prompt templates we use for all the examples. |
| `--data-dir temp/output/ollama/gpt-oss_20b/data` | Where any generated data files are written. (Not used by all tools.) |
| `--log-file temp/output/ollama/gpt-oss_20b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log` | Where log output is captured. |

{: .tip}
> **TIP:**
>
> If you want to save the outputs of the tool invocations for a particular `MODEL` value, run `make save-examples`. It will create a subdirectory of  run to `src/data/examples/` for the model used and copy the results there. Hence, you have to specify the desired model, e.g., `make MODEL=ollama/llama3.2:3B save-examples`. To save the outputs for all the models defined by `MODELS`, use `make all-models-save-examples`. We have included example outputs for the four models discussed previously in the repo. The `.log` files that capture command output are also saved.

The `tdd-example-refill-chatbot.py` tool runs two experiments, one with the template file [`q-and-a_patient-chatbot-prescriptions.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions.yaml){:target="_blank"} and the other with [`q-and-a_patient-chatbot-prescriptions-with-examples.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml){:target="_blank"}. The only difference is the second file contains embedded examples in the prompt, so in principal the results should be better, but in fact, they are often the same, as discussed in the [TDD chapter]({{site.baseurl}}/arch-design/tdd/).

{: .note}
> **NOTE:**
>
> These template files were originally designed for use with the `llm` CLI tool (see the Appendix in the repo's [`README`]({{site.gh_edit_repository}}/){:target="readme"} for details about `llm`). In our Python scripts, [LiteLLM](https://docs.litellm.ai/#basic-usage){:target="_blank"} is used instead to invoke inference. We extract the content we need from the templates and construct the prompts we send through LiteLLM.

The `tdd-example-refill-chatbot.py` tool passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. As the [TDD chapter]({{site.baseurl}}/arch-design/tdd/) explains, this is a very ad-hoc approach to creating and testing a _unit benchmark_.

## Run `unit-benchmark-data-synthesis`

Described in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/){:target="ub"}, this script uses an LLM to generate Q&A (question and answer) pairs for _unit benchmarks_. It addresses some of the limitations of the more ad-hoc approach to benchmark creation used in the previous TDD exercise:

```shell
make run-unit-benchmark-data-synthesis
```

There are shorthand "aliases" for this target:

```shell
make run-ubds
make ubds
```

After the same setup steps as before, the following command is executed:

```shell
time uv run src/scripts/unit-benchmark-data-synthesis.py \
	--model ollama/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir src/prompts/templates \
	--data-dir temp/output/ollama/gpt-oss_20b/data \
	--log-file temp/output/ollama/gpt-oss_20b/logs/${TIMESTAMP}/unit-benchmark-data-synthesis.log
```

{: .note}
> **NOTE:**
>
> If you run the previous tool command, then this one, the two values for `TIMESTAMP` will be different. However, when you make `all-code` or any `all-models-*` target, the _same_ value will be used for `TIMESTAMP` for all the invocations.

The arguments are the same as before, but in this case, the `--data-dir` argument specifies the location where the Q&A pairs are written, one file per unit benchmark, with subdirectories for each model used. For example, after running this script with `ollama/gpt-oss:20b`, `temp/output/data/ollama/gpt-oss_20b` (recall that `:` is an invalid character for MacOS file paths, so we replace it with `_`) will have these files of synthetic Q&A pairs:

* `synthetic-q-and-a_patient-chatbot-emergency-data.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`

(Examples can be found in the repo's [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama){:target="examples"} directory.)

They cover three unit-benchmarks:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should stop using the ChatBot and call 911 (in the US) immediately.
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

The prompt used tells the model to return one of these _classification_ labels, along with some additional information, rather than an ad-hoc, generated text like, "It sounds like you are having an emergency. Please call 911..."

Each of these data files are generated with a single inference invocation, with each invocation using these corresponding template files:

* [`synthetic-q-and-a_patient-chatbot-emergency.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency.yaml){:target="yaml1"}
* [`synthetic-q-and-a_patient-chatbot-prescription-refills.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills.yaml){:target="yaml2"}
* [`synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml){:target="yaml3"}

## Run `unit-benchmark-data-validation`

Described in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/){:target="laaj"}, this script uses a _teacher model_ to _validate_ the quality of the Q&A pairs that were generated in the previous exercise:

```shell
make run-unit-benchmark-data-validation
```

There are shorthand "aliases" for this target:

```shell
make run-ubdv
make ubdv
```

After the same setup steps, the following command is executed:

```shell
time uv run src/scripts/unit-benchmark-data-validation.py \
	--model ollama/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir src/prompts/templates \
	--data-dir temp/output/ollama/gpt-oss_20b/data \
	--log-file temp/output/ollama/gpt-oss_20b/logs/TIMESTAMP/unit-benchmark-data-validation.log \
```

In this case, the `--data-dir` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory:

* `synthetic-q-and-a_patient-chatbot-emergency-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.yaml`

(See examples in [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama){:target="examples"}.)

These files &ldquo;rate&rdquo; each Q&A pair from 1 (bad) to 5 (great).
Also, summary statistics are written to `stdout` and to the output file `temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out`. Currently, we show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. (For simplicity, we used the same `gpt-oss:20b` model as the _teacher_ that we used for generation.) From one of our test runs a text version of the following table was written:

Files:                                                                            |    1  |    2  |    3  |    4  |    5  | Total |
| :------                                                               | ----: | ----: | ----: | ----: | ----: | ----: |
synthetic-q-and-a_patient-chatbot-emergency-data.json                             |    0  |    4  |    7  |   12  |  168  |  191  |
synthetic-q-and-a_patient-chatbot-prescription-refills-data.json                  |    0  |    0  |    0  |    0  |  108  |  108  |
synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json              |    2  |    2  |    0  |    1  |  168  |  173  |
| | | | | | | |
Totals:                                                                           |    2  |    6  |    7  |   13  |  444  |  472  |

Total count: 475 (includes errors), total errors: 3

The teacher model is asked to provide _reasoning_ for its ratings. It is instructive to look at the output `*-validation.yaml` files that we saved in [`src/data/examples/ollama/gpt-oss_20b/data/`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama/gpt-oss_20b/data/){:target="examples"}.

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). 

In fact, the program deliberately ignores the actual file where the Q&A pair appears. For example, we found that the _emergency_ file contains some _refill_ and _other_ questions. Only the actual label in the answer corresponding to a question was evaluated. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. You could decide to resort all the data by label to keep them separated by use case or you could just concatenate all the Q&A pairs into one big set. We think the first choice is more in the spirit of how focused, automated, use-case specific tests are supposed to work, but it is up to you...

The same template file was used for evaluating the three data files:

* [`synthetic-q-and-a_patient-chatbot-data-validation.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml){:target="yaml"}

## Planned Additions

{: .todo}
> **TODO:**
>
> We intend to add additional content here covering the following topics.
> * Where each tool and process fits into the software development lifecycle.
> * Integration of our new tools into existing process frameworks, e.g., running _unit benchmarks_  integrated with [PyTest](https://docs.pytest.org/en/stable/){:target="_blank"} and similar tools.
> * ...

### Integration into the Software Development Lifecycle

TODO

### Writing Tests During Test-Driven Development

TODO

### Integration into Test Suites

TODO: Discuss integration into PyTest and other frameworks.
