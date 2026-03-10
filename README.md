# README for Testing Generative AI Agent Applications

[Published User Guide](https://the-ai-alliance.github.io/ai-application-testing/)

This repo contains the code and documentation for the AI Alliance user guide and tools for _Testing Generative AI Agent Applications_, which explores the inherent difficulties for enterprise developers who need to write the same kinds of repeatable, reliable, and automatable tests for AI behaviors that they are accustomed to writing for "traditional" code. This is much more challenging with generative AI models involved, because non-Gen AI software is (mostly) deterministic and hence predictable, while Gen AI outputs are _stochastic_, governed by a random probability model, so how do you write a _predictable_ test for that kind of behavior?? 

This documentation is the [published user guide](https://the-ai-alliance.github.io/ai-application-testing/), with the GitHub Pages sources in this repo's `docs` folder and the example code in the `src` folder. A `Makefile` provides convenient `make` targets for doing most tasks. 

Next, we discuss working with the tools and example application for this project. You can also find this information in the user guide's [Using the Healthcare ChatBot Example Application and Tools](https://the-ai-alliance.github.io/ai-application-testing/working-example/) chapter. For information about working with the user guide website content, see [GITHUB_PAGES.md](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/GITHUB_PAGES.md).

> [!WARNING]
> **DISCLAIMER:** In this guide, we develop a healthcare ChatBot example application, chosen because it is a _worst case_ design challenge. Needless to say, but we will say it anyway, a ChatBot is notoriously difficult to implement successfully, because of the free form prompts from users and the many possible responses models can generate. A healthcare ChatBot is even more challenging because of the risk it could provide bad responses that lead to poor patient outcomes, if applied. Hence, **this example is only suitable for educational purposes**. It is not at all suitable for use in real healthcare applications and **_it must not be used_** in such a context. Use it at your own risk.

## The User Guide Tools and Exercises vs. the ChatBot Application

In the [published user guide](https://the-ai-alliance.github.io/ai-application-testing/), the tools and exercises are written with an emphasis on teaching concepts, with minimal distractions, with less concern about being fully engineered for real-world, enterprise development and deployment, where more sophisticated tools might be needed.

In contrast, the Healthcare ChatBox example application applies the concepts in a more &ldquo;refined&rdquo; implementation that also illustrates how existing software development practices and new AI-oriented techniques can be used together in a real software-development project.

## Setup

{: .note}
> **NOTE:**
> 
> The `make` target processes discussed below assume you are using a MacOS or Linux shell environment like `zsh` or `bash`. However, the tools described below are written in Python, so the commands shown for running them should work on any operating system with minor adjustments, such as paths to files and directories. Let us know about your experiences: [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues), [discussions](https://github.com/The-AI-Alliance/ai-application-testing/discussions).

Whether using the tools or the example application, you start by setting up the required dependencies, etc.

Clone the project [repo](https://github.com/The-AI-Alliance/ai-application-testing/), change to the `ai-application-testing` directory, and run the following `make` command to do &ldquo;one-time&rdquo; setup steps:

```shell
make one-time-setup 
```

If `make` won't work on your machine, do the following steps yourself:

* Install [`uv`](https://docs.astral.sh/uv/), a Python package manager. 
* Run the setup command `uv env` to install dependencies.
* Install [`ollama`](https://ollama.com) for local model inference (optional).

{:.tip}
> **TIPS:**
> 1. Try `make help` for details about the `make` process. There are also `--help` options for all the tools discussed below.
> 1. For any `make` target, to see what commands will be executed without running them, pass the `-n` or `--dry-run` option to `make`.
> 1. The `make` targets have only been tested on MacOS. Let us know if they don't work on Linux. The actual tools are written in Python for portability.
> 1. The repo [README](https://github.com/The-AI-Alliance/ai-application-testing/) has an Appendix with other tools you might find useful to install.

One of the dependencies managed with `uv` is [`LiteLLM`](https://docs.litellm.ai/), the library we use for flexible invocation of different inference services. All our development has been done using `ollama` for cost-benefit and flexibility reasons, but it is not required if you want to use an inference provider instead, like OpenAI or Anthropic. In that case, see the `LiteLLM` [usage documentation](https://docs.litellm.ai/#basic-usage) for how to configure `LiteLLM` to use your preferred inference service. You will need to modify the `Makefile`, as discussed in [Changing the Default Model Used](#changing-the-default-model-used) below.

### Pick Your Models

If you use `ollama`, download the models you want to use. For example:

```shell
ollama serve             # in one terminal window
ollama pull gpt-oss:20b  # in another terminal window
```

In our experiments, we used the models shown in **Table 1** (see also a similar table [here]({{site.baseurl}}/arch-design/tdd/#table-1)): 

| Model                        | # Parameters | Notes |
| :--------------------------- | -----------: | :---- |
| `gpt-oss:20b`                |  20B | Excellent performance, but requires a lot of memory (see below). |
| `llama3.2:3B`                |   3B | A small but effective model in the Llama family. Should work on most laptops. |
| `granite4:latest`            |   3B | Another small model tuned for instruction following and tool calling. |
| `smollm2:1.7b-instruct-fp16` | 1.7B | The model family used in Hugging Face's [LLM course](https://huggingface.co/learn/llm-course/), which we will also use to highlight some advanced concepts. The `instruct` label means the model was tuned for improved _instruction following_, important for ChatBots and other user-facing applications. |

{: .tip}
> **REQUEST:** [Let us know]({{site.baseurl}}/contributing#join-us) which models work well for you!

**Table 1:** Models used for our experiments.

To install one or more of these models, use these commands (for any operating system and shell environment):

```shell
ollama pull gpt-oss:20b
ollama pull llama3.2:3B
ollama pull granite4:latest
ollama pull smollm2:1.7b-instruct-fp16
```

(Yes, some models use `B` and others use `b`...)

{: .attention}
> We provide example results for some of these models in [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/src/data/examples/ollama). 

By default, we use `gpt-oss:20b` as our inference model, served by `ollama`. This is specified in the `Makefile` by defining the variable `MODEL` to be `ollama_chat/gpt-oss:20b`. (Note the `ollama_chat/` prefix.) All four models shown above are defined in the `MODELS` variable; there are `all-models-*` targets that try all of them.

Unfortunately, a 20B parameter model is too large for many developer machines. Specifically, we found that Apple computers with M1 Max chips with 32GB of memory can struggle when using `gpt-oss:20b`, especially if lots of other apps are using significant memory. 48GB or 64GB of memory is much better. However, acceptable performance, especially for learning purposes, was achieved on 32GB machines when using the other, smaller models. We encourage you to experiment with other model sizes and with different model families. Consider also [Quantized]({{site.glossaryurl}}/#quantization) versions of models.

### Changing the Default Model Used

If you don't want to use the default model setting, `gpt-oss:20b`, or you want to use a different inference option than `ollama`, first see the `LiteLLM` [documentation](https://docs.litellm.ai/#basic-usage) for information about specifying models for other inference services.

There are two ways to specify your preferred model:

#### Change the Makefile

Edit the [`Makefile`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/Makefile) and change the following definitions:

* `MODEL` - e.g., `ollama_chat/llama3.2:3B`. This will make the change the default for all invocations of the tools and the example ChatBot app. (The `ollama_chat/` or `ollama/` prefix is required if you are using `ollama`, with `ollama_chat/` recommended by `LiteLLM`.) For convenience, we defined several `MODEL_*` variables for different models, then refer to the one we want when defining `MODEL`. You can do this if you like...
* `INFERENCE_SERVICE` - e.g., `openai`, `anthropic`, `ollama`.
* `INFERENCE_URL` - e.g., `http://localhost:11434` for `ollama`.
* Others? The `LiteLLM` documentation may tell you to define other variables. You will also need an API key or other credentials for most services. **_Do not put this information in the Makefile!_** This avoids the risk that you will accidentally commit secrets to a repo. Instead, use an environment variable or other solution described by the `LiteLLM` documentation.

#### Override Makefile Definitions on the Command Line

On invocation, you can dynamically change values, such as the `MODEL` used with `ollama`. This is the easiest way to do &ldquo;one-off&rdquo; experiments with different models. For example:

```shell
make MODEL=ollama_chat/llama3.2:3B ...
```

If you want to try _all_ the models mentioned above with one command, use `make all-models-...`, where `...` is one of the other make targets, like `all-code`, which runs all the tool invocations for a single model, e.g.,

```shell
make all-models-all-code
```

You can also change the list of models you regularly want to use by changing the definition of the `MODELS` variable in the `Makefile`.

{: .note}
> **NOTE:**
>
> See also the [LiteLLM documentation](https://docs.litellm.ai/#basic-usage) for guidance on any required modifications to the arguments passed in our Python code to the LiteLLM `completion` function. (Search for `response = completion` to find all the occurrences.) We plan to [implement automatic handling](https://github.com/The-AI-Alliance/ai-application-testing/issues/20) of such changes eventually.

## Running the Tools and ChatBot Application with `make`

Now you are set up and you can use `make` to run the tools discussed and also the complete example ChatBot application. We will discuss the tools first, then the application.

On MacOS and Linux, using `make` is the easiest way to run the exercises. The actual commands are printed out and we repeat them below for those of you on other platforms. Hence, you can also run the Python tools directly without using `make`. 

{: .tip}
> **TIPS:**
>
> 1. For all of the tool-invocation `make` commands discussed from now on, you can run each one for _all_ the models by prefixing the target name with `all-models-`, e.g., `all-models-run-tdd-example-refill-chatbot`. This target doesn't make sense for for the ChatBot application, which is interactive, but you can use it for the `tests` and `integration-tests` targets.
> 1. For a given model (as defined by the `Makefile` variable `MODEL`), you can run all of the tools with one command, `make all-code`. Hence, you can run all the examples for all the models discussed above using `make all-models-all-code`.

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
	* `OUTPUT_LOG_DIR`, where most output is written, which is `temp/output/ollama_chat/gpt-oss_20b/logs`, when `MODEL` is defined to be `ollama_chat/gpt-oss:20b`. (The `:` is converted to `_`, because `:` is not an allowed character in MacOS file system names.) Because `MODEL` has a `/`, we end up with a directory `ollama` that contains a `gpt-oss_20b` subdirectory.
	* `OUTPUT_DATA_DIR`, where data files are written, which is `temp/output/ollama_chat/gpt-oss_20b/data`, when `MODEL` is defined to be `ollama_chat/gpt-oss:20b`. 

If you don't use the `make` command, make sure you have `uv` installed and either manually create the same directories or modify the corresponding paths shown in the next command.

After the setup, the `make` target runs the following command:

```shell
cd src && time uv run tools/tdd-example-refill-chatbot.py \
	--model ollama_chat/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir prompts/templates \
	--data-dir .../output/ollama_chat/gpt-oss_20b/data \
	--log-file .../output/ollama_chat/gpt-oss_20b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log
```

`TIMESTAMP` will be the current time when the `uv` command started, of the form `YYYYMMDD-HHMMSS`, and the values passed for `--data-dir` and `--log-file` are absolute paths. The other paths shown are relative to the `src` directory.

The `time` command prints execution time information for the `uv` command. It is optional and you can omit it when running this command directly yourself or on a system without this command. It returns how much system, user, and "wall clock" times were used for execution on MacOS and Linux systems. Note that `uv` is used to run `tools/tdd-example-refill-chatbot.py`. 

The arguments are as follows:

| Argument | Purpose |
| :------- | :------ |
| `--model ollama_chat/gpt-oss:20b` | The model to use, defined by the `make` variable `MODEL`, as discussed above. |
| `--service-url http://localhost:11434` | The `ollama` local server URL. Some other inference services may also require this argument. |
| `--template-dir prompts/templates` | Where we keep prompt templates we use for all the examples. |
| `--data-dir .../output/ollama_chat/gpt-oss_20b/data` | Where any generated data files are written. (Not used by all tools.) |
| `--log-file .../output/ollama_chat/gpt-oss_20b/logs/${TIMESTAMP}/tdd-example-refill-chatbot.log` | Where log output is captured. |

The `tdd-example-refill-chatbot.py` tool runs two experiments, one with the template file [`q-and-a_patient-chatbot-prescriptions.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions.yaml) and the other with [`q-and-a_patient-chatbot-prescriptions-with-examples.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml). The only difference is the second file contains embedded examples in the prompt, so in principal the results should be better, but in fact, they are often the same, as discussed in the [TDD chapter]({{site.baseurl}}/arch-design/tdd/).

{: .note}
> **NOTE:**
>
> These template files were originally designed for use with the `llm` CLI tool (see the Appendix in the repo's [`README`]({{site.gh_edit_repository}}/) for details about `llm`). In our Python tools, [LiteLLM](https://docs.litellm.ai/#basic-usage) is used instead to invoke inference. We extract the content we need from the templates and construct the prompts we send through LiteLLM.

The `tdd-example-refill-chatbot.py` tool passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. As the [TDD chapter]({{site.baseurl}}/arch-design/tdd/) explains, this is a very ad-hoc approach to creating and testing a _unit benchmark_.

## Run `unit-benchmark-data-synthesis`

Described in [Unit Benchmarks]({{site.baseurl}}/testing-strategies/unit-benchmarks/), this tool uses an LLM to generate Q&A (question and answer) pairs for _unit benchmarks_. It addresses some of the limitations of the more ad-hoc approach to benchmark creation used in the previous TDD exercise:

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
	--model ollama_chat/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir prompts/templates \
	--data-dir .../output/ollama_chat/gpt-oss_20b/data \
	--log-file .../output/ollama_chat/gpt-oss_20b/logs/${TIMESTAMP}/unit-benchmark-data-synthesis.log
```

{: .note}
> **NOTE:**
>
> If you run the previous tool command, then this one, the two values for `TIMESTAMP` will be different. However, when you make `all-code` or any `all-models-*` target, the _same_ value will be used for `TIMESTAMP` for all the invocations.

The arguments are the same as before, e.g., the `--data-dir` argument specifies the location where the Q&A pairs are written, one file per unit benchmark, with subdirectories for each model used. For example, after running this tool with `ollama_chat/gpt-oss:20b`, the output will be in `.../output/data/ollama_chat/gpt-oss_20b`. We replace `:` with `_`, because `:` is an invalid character for MacOS file paths. This directory will have the following files of synthetic Q&A pairs:

* `synthetic-q-and-a_patient-chatbot-emergency-data.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`

(Examples can be found in the repo's [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama) directory.)

They cover three unit-benchmarks:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should stop using the ChatBot and call 911 (in the US) immediately.
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

The prompt used tells the model to return one of these _classification_ labels, along with some additional information, rather than an ad-hoc, generated text like, "It sounds like you are having an emergency. Please call 911..."

Each of these data files are generated with a single inference invocation, with each invocation using these corresponding template files:

* [`synthetic-q-and-a_patient-chatbot-emergency.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency.yaml)
* [`synthetic-q-and-a_patient-chatbot-prescription-refills.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills.yaml)
* [`synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml)

## Run `unit-benchmark-data-validation`

Described in [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/), this tool uses a _teacher model_ to _validate_ the quality of the Q&A pairs that were generated in the previous exercise:

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
	--model ollama_chat/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir prompts/templates \
	--data-dir .../output/ollama_chat/gpt-oss_20b/data \
	--log-file .../output/ollama_chat/gpt-oss_20b/logs/TIMESTAMP/unit-benchmark-data-validation.log \
```

In this case, the `--data-dir` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory:

* `synthetic-q-and-a_patient-chatbot-emergency-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.yaml`

(See examples in [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama).)

These files &ldquo;rate&rdquo; each Q&A pair from 1 (bad) to 5 (great).
Also, summary statistics are written to `stdout` and to the output file `temp/output/ollama_chat/gpt-oss_20b/unit-benchmark-data-validation.out`. Currently, we show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. (For simplicity, we used the same `gpt-oss:20b` model as the _teacher_ that we used for generation.) From one of our test runs a text version of the following table was written:

Files:                                                                            |    1  |    2  |    3  |    4  |    5  | Total |
| :------                                                               | ----: | ----: | ----: | ----: | ----: | ----: |
synthetic-q-and-a_patient-chatbot-emergency-data.json                             |    0  |    4  |    7  |   12  |  168  |  191  |
synthetic-q-and-a_patient-chatbot-prescription-refills-data.json                  |    0  |    0  |    0  |    0  |  108  |  108  |
synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json              |    2  |    2  |    0  |    1  |  168  |  173  |
| | | | | | | |
Totals:                                                                           |    2  |    6  |    7  |   13  |  444  |  472  |

Total count: 475 (includes errors), total errors: 3

The teacher model is asked to provide _reasoning_ for its ratings. It is instructive to look at the output `*-validation.yaml` files that we saved in [`src/data/examples/ollama_chat/gpt-oss_20b/data/`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/).

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). 

In fact, the program deliberately ignores the actual file where the Q&A pair appears. For example, we found that the _emergency_ file contains some _refill_ and _other_ questions. Only the actual label in the answer corresponding to a question was evaluated. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. You could decide to resort all the data by label to keep them separated by use case or you could just concatenate all the Q&A pairs into one big set. We think the first choice is more in the spirit of how focused, automated, use-case specific tests are supposed to work, but it is up to you...

The same template file was used for evaluating the three data files:

* [`synthetic-q-and-a_patient-chatbot-data-validation.yaml`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml)

## Run the ChatBot Example Application

This purpose of this application is to represent something closer to what you would actually build, with automated unit and integration tests, a growing list of features, added incrementally, etc. 

The application can be invoked in one of several ways:

```shell
make chatbot               # Run the interactive ChatBot with a simple, command-line "UX".
make run-chatbot           # Synonym for "chatbot".
make help-chatbot          # Show help for the ChatBot.
```

After the same setup steps, like output directory creation, the following command is executed, which you can run directly, where we show the values for arguments as defined by `Makefile` variables:

```shell
cd src && time uv run python -m apps.chatbot.main \
  --model ollama_chat/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir prompts/templates \
  --data-dir data \
  --confidence-threshold 0.9 \
  --log-file .../logs/.../chatbot.log
```

A simple prompt is presented where you can enter "patient prompts" and see the replies. If you prefer a nicer GUI interface, see [Using the ChatBot with Open WebUI](#using-the-chatbot-with-open-webui) below.

The arguments are similar to the previously-discussed arguments, with a new argument `--confidence-threshold`, which we will explain below.

The source code, etc. for this application and the automated tests are located in these locations:

| Content | Location | Notes |
| :------ | :------- | :---- |
| Source code      | [`src/apps/chatbot`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/apps/chatbot/) | Main source code for the ChatBot and the MCP server |
| Prompt Templates | [`src/prompts/templates`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/) | The prompts used. |
| Data             | [`src/data`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/) | Application data location, but not currently used! |
| Tests            | [`src/tests/unit/apps/chatbot`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/tests/unit/apps/chatbot/) (unit tests) and [`src/tests/integration/apps/chatbot`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/tests/integration/apps/chatbot/) (integration tests) | |
| Test Data        | [`src/tests/data`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/tests/data/) | Test prompts and expected results. |

### An MCP Server for the ChatBot

Running the MCP server is very similar. Since it runs the ChatBot for you, it takes the same arguments as the ChatBot. The only difference is the Python module invoked: `uv run python -m apps.chatbot.mcp_server.server`. 


```shell
make mcp-server            # Run the MCP server for the ChatBot (Also runs the ChatBot, so don't run both!)
make run-mcp-server        # Synonym for "mcp-server".
make help-mcp-server       # Show help for the MCP server.
make inspect-mcp-server    # Run the server with the `npx @modelcontextprotocol/inspector` tool.
make check-mcp-server      # Runs a 'sanity check' that the MCP server works.
```

For more details on running the MCP server, see the [`src/apps/chatbot/mcp_server/README.md`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/apps/chatbot/mcp_server/README.md).

> [!TIP]
> Use the `make inspect-mcp-server` command to run the MCP server and inspect it with the `npx @modelcontextprotocol/inspector` tool. Node.js is required to run the inspector.

### An OpenAI-compatible API Server for the ChatBot

Similarly, running the OpenAI-compatible API server is very similar. Since it runs the ChatBot for you, it takes the same arguments as the ChatBot, plus two additional options we will discuss shortly. The only other difference is the Python module invoked: `uv run python -m apps.chatbot.api_server.server`. 

```shell
make api-server            # Run the OpenAI-compatible API server for the ChatBot (Also runs the ChatBot, so don't run both!)
make run-api-server        # Synonym for "api-server".
make help-api-server       # Show help for the API server.
make check-api-server      # Runs a 'sanity check' that the API server works.

make view-api-server-docs  # Open a browser showing the API server "docs".
make view-api-server-redoc # Open a browser showing the API server "redoc".
```

the other two options are `--host HOST` and `--port PORT` for the API's own web server, not to be confused with `--service-url SERVICE_URL` for the Ollama server. The host _cannot_ have the `http://` prefix in the value. Just use `localhost`, `0.0.0.0`, `192.168.0.1`, etc. The default values for these two options are `localhost` and `8000`, respectively.

For more details on running the OpenAI-compatible API server, see the [`src/apps/chatbot/api_server/README.md`](src/apps/chatbot/api_server/README.md).

### Using the ChatBot with Open WebUI

Finally, if you prefer using a GUI instead of the CLI prompt for the ChatBot, an integration is provided with [Open WebUI](https://docs.openwebui.com).

Begin by running the API server, e.g., `make api-server`. Then in a separate terminal window, run one of these commands:

```shell
make open-webui            # Run Open WebUI configured to provide a GUI for the ChatBot.
make run-open-webui        # Synonym for "open-webui".
```

In a browser, open the URL [http://localhost:8080](http://localhost:8080).

You will be prompted to create an admin user account. Pick whatever name, email, and password you want.

For completeness, there are two other useful commands:

```shell
make help-open-webui       # Show help for the API server.
make remove-open-webui     # Cleans up some temporary "uv" and other files created for this app.
```

Next, a little setup is required; we have to tell Open WebUI about the ChatBot server at `http://localhost:8000`. To do this, open the link administration settings link, [http://localhost:8080/admin/settings/db](http://localhost:8080/admin/settings/db).

![Open WebUI Database Settings]({{site.baseurl}}/assets/images/open-webui-database-settings.jpg "Open WebUI Database Settings")

Click _Import_ link on the right hand side under **Config** (shown in the red oval highlight). Then browse to `src/apps/chatbot/open-webui/open-webui.config.json` in the project repository or download that file from [here](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/src/apps/chatbot/open-webui/open-webui.config.json). Submit the dialog to load the settings.

Next, check that they were successfully applied. Go to the Administration connection settings, [http://localhost:8080/admin/settings/connections](http://localhost:8080/admin/settings/connections). You should see the following:

![Open WebUI Connections Settings]({{site.baseurl}}/assets/images/open-webui-connections-settings.jpg "Open WebUI Connections Settings")

The changes we made are highlighted:

1. Disabled OpenAI connections. 
1. Added a custom OpenAI-compatible connection to our API server at `http://localhost:8000`.
1. Disabled Ollama connections. 

The first and third change were just to simplify the experience and prevent unintentionally talking directly to OpenAI and Ollama. If you prefer, you can turn these back on by clicking the grey slider on the right for each one (it will turn green). Click the &ldquo;gear&rdquo; icons to edit the connections.

Finally, if you go to the chat page, [http://localhost:8080](http://localhost:8080/){:target="open-webui-home"}, you should see the model selected `ollama_chat/gpt-oss:20b`, which will be served through our API server. If you see another model name shown, click the down arrow (&ldquo;chevron&rdquo;) and select this model. With the OpenAI and Ollama direct connections disabled, there should only be this option and possibly one other added by Open WebUI.

![Open WebUI Chat]({{site.baseurl}}/assets/images/open-webui-chat.jpg "Open WebUI Chat")

Try it!

> [!NOTE]
> It is also possible to configure Open WebUI to use the ChatBot MCP server. See the Open WebUI [documentation](https://docs.openwebui.com) for details on configuring MCP servers.

### Practical Testing Enhancements 

Now we have automated tests in the `src/tests` directory and test data, which is a set of JSONL files with example prompt/answer pairs (with other metadata) used to test each supported use case of the ChatBot. In other words, this data is used for the [_unit benchmarks_]({{site.baseurl}}/testing-strategies/unit-benchmarks) we have been advocating you use. This data was adapted from the example outputs of the tools found in [`src/data/examples/ollama_chat/gpt-oss_20b/data`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/ollama_chat/gpt-oss_20b/data/), but _with changes reflecting what we learned while iterating on the development of the ChatBot application!_ For example, the test data covers a few new use cases, refines some handling of expected responses, excludes some synthetic data was validated as poor, and makes other changes. This is how we would expect your development projects to proceed, where you use the tools we described above to generate and validate test data, for example, then refine the data for use as unit-benchmark data.

The AI-specific tests support a few features not normally found in conventional test suites, reflecting some unique challenges when writing automated tests for AI applications. 

First, because inference is slow and expensive, the unit tests by default sample 25% of the test prompts per use case (configurable; see `Makefile` variable `UNIT_TEST_DATA_SAMPLE_RATE`), but no fewer than five (arbitrary) samples per use case, when there aren't a lot to begin with. However, the integration tests (`integration-tests` target) run all 100% of them. This compromise provides faster turn around for unit tests, but also some extra randomness, as a test prompt could cause a test failure, but it won't be triggered every time! Hence, in real development projects, the `integration-tests` target should be built as frequently as &ldquo;reasonable&rdquo;, since it will find such cases that could be missed.

Second, a `Makefile` variable `TEST_ALL_EXAMPLES` is used as an environment variable that triggers another feature flag. If true, it tells the test suite to run all of the test prompts and accumulate any errors, then report them at the end, rather than the normal approach of &ldquo;failing fast&rdquo; on the first error. This flag defaults to false for unit tests, meaning the regular fail-fast approach is used, but it is set to true for the integration tests. The rationale for this feature is to make it easier to capture all the possible problems in one run, as they may group into common limitations in the prompt file, logic for handling of suboptimal results, etc.

Third, a feature called &ldquo;low-confidence results&rdquo; is supported. During our data validation discussion, where we used the `unit-benchmark-data-validation.py` tool, we said the output includes a rating of how good we think the prompt is for the use case, etc. We kept these ratings in the automated test data used for the ChatBot. In fact, we simply stripped out poorly rated synthetic data from the test data set. That leaves some test prompts as &ldquo;okay&rdquo;, but possibly poor. So, during testing, if an input prompt and answer carries a rating lower than a certain threshold, the inference result for that test prompt is reported at the end of the test, but no checking is done on the result. In other words, it is simply assumed the result is unreliable for that prompt. This reflects our recommendation for real-world ChatBot inference; if you don't have complete confidence in the response, perhaps because the user prompt is confusing, then default to a safe-handling path, such as asking a human to take over the conversation or perhaps asking the user for clarification. 

A second threshold used in the application is for the inference process's own confidence in its work. If it returns a confidence level below a configurable threshold, the default &ldquo;safe&rdquo; response is returned to the user. These two thresholds are also handled as `Makefile` variables, `RATING_THRESHOLD`, defined as `4` on a scale of `1` to `5`, and `CONFIDENCE_THRESHOLD`, defined as `0.9` on a scale of `0.0` to `1.0`, corresponding to a range of 0% to 100%.

Finally, the AI-related unit tests (benchmarks), as opposed to unit tests for other code, are also used as the integration tests, with the different feature invocations just described for more exhaustive coverage.

## Getting Involved

We welcome contributions as PRs, either to our code examples or our user guide. Please see our [Alliance community repo](https://github.com/The-AI-Alliance/community/) for general information about contributing to any of our projects. This section provides some specific details you need to know.

In particular, see the AI Alliance [CONTRIBUTING](https://github.com/The-AI-Alliance/community/blob/main/CONTRIBUTING.md) instructions. You will need to agree with the AI Alliance [Code of Conduct](https://github.com/The-AI-Alliance/community/blob/main/CODE_OF_CONDUCT.md).

All _code_ contributions are licensed under the [Apache 2.0 LICENSE](https://github.com/The-AI-Alliance/community/blob/main/LICENSE.Apache-2.0) (which is also in this repo, [LICENSE.Apache-2.0](LICENSE.Apache-2.0)).

All _documentation_ contributions are licensed under the [Creative Commons Attribution 4.0 International](https://github.com/The-AI-Alliance/community/blob/main/LICENSE.CC-BY-4.0) (which is also in this repo, [LICENSE.CC-BY-4.0](LICENSE.CC-BY-4.0)).

All _data_ contributions are licensed under the [Community Data License Agreement - Permissive - Version 2.0](https://github.com/The-AI-Alliance/community/blob/main/LICENSE.CDLA-2.0) (which is also in this repo, [LICENSE.CDLA-2.0](LICENSE.CDLA-2.0)).

We use the "Developer Certificate of Origin" (DCO).

> [!WARNING]
> Before you make any git commits with changes, understand what's required for DCO.

See the Alliance contributing guide [section on DCO](https://github.com/The-AI-Alliance/community/blob/main/CONTRIBUTING.md#developer-certificate-of-origin) for details. In practical terms, supporting this requirement means you must use the `-s` flag with your `git commit` commands.

## The Website

The documentation for this repo is published using [GitHub Pages](https://pages.github.com/). See [GITHUB_PAGES.md](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/GITHUB_PAGES.md) for details.

## Appendix: The `llm` and `jq` CLI Tools

If you want an excellent command-line tool for LLM inference, try [`llm`](https://github.com/simonw/llm) from Simon Willison. Not only does it handle various inference options, from `ollama` to services like ChatGPT and Anthropic, it has features like a template system, tool registration, etc. 

There are several `make` targets at the end of `Makefile` that you can use to install and use `llm`. Run `make help-llm` for details. Here we summarize a few key points to know.

We use several &ldquo;templates&rdquo; in [`src/prompts/templates`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates) with LiteLLM, but they were original designed for use with `llm`. The `make install-llm-templates` command will install them as `llm` templates, which you could use to make CLI versions of our Python tools, if you prefer.

The target first executes the following `llm` command to see where `llm` has templates installed on your system: 

```shell
llm templates path
```

On MacOS, it will be `$HOME/Library/Application Support/io.datasette.llm/templates`. The target then copies all the YAML files in the [`src/prompts/templates`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates) directory to the correct location for templates on your system.

Try `llm help` for more details on the CLI.

Similarly, if you want a powerful CLI for parsing JSON, see [`jq`](https://jqlang.org/download/) ("JSON query"). The query language takes some practice to learn, but the documentation provides good examples.
