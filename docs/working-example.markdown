---
layout: default
title: The Working Example and Tools
nav_order: 50
has_children: false
---

# Using the Healthcare ChatBot Example Application and Tools

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

{: .warning}
> **DISCLAIMER:** 
> 
> In this guide, we develop a healthcare ChatBot example application, chosen because it is a _worst case_ design challenge. Needless to say, but we will say it anyway, a ChatBot is notoriously difficult to implement successfully, because of the free-form prompts from users and the many possible responses models can generate. A healthcare ChatBot is even more challenging because of the risk the ChatBot could provide bad advice that leads to a poor patient outcome, if followed. Hence, **this example is only suitable for educational purposes**. It is not at all suitable for use in real healthcare applications and **_it must not be used_** in such a context. Use it at your own risk.

{: .tip}
> **TIP:** To see the discussion about using _unit benchmarks_ in the software development life cycle, [jump to here](#automated-testing-practical-enhancements).

## The User Guide Tools and Exercises vs. the ChatBot Application

The tools and exercises in this user guide are written with an emphasis on teaching concepts, with minimal distractions, with less concern about being fully engineered for real-world, enterprise development and deployment, where more sophisticated tools might be needed.

In contrast, the Healthcare ChatBox example application applies the concepts in a more &ldquo;refined&rdquo; implementation that also illustrates how existing software development practices and new AI-oriented techniques can be used together in a real software-development project.

For convenience, this chapter gathers in one place information spread across other chapters. See also the discussion in the repo's [`README`]({{site.gh_edit_repository}}/){:target="readme"}. 

We welcome your [feedback](({{site.baseurl}}/contributing)) on our approach, as well as [contributions]({{site.baseurl}}/contributing). Are you able to adapt the tools to your development needs? Have you found it necessary to adopt other tools, but apply the techniques discussed here? How could we improve the tools and examples?

## Setup

{: .note}
> **NOTE:**
> 
> The `make` target processes discussed below assume you are using a MacOS or Linux shell environment like `zsh` or `bash`. However, the tools described below are written in Python, so the commands shown for running them should work on any operating system with minor adjustments, such as paths to files and directories. Let us know about your experiences: [issues]({{site.gh_edit_repository}}/issues){:target="issues"}, [discussions]({{site.gh_edit_repository}}/discussions){:target="discussions"}.

Whether using the tools or the example application, you start by setting up the required dependencies, etc.

Clone the project [repo]({{site.gh_edit_repository}}/){:target="repo"}, change to the `ai-application-testing` directory, and run the following `make` command to do &ldquo;one-time&rdquo; setup steps:

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
> 1. For any `make` target, to see what commands will be executed without running them, pass the `-n` or `--dry-run` option to `make`. While we try to keep this documentation consistent with the implementations. This is the best way to confirm the correct way to run the various programs.
> 1. The `make` targets have only been tested on MacOS. Let us know if they don't work on Linux. The actual tools are written in Python for portability.
> 1. The repo [README]({{site.gh_edit_repository}}/){:target="repo"} has an Appendix with other tools you might find useful to install.

One of the dependencies managed with `uv` is [`LiteLLM`](https://docs.litellm.ai/){:target="litellm"}, the library we use for flexible invocation of different inference services. All our development has been done using `ollama` for cost-benefit and flexibility reasons, but it is not required if you want to use an inference provider instead, like OpenAI or Anthropic. In that case, see the `LiteLLM` [usage documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for how to configure `LiteLLM` to use your preferred inference service. You will need to modify the `Makefile`, as discussed in [Changing the Default Model Used](#changing-the-default-model-used) below.

### Pick Your Models

If you use `ollama`, download the models you want to use. For example:

```shell
ollama serve            # in one terminal window
ollama pull gemma4:e4b  # in another terminal window
```

In our experiments, we used the models shown in **Table 1** (see also a similar table [here]({{site.baseurl}}/arch-design/tdd/#table-1)): 

<a id="table-1"></a>

| Model | Parameters | Memory | Hugging Face | Ollama | Description |
| :---- | ---------: | -----: | :----------- | :----- | :---------- |
| `gemma4:e4b`  |  8 B | 11 GB | [link](https://huggingface.co/blog/gemma4){:target="hf-gemma4"} | [link](https://ollama.com/library/gemma4){:target="ollama-gemma4"} |  **Default model used in the `Makefile`.** Excellent performance, requiring about 11 GB, so it provides a good balance between performance and efficiency. The larger `gemma4` models available, `26b` and `31b` work even better, but require much more memory. |
| `gpt-oss:20b` | 20 B | 14 GB | [link](https://huggingface.co/openai/gpt-oss-20b){:target="hf-gpt-oss"} | [link](https://ollama.com/library/gpt-oss:20b){:target="ollama-gpt-oss"} | Excellent performance, with slightly more memory required. However, at this time, this model doesn't work with the agent ChatBot implementation, which uses [LangChain's Deep Agents](https://docs.langchain.com/oss/python/deepagents/) framework. See [this LangChain issue](https://github.com/langchain-ai/langchain/issues/33116) for details. |
| `qwen3.5:35b` | 35 B | 27 GB | [link](https://huggingface.co/models?sort=trending&search=qwen3.5){:target="hf-qwen3.5"} | [link](https://ollama.com/library/qwen3.5){:target="ollama-qwen"} | Excellent performance, but requires about 27 GB of memory. |
| `llama3.2:3B` |  3 B | 7.5 GB | [link](https://huggingface.co/meta-llama/Llama-3.2-3B){:target="hf-llama32"} | [link](https://ollama.com/library/llama3.2:3b){:target="ollama-llama32"} | A small but effective model in the Llama family. A good choice during development when overhead is more important than performance. |
| `granite4:latest` | 3B | 7 GB | [link](https://huggingface.co/ibm-granite/granite-4.0-micro){:target="hf-granite4"} | [link](https://ollama.com/library/granite4:latest){:target="ollama-granite4"} | Another small model tuned for instruction following and tool calling. |
| `smollm2:1.7b-instruct-fp16` | 1.7B | 5.6 GB | [link](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct){:target="hf-smallm2"} | [link](https://ollama.com/library/smollm2:1.7b-instruct-fp16){:target="ollama-smollm2"} | The model family used in Hugging Face's [LLM course](https://huggingface.co/learn/llm-course/){:target="hf-llm-course"}, which we plan to use to highlight some advanced concepts. The `instruct` label means the model was tuned for improved _instruction following_, important for ChatBots and other user-facing applications. |

**Table 1:** The models we used for experimenting.

(Yes, some models use `B` and others use `b`...)

{: .tip}
> **REQUEST:** [Let us know]({{site.baseurl}}/contributing#join-us) which models work well for you!

**Table 1:** Models used for our experiments.

{: .attention}
> We provide example results for some of these models in [`src/data/examples/ollama_chat`]({{site.gh_edit_repository}}/blob/main/src/data/examples/ollama_chat){:target="examples"}. 

By default, we use `gemma4:e4b` as our inference model, served by `ollama`. Previously, we used `gpt-oss:20b`, but switched due to [this LangChain issue](https://github.com/langchain-ai/langchain/issues/33116). This is specified in the `Makefile` by defining the variable `MODEL` to be `ollama_chat/gemma4:e4b`. (Note the `ollama_chat/` prefix.) All the models shown above are defined in the `MODELS` variable; there are `all-models-*` targets that try all of them.

We find that `gemma4:e4b`, requiring about 11 GB of memory performs reasonably well on a MacBook Pro with an M1 Max chips and 32GB of memory. The slightly larger `gpt-oss:20b` can be slower, especially if lots of other apps are using significant memory. 48 GB or 64 GB of memory is much better for both models and also supports larger models more easily.

We encourage you to experiment with other model sizes and with different model families. Consider also [Quantized]({{site.glossaryurl}}/#quantization){:target="_glossary"} versions of models. It is worth the time to experiment with different models to find the ones that work best for your development environment and production deployments.

### Changing the Default Model Used

If you don't want to use the default model, `gemma4:e4b`, served by `ollama`, you can change the definition of `MODEL` in the `Makefile` in one of several ways.

If you want to use a different inference option other than `ollama`, first see the `LiteLLM` [documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for information about specifying models for other inference services. In most cases, it will be as simple as changing a few definitions in the `Makefile` (discussed next).

There are two ways to specify your preferred model in the `Makefile`:

#### Edit the Makefile

Edit the [`Makefile`]({{site.gh_edit_repository}}/tree/main/Makefile){:target="makefile"} and change the following definitions:

* `MODEL` - e.g., `ollama_chat/llama3.2:3B`. This will change the default for all invocations of the tools and the example ChatBot app. (The `ollama_chat/` or `ollama/` prefix is required if you are using `ollama`, with `ollama_chat/` recommended by `LiteLLM`.) For convenience, we defined several `MODEL_*` variables for different models, then refer to the one we want when defining `MODEL`. You can do this if you like...
* `INFERENCE_SERVICE` - e.g., `openai`, `anthropic`, `ollama`.
* `INFERENCE_URL` - e.g., `http://localhost:11434` for `ollama` or `https://api.openai.com/v1` for OpenAI.
* Others? The `LiteLLM` documentation may tell you to define other variables. You will most likely need an API key or other credentials for hosted services, like OpenAI and Anthropic. **_Do not put this information in the Makefile!_** This avoids the risk that you will accidentally commit secrets to a repo. Instead, use an environment variable or other solution described by the `LiteLLM` documentation.

#### Override Makefile Definitions on the Command Line

On invocation, you can dynamically change values, such as the `MODEL` used with `ollama`. This is the easiest way to do &ldquo;one-off&rdquo; experiments with different models. For example:

```shell
make MODEL=ollama_chat/llama3.2:3B chatbot
```

If you want to try _all_ the models mentioned above with one command, use `make all-models-...`, where `...` is one of the other make targets, like `all-code`, which runs all the tool invocations for a single model, e.g.,

```shell
make all-models-all-chatbot
```

You can also change the list of models you regularly want to use by changing the definition of the `MODELS` variable in the `Makefile`.

{: .note}
> **NOTE:**
>
> See also the [LiteLLM documentation](https://docs.litellm.ai/#basic-usage){:target="litellm"} for guidance on any required modifications to the arguments passed in our Python code to the LiteLLM `completion` function. (Search for `response = completion` to find all the occurrences.) We plan to [implement automatic handling]({{site.gh_edit_repository}}/issues/20){:target="issues"} of such changes eventually.

## Running the Tools and ChatBot Application with `make`

Now you are set up and you can use `make` to run the tools discussed and also the complete example ChatBot application. We will discuss the tools first, then the application.

On MacOS and Linux, using `make` is the easiest way to run the exercises. The actual commands are printed out and we repeat them below for those of you on other platforms. Hence, you can also run the Python tools directly without using `make`. 

{: .tip}
> **TIPS:**
>
> 1. For all of the tool-invocation `make` commands discussed from now on, you can run each one for _all_ the models (as defined by the `Makefile` variable `MODELS`) by prefixing the target name with `all-models-`, e.g., `all-models-run-tdd-example-refill-chatbot`. You can use it for most targets, although it doesn't make sense for some of them, like the `help-*` targets and the ChatBot application, which is interactive.
> 1. For a given model (as defined by the `Makefile` variable `MODEL`), you can run all of the tools with one command, `make all-code`. Hence, you can run all the examples for all the models discussed above using `make all-models-all-code`. (This target doesn't run the ChatBot application.)

### Run `tdd-example-refill-chatbot`

This tool is explained in the section on [Test-Driven Development]({{site.baseurl}}/arch-design/tdd/). It introduces some concepts, but isn't intended to be a tool you use long term, in contrast to the next two `unit-benchmark-data-*` tools discussed below.

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
	* `OUTPUT_LOG_DIR`, where most output is written, which is `temp/output/ollama_chat/gemma4_e4b/logs`, when `MODEL` is defined to be `ollama_chat/gemma4:e4b`. (The `:` is converted to `_`, because `:` is not an allowed character in MacOS file system names.) Because `MODEL` has a `/`, we end up with a directory `ollama_chat` that contains a `gemma4_e4b` subdirectory.
	* `OUTPUT_DATA_DIR`, where data files are written, which is `temp/output/ollama_chat/gemma4_e4b/data`. 

If you don't use the `make` command, make sure you have `uv` installed and either manually create the same directories or modify the corresponding paths shown in the next command.

After the setup, the `make` target runs the following command:

```shell
cd src && time uv run tools/tdd-example-refill-chatbot.py \
	--model ollama_chat/gemma4:e4b \
	--service-url http://localhost:11434 \
	--template-dir tools/prompts/templates \
	--data-dir .../output/ollama_chat/gemma4_e4b/data \
	--log-file .../output/ollama_chat/gemma4_e4b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log
```

`TIMESTAMP` will be the current time when the `uv` command started, of the form `YYYYMMDD-HHMMSS`, and the values passed for `--data-dir` and `--log-file` are absolute paths. The other paths shown are relative to the `src` directory.

The `time` command prints execution time information for the `uv` command. It is optional and you can omit it when running this command directly yourself or on a system without this command. It returns how much system, user, and "wall clock" times were used for execution on MacOS and Linux systems. Note that `uv` is used to run `tools/tdd-example-refill-chatbot.py`. 

The arguments are as follows:

<a id="table-2"></a>

| Argument | Purpose |
| :------- | :------ |
| `--model ollama_chat/gemma4:e4b` | The model to use, defined by the `make` variable `MODEL`, as discussed above. |
| `--service-url http://localhost:11434` | The `ollama` local server URL. Some other inference services may also require this argument. |
| `--template-dir tools/prompts/templates` | Where we keep prompt templates we use for all the examples. |
| `--data-dir .../output/ollama_chat/gemma4_e4b/data` | Where any generated data files are written. (Not used by all tools.) |
| `--log-file .../output/ollama_chat/gemma4_e4b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log` | Where log output is captured. |

**Table 2:** Arguments passed to `tools/tdd-example-refill-chatbot.py`.

The `tdd-example-refill-chatbot.py` tool runs two experiments, one with the template file [`q-and-a_patient-chatbot-prescriptions.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/q-and-a_patient-chatbot-prescriptions.yaml){:target="_blank"} and the other with [`q-and-a_patient-chatbot-prescriptions-with-examples.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml){:target="_blank"}. The only difference is the second file contains embedded examples in the prompt, so in principal the results should be better, but in fact, they are often the same, as discussed in the [TDD chapter]({{site.baseurl}}/arch-design/tdd/).

{: .note}
> **NOTE:**
>
> These template files were originally designed for use with the `llm` CLI tool (see the Appendix in the repo's [`README`]({{site.gh_edit_repository}}/){:target="readme"} for details about `llm`). In our Python tools, [LiteLLM](https://docs.litellm.ai/#basic-usage){:target="_blank"} is used instead to invoke inference. We extract the content we need from the templates and construct the prompts we send through LiteLLM.

The `tdd-example-refill-chatbot.py` tool passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. As the [TDD chapter]({{site.baseurl}}/arch-design/tdd/) explains, this is a very ad-hoc approach to creating and testing a _unit benchmark_.

### Run `unit-benchmark-data-synthesis`

Described in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/){:target="ub"}, this tool uses an LLM to generate Q&A (question and answer) pairs for _unit benchmarks_. It addresses some of the limitations of the more ad-hoc approach to benchmark creation used in the previous TDD exercise:

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
cd src && time uv run tools/unit-benchmark-data-synthesis.py \
	--model ollama_chat/gemma4:e4b \
	--service-url http://localhost:11434 \
	--template-dir tools/prompts/templates \
	--data-dir .../output/ollama_chat/gemma4_e4b/data \
	--log-file .../output/ollama_chat/gemma4_e4b/logs/${TIMESTAMP}/unit-benchmark-data-synthesis.log
```

{: .note}
> **NOTE:**
>
> If you run the previous tool command, then this one, the two values for `TIMESTAMP` will be different. However, when you make `all-code` or any `all-models-*` target, the _same_ value will be used for `TIMESTAMP` for all the invocations.

The arguments are the same as before, e.g., the `--data-dir` argument specifies the location where the Q&A pairs are written, one file per unit benchmark, with subdirectories for each model used. For example, after running this tool with `ollama_chat/gemma4:e4b`, the output will be in `.../output/data/ollama_chat/gemma4_e4b`, as discussed previously. This directory will have the following files of synthetic Q&A pairs:

* `synthetic-q-and-a_patient-chatbot-emergency-data.jsonl`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.jsonl`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data.jsonl`

(Examples can be found in the repo's [`src/data/examples/ollama_chat`]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat){:target="examples"} directory.)

They cover three unit-benchmarks:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should stop using the ChatBot and call 911 (in the US) immediately.
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

The prompt used tells the model to return one of these _classification_ labels, along with some additional information, rather than an ad-hoc, generated text like, "It sounds like you are having an emergency. Please call 911..."

Each of these data files are generated with a single inference invocation, with each invocation using these corresponding template files:

* [`synthetic-q-and-a_patient-chatbot-emergency.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency.yaml){:target="yaml1"}
* [`synthetic-q-and-a_patient-chatbot-prescription-refills.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills.yaml){:target="yaml2"}
* [`synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml){:target="yaml3"}

### Run `unit-benchmark-data-validation`

Described in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/){:target="laaj"}, this tool uses a _teacher model_ to _validate_ the quality of the Q&A pairs that were generated in the previous exercise:

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
cd src && time uv run tools/unit-benchmark-data-validation.py \
	--model ollama_chat/gemma4:e4b \
	--service-url http://localhost:11434 \
	--template-dir tools/prompts/templates \
	--data-dir .../output/ollama_chat/gemma4_e4b/data \
	--log-file .../output/ollama_chat/gemma4_e4b/logs/TIMESTAMP/unit-benchmark-data-validation.log \
```

In this case, the `--data-dir` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory:

* `synthetic-q-and-a_patient-chatbot-emergency-data-validation.jsonl`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.jsonl`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.jsonl`

(See examples in [`src/data/examples/ollama_chat`]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat){:target="examples"}.)

These files &ldquo;rate&rdquo; each Q&A pair from 1 (bad) to 5 (great).
Also, summary statistics are written to `stdout` and to the output file `temp/output/ollama_chat/<model>/unit-benchmark-data-validation.out`. Currently, we show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. For simplicity, we used the same model as the _teacher_ that we used for generation, but for real use, consider using a different model. 

From one of our test runs a text version of the following table was printed:

<a id="table-3"></a>

Files:                                                                            |    1  |    2  |    3  |    4  |    5  | Total |
| :------                                                               | ----: | ----: | ----: | ----: | ----: | ----: |
synthetic-q-and-a_patient-chatbot-emergency-data.jsonl                            |    0  |    4  |    7  |   12  |  168  |  191  |
synthetic-q-and-a_patient-chatbot-prescription-refills-data.jsonl                 |    0  |    0  |    0  |    0  |  108  |  108  |
synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.jsonl             |    2  |    2  |    0  |    1  |  168  |  173  |
| | | | | | | |
Totals:                                                                           |    2  |    6  |    7  |   13  |  444  |  472  |

**Table 3:** Example results for ratings.

Total count: 475 (includes errors), total errors: 3

The teacher model is asked to provide _reasoning_ for its ratings. It is instructive to look at the output `*-validation.jsonl` files that we saved in [`src/data/examples/ollama_chat/gpt-oss_20b/data/`]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/){:target="examples"}.

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). 

In fact, the program deliberately ignores the actual file where the Q&A pair appears. For example, we found that the _emergency_ file contains some _refill_ and _other_ questions. Only the actual label in the answer corresponding to a question was evaluated. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. You could decide to resort all the data by label to keep them separated by use case or you could just concatenate all the Q&A pairs into one big set. We think the first choice is more in the spirit of how focused, automated, use-case specific tests are supposed to work, but it is up to you...

The same template file was used for evaluating the three data files:

* [`synthetic-q-and-a_patient-chatbot-data-validation.yaml`]({{site.gh_edit_repository}}/tree/main/src/tools/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml){:target="yaml"}

### Run the Langflow Pipeline for the Tools

The unit benchmark data synthesis and validation tools can also be executed as a [Langflow](https://www.langflow.org/){:target="langflow"} pipeline. See [`src/tools/langflow/README.md`]({{site.gh_edit_repository}}/tree/main/src/tools/langflow/README.md){:target="langflow-gh"} for details.

## Run the ChatBot Example Application

This purpose of this application is to represent something closer to what you would actually build, with a growing suite of automated unit and integration tests corresponding to incrementally added features. 

There are actually _two_ implementations of this application:

* [`ChatBotSimple`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/apps/chatbot/chatbot_simple.py){:target="cba-gh"} - A "simple" implementation that just uses LLM inference wrapped with some custom Python code, but without agent tools. This is the first version of the ChatBot that we started with while developing the initial content of this guide.
* [`ChatBotAgent`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/apps/chatbot/chatbot_agent.py){:target="cba-gh"} - A more advanced "agent" implementation that uses [Langchain's _Deep Agents_](https://www.langchain.com/deep-agents){:target="lcda"} tools for more advanced behaviors, like using _agent skills_ to define new behaviors.

A command-line argument `--which-chatbot` is used with a shared code base to select which implementation to use. By default, the `Makefile` targets use `ChatBotAgent`, which is selected because the `Makefile` variable `WHICH_CHATBOT` is defined to be `agent`. This value is overridden by `*-`, but it can be overridden on the command line with the value `simple` to use the other implementation.

{: .note}
> **NOTE:** The test suite for the ChatBot application demonstrates how to apply the ideas and techniques discussed in this guide to actual projects. 

The application can be invoked in one of several ways:

```shell
make chatbot               # Run the interactive ChatBot, agent implementation by default.
make run-chatbot           # Synonym for "chatbot".
make agent-chatbot         # Run the agent implementation ChatBot, explicitly.
make simple-chatbot        # Run the "simple" implementation ChatBot.
```

After the same setup steps, like output directory creation, the following command is executed, which you could also run directly, where we show the values for arguments as defined by `Makefile` variables:

```shell
cd src && time uv run python -m apps.chatbot.main \
  --model ollama_chat/gemma4:e4b \
  --service-url http://localhost:11434 \
  --template-dir tools/prompts/templates \
  --data-dir data \
  --output-dir output \
  --confidence-threshold 0.9 \
  --which-chatbot agent \
  --log-file .../logs/.../chatbot.log
```

{: .tip}
> **TIP:** Using the [Open WebUI](#using-the-chatbot-with-open-webui) GUI is recommended for experimenting with the ChatBot.

For help on the application, try this:

```shell
make help-chatbot          # Help on the interactive ChatBot, agent implementation by default.
make help-agent-chatbot    # Help on the agent implementation ChatBot, explicitly.
make help-simple-chatbot   # Help on the "simple" implementation ChatBot.
```

A text prompt is presented where you can enter &ldquo;patient prompts&rdquo; and see the replies. 

The arguments are similar to the previously-discussed arguments, with two new arguments, `--output-dir`, for writing some output during execution, and `--confidence-threshold`, to set how the confident the application needs to be in its answers before or else it should default to &ldquo;safe&rdquo;, generic handling. We discuss this concept in more detail below.

The source code, etc. for this application and the automated tests are located in these locations:

<a id="table-4"></a>

| Content | Location | Notes |
| :------ | :------- | :---- |
| Source code       | [`src/apps/chatbot`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/){:target="chatbot"} | Main source code for the ChatBot and the MCP server. |
| Agent Skills      | [`src/apps/chatbot/skills`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/skills/){:target="skills"} | Skills for the Deep Agent implementation, including the appointment management skill. |
| Prompt Templates  | [`src/apps/chatbot/prompts/templates`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/prompts/templates/){:target="prompts-chatbot"} | The prompts used by the ChatBot application and related tests. There are different prompts for the "simple" vs. "agent" implementations. |
| Unit Tests        | [`src/tests/unit/`]({{site.gh_edit_repository}}/tree/main/src/tests/unit//){:target="utests"} | Conventional unit tests and AI-specific tests for the chatbot in [`src/tests/unit/apps/chatbot`]({{site.gh_edit_repository}}/tree/main/src/tests/unit/apps/chatbot/){:target="utests"} .The AI-specific tests are executed with both ChatBot implementations. |
| Integration Tests | [`src/tests/integration/`]({{site.gh_edit_repository}}/tree/main/src/tests/integration/){:target="utests"} | The `make` target `integration-tests` also runs the unit tests in a more _exhaustive_ way, as discussed below. |
| Test Data         | [`src/tests/data`]({{site.gh_edit_repository}}/tree/main/src/tests/data/){:target="test-data"} | Test Q&A data for the AI tests. |
| Test Logs         | `src/tests/logs/${MODEL_FILE_NAME}` | Special log output for easier examination of AI-related test results, where `MODEL_FILE_NAME` will be `ollama_chat/gemma4_e4b`, by default. It is computed from the value of the `MODEL` variable, where any colons are replaced with underscores. |

**Table 4:** Locations for code, data, templates, etc. for the ChatBot application.

### Appointment Management Feature

The ChatBot Agent implementation includes a simple appointment management skill for demonstration purposes, implemented using LangChain's Deep Agents "skills" feature. This skill allows patients to:

- **Schedule appointments**: Create new appointments during weekday business hours
- **Cancel appointments**: Cancel existing appointments  
- **Confirm appointments**: Confirm scheduled appointments
- **Change appointments**: Reschedule to a different time
- **List appointments**: View all scheduled appointments

The appointment system enforces the following business rules:

- Appointments must be scheduled on the hour (e.g., 10:00, 11:00, not 10:30)
- Only weekdays (Monday-Friday) are available
- Common USA holidays are excluded
- Only one patient per time slot

The appointment data is stored in a JSONL file (`data/appointments.jsonl`) that persists across sessions.

#### Testing the Appointment Feature

Unit tests for the appointment tool can be run with:

```shell
make unit-tests-appointments
```

These tests verify all appointment operations including creation, cancellation, confirmation, rescheduling, and validation of business rules using Test-Driven Development (TDD) principles.


We will discuss the automated tests below, in [Automated Testing: Practical Enhancements](#automated-testing-practical-enhancements).

### Using the ChatBot with Open WebUI

If you prefer using a GUI instead of the CLI prompt for the ChatBot, an integration is provided with [Open WebUI](https://docs.openwebui.com){:target="open-webui"}.

{: tip}
> **TIP:**
> While it is tedious to set this up, once configured this is the most effective way to experiment with the ChatBot application, especially for the more advanced use cases implemented by the _agent_ version of the ChatBot.

Begin by running the API server, e.g., `make api-server`, which runs the agent-implementation of the ChatBot, by default. Then in a separate terminal window, run one of these commands:

```shell
make open-webui            # Run Open WebUI configured to provide a GUI for the ChatBot.
make run-open-webui        # Synonym for "open-webui".
```

In a browser, open the URL [http://localhost:8080](http://localhost:8080){:target="localhost"}.

You will be prompted to create an admin user account. Pick whatever name, email, and password you want.

For completeness, there are two other useful commands:

```shell
make help-open-webui       # Show help for the API server.
make remove-open-webui     # Cleans up some temporary "uv" and other files created for this app.
```

Next, a little setup is required; we have to tell Open WebUI about the ChatBot server at `http://localhost:8000`. To do this, open the administration settings link, [http://localhost:8080/admin/settings/db](http://localhost:8080/admin/settings/db){:target="localhost"}.

![Open WebUI Database Settings]({{site.baseurl}}/assets/images/open-webui-database-settings.jpg "Open WebUI Database Settings")

Click the _Import_ link on the right hand side under **Config** (shown in the red rounded rectangle highlight). Then browse to `src/apps/chatbot/open-webui/open-webui.config.json` in the project repository or download that file from [here]({{site.gh_edit_repository}}/blob/main/src/apps/chatbot/open-webui/open-webui.config.json){:target="config-json"}. Submit the dialog to load the settings.

Next, check that they were successfully applied. Go to the Administration connection settings, [http://localhost:8080/admin/settings/connections](http://localhost:8080/admin/settings/connections){:target="localhost"}. You should see the following:

![Open WebUI Connections Settings]({{site.baseurl}}/assets/images/open-webui-connections-settings.jpg "Open WebUI Connections Settings")

The changes we made are highlighted with red rounded rectangles:

1. Disabled OpenAI connections. 
1. Added a custom OpenAI-compatible connection to our API server at `http://localhost:8000`.
1. Disabled Ollama connections. 

The first and third change were just to simplify the experience and prevent unintentionally talking directly to OpenAI and Ollama. If you prefer, you can turn these back on by clicking the grey slider on the right for each one (it will turn green). Click the &ldquo;gear&rdquo; icons to edit the connections.

Finally, if you go to the chat page, [http://localhost:8080](http://localhost:8080/){:target="open-webui-home"}, you should see the model selected `ollama_chat/gemma4:e4b`, which will be served through our API server. If you see another model name shown, click the down arrow (&ldquo;chevron&rdquo;) and select this model. With the OpenAI and Ollama direct connections disabled, there should only be this option and possibly one other added by Open WebUI.

![Open WebUI Chat]({{site.baseurl}}/assets/images/open-webui-chat.jpg "Open WebUI Chat")

Try it!

{: .note}
> **Note:**
> It is also possible to configure Open WebUI to use the ChatBot MCP server (discussed next). See the Open WebUI [documentation](https://docs.openwebui.com){:target="openwebui"} for details on configuring MCP servers.

### An MCP Server for the ChatBot

Running the MCP server is very similar. Since it runs the ChatBot for you, it takes the same arguments as the ChatBot. The only difference is the Python module invoked: `uv run python -m apps.chatbot.mcp_server.server`. The same `--which-chatbot` argument is used to select the ChatBot implementation.

```shell
make mcp-server            # Run the MCP server for the ChatBot (Also runs the ChatBot, so don't run both!)
make run-mcp-server        # Synonym for "mcp-server".
make help-mcp-server       # Show help for the MCP server.
make inspect-mcp-server    # Run the server with the `npx @modelcontextprotocol/inspector` tool.
make check-mcp-server      # Runs a 'sanity check' that the MCP server works.
```

For more details on running the MCP server, see the [`src/apps/chatbot/mcp_server/README.md`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/mcp_server/README.md){:target="mcp-readme"}.

{: .tip}
> **Tip:**
> Use the `make inspect-mcp-server` command to run the MCP server under the inspector tool `npx @modelcontextprotocol/inspector`. Node.js has to be installed already to run the inspector.

### An OpenAI-compatible API Server for the ChatBot

An OpenAI-compatible API server is provided. Running it is very similar to running the MCP server. Since it runs the ChatBot for you, it takes the same arguments as the ChatBot, plus two additional options we will discuss shortly. The only other difference is the Python module invoked: `uv run python -m apps.chatbot.api_server.server`. The same `--which-chatbot` argument is used to select the ChatBot implementation.

```shell
make api-server            # Run the OpenAI-compatible API server for the ChatBot (Also runs the ChatBot, so don't run both!)
make run-api-server        # Synonym for "api-server".
make help-api-server       # Show help for the API server.
make check-api-server      # Runs a 'sanity check' that the API server works.

make view-api-server-docs  # Open a browser showing the API server "docs".
make view-api-server-redoc # Open a browser showing the API server "redoc".
```

the other two options are `--host HOST` and `--port PORT` for the API's own web server, not to be confused with `--service-url SERVICE_URL` for the Ollama server. The host _cannot_ have the `http://` prefix in the value. Just use `localhost`, `0.0.0.0`, `192.168.0.1`, etc. The default values for these two CLI arguments are `localhost` and `8000`, respectively.

For more details on running the OpenAI-compatible API server, see the [`src/apps/chatbot/api_server/README.md`]({{site.gh_edit_repository}}/tree/main/src/apps/chatbot/api_server/README.md){:target="api-readme"}.

<a id="automated-testing-practical-enhancements"></a>

## Automated Testing: Practical Enhancements 

This user guide is all about solving the problem of continuing to use traditional software development life cycle (SDLC) practices, which rely heavily on deterministic behavior, with applications that use stochastic, generative AI. The ChatBot application applies the principles described in a practical way for a realistic AI project.

You can run the unit and integration tests with these make targets, but **warning**, they run for a long time since they use inference!

```shell
make tests               # unit tests. Synonyms: test, unit-tests
make integration-tests   # integration tests
```

The automated tests are found in the [`src/tests`]({{site.gh_edit_repository}}/tree/main/src/tests/){:target="tests-dir"} directory. Specifically, the generative AI _unit benchmarks_ are driven by four test suites in [`src/tests/unit/apps/chatbot/`]({{site.gh_edit_repository}}/tree/main/src/tests/unit/apps/chatbot/){:target="atc"} that are named `ai_test_chatbot_*.py`, where `*` is one of the use case names. Most of the implementation is in a `TestBase` parent class in  [`src/tests/utils/apps/chatbot/testbase.py`]({{site.gh_edit_repository}}/tree/main/src/tests/utils/apps/chatbot/testbase.py){:target="testbase"}. This is the code that implements the [_unit benchmarks_]({{site.baseurl}}/testing-strategies/unit-benchmarks) for this project.

Test data files of Q&A  (question and answer) pairs (and additional metadata) were adapted from the example tool outputs found in [`src/data/examples/ollama_chat/gpt-oss_20b/data`]({{site.gh_edit_repository}}/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/){:target="examples"}. However, _we made a lot of changes reflecting what we learned while iterating on the development of the ChatBot application!_ 

These test data files in JSONL format are in the [`src/tests/data`]({{site.gh_edit_repository}}/tree/main/src/tests/data/){:target="test-data"} directory. There are four files (at the time of this writing) for user queries that we classify into four, broad use cases:

<a id="table-5"></a>

| Use Case | Description |
| :------- | :---------- |
| [Emergencies]({{site.gh_edit_repository}}/tree/main/src/tests/data/emergencies.jsonl){:target="test-data"} | Queries that strongly suggest the patient needs urgent medical attention. In the US, they would be told to call _911_ immediately. |
| [Prescriptions]({{site.gh_edit_repository}}/tree/main/src/tests/data/prescriptions.jsonl){:target="test-data"} | Refill requests, questions about how to take a medication, store it, compatibility with particular activities, etc. |
| [Appointments]({{site.gh_edit_repository}}/tree/main/src/tests/data/appointments.jsonl){:target="test-data"} | Requests to schedule or reschedule an appointment. |
| [Others]({{site.gh_edit_repository}}/tree/main/src/tests/data/others.jsonl){:target="test-data"} | Other general health questions and other kinds of queries, such as how to pay a bill, where the office is located, etc. (Many of these Q&A pairs suggest possible future use cases to support.) |

**Table 5:** Use case test data files.

There is one JSONL file per _use case_. The format is illustrated with this example from `appointments.jsonl` (nicely formatted...):

```json
{
  "query":   "I need to reschedule my next appointment.",
  "labels":  ["appointment"],
  "actions": ["reschedule"],
  "rating":  5
}
```

We have been calling these examples _Q&A_ (question and answer) pairs, but they actually contain a query (question) and three expected metadata values corresponding to metadata fields the prompt asks the ChatBot to return. At this time, don't do any testing on the actual generated text in the response, as it is too stochastic, but a possible enhancement is to use _LLM as a Judge_ to assess how good they are:

<a id="table-6"></a>

| Expected Metadata Field | Corresponding Response Field | Discussion |
| :---------------------- | :--------------------------- | :--------- |
| `labels`  | `label`   | The response's `label` is expected to be found in the `labels` list. Usually there is just one element in `labels`, but sometimes more than one label is listed when the query is potentially ambiguous. |
| `actions` | `actions` | The response `actions` list should be a subset of the allowed `actions`. |
| `rating`  | _N/A_     | How the _LLM as a Judge_ validation process rated this synthetic example. |

**Table 6:** Expected metadata fields.

In addition, there are optional fields that may appear in the examples:

<a id="table-7"></a>

| Expected Metadata Field | Corresponding Response Field | Discussion |
| :---------------------- | :--------------------------- | :--------- |
| `reason`        | _N/A_           | Why the judge rated the example the way it did. |
| `prescriptions` | `prescriptions` | List of one or more prescriptions mentioned in the query. |
| `body_parts`    | `body_parts`    | List of one or more body parts mentioned in the query. |
| `vaccines`      | `vaccines`      | List of one or more vaccines mentioned in the query. |

**Table 7:** Optional metadata fields.

The last three fields only appear in an example JSONL if they are non-empty.

During testing, if the `rating` is below a threshold, the ChatBot result is logged as _low confidence_ and not checked for expected results. The ChatBot is also asked to provide its _confidence_ of the result, which is used similarly during the test. This is printed to standard output and to a log file, 

The `label` returned by the ChatBot should correspond to the use case file name! However, in practice, some queries are ambiguous enough that more than one label would be a reasonable interpretation, which is why `labels` is a list. The first list element is always the name of the use case. So, for example, there are many examples in `prescriptions.jsonl` with the label list `["prescription", "appointment"]`, like this one:

```json
{
  "query":         "Do I need a follow-up appointment for my prescription for ozempic?",
  "labels":        ["prescription","appointment"],
  "actions":       ["inquiry"],
  "prescriptions": ["ozempic"],
  "rating": 5
}
```

You can see from the query that it's reasonable to interpret the query as an appointment or prescription query. It is really both, but we &ldquo;force&rdquo; the ChatBot to choose and return only one `label`.

#### Dealing with Slow and Expensive Inference

The AI-specific tests support a few features not normally found in conventional test suites, reflecting some unique challenges when writing automated tests for generative AI applications. Let's discuss these enhancements in depth, starting with the challenge of long test runs.

Normally, we want our unit tests to run very quickly, so we can run them frequently during every small iteration of development. Because inference is relatively slow and expensive, running the full set of Q&A pairs is only practical for occasional (e.g., nightly) integration tests. 

{: .highlight}
> Running the unit test suite using local `ollama` inference with all the Q&A examples can take many hours to complete!

Hence, the first unique feature supported by the test suite is an environment variable `DATA_SAMPLE_RATE`, which tells the test what percentage of the total Q&A pairs to use. For unit tests, it is set to the value of `UNIT_TEST_DATA_SAMPLE_RATE`, which is defined to be 0.1 (or 10%) in the `Makefile`. So, 10% of the Q&A pairs are used for unit tests. These runs still take tens of minutes to complete. However, since some of the Q&A data files have just a few dozen pairs, a lower limit of five is used if the calculated sample size would be less than five.

The integration tests (`integration-tests` target) run all 100% of the Q&A pairs, by default. 

Hence, the sampling feature provides faster turn around for unit tests, but also some extra randomness, as a test prompt could cause a test failure, but it won't be triggered every time! In real development projects, the `integration-tests` target should be built as frequently as possibly (at least nightly?), since they are more likely to find such cases that the unit tests might miss. 

On the other hand, many of the examples are very close to each other, either a few word changes or very similar phrasing, so it is likely that the ChatBot will respond the same way to each variant. So, in terms of _behavior_, the unit test coverage is better than the sample percentage might suggest.

Second, an environment variable `ACCUMULATE_TEST_ERRORS` is used to trigger another feature flag, when the value is non-empty, meaning true. If true, it tells the test suite to run all of the test prompts and accumulate any errors, then report them at the end, rather than the normal approach of &ldquo;failing fast&rdquo; on the first error. The rationale for this feature is to make it easier to capture all the possible problems in one run, given how much time they take, and then work to address them at once. Sometimes common patterns or limitations are evident, e.g., a set of mislabeled Q&A pairs in a data file. This flag defaults to true in the `Makefile`. As we become more comfortable with writing and running the AI-specific unit tests, we may set the default to false for unit tests, returning to the familiar, fail-fast behavior, while keeping it enabled for integration tests. 

When using this feature, it is convenient to log the key output as JSON to a file for subsequent analysis. (CLI JSON processing tools like [`jq`](https://jqlang.org/download/){:target="jq"} are very helpful.) We write JSONL files with the problem information into the directory [`src/tests/logs`]({{site.gh_edit_repository}}/tree/main/src/tests/logs/){:target="logs"}.

#### What Does Pass/Fail Mean?

We spent a great deal of time thinking about how to handle _discrepancies_, inference results that don't exactly match what was expected in the Q&A pair. The labels discussed above are part of the solution. First have the application attempt to determine the use case the patient is invoked (such as a prescription refill), then formulate a deterministic response from that. For some use cases, this eliminates the need to handle the variant responses, while greatly reducing the challenge for other use cases, where we use the response.

Still, the system may not return the label and other metadata expected. Sometimes the request vs. expected label is ambiguous. Mentioning &ldquo;severe chest pain&rdquo; should trigger the _emergency_ use case, while &ldquo;severe stomach pain&rdquo; is more ambiguous and &ldquo;severe foot pain&rdquo; is unlikely to be an emergency, although probably an urgent concern.

A feature called &ldquo;low-confidence results&rdquo; is supported, a practical testing extension we use, as well as a runtime in the ChatBot. During our discussion of data validation (i.e., for the `unit-benchmark-data-validation.py` tool), we said the output includes a _confidence_ rating for how good we think the Q&A pair is for the use case. While we discarded poorly-rated pairs, we kept those with &ldquo;okay&rdquo; ratings.

During testing, if an input prompt and answer carries a rating lower than a certain threshold, the inference result for that test prompt is reported at the end of the test, but no checking is done on the result. We report it as a _low-confidence result._ The `Makefile` variable, `RATING_THRESHOLD`, which defaults to `4` on a scale of `1` to `5`, sets this threshold.

Similarly, when invoking the ChatBot application, the `--confidence-threshold` argument allows you to specify a threshold for answers. If the ChatBot rates an answer to a user prompt below this threshold, the system defaults to a &ldquo;safer&rdquo; default handling. In the `Makefile`, the `CONFIDENCE_THRESHOLD` variable defaults to `0.9`, on a scale of `0.0` to `1.0`, corresponding to a range of 0% to 100% confidence.

Finally, the AI-related unit benchmarks, as opposed to unit tests for other code, are also used as the integration tests, with the different feature invocations just described for more exhaustive coverage. There are additional integration tests, too.
