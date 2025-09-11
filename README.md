# README for Achieving Confidence in Enterprise AI Applications

[Published User Guide](https://the-ai-alliance.github.io/ai-application-testing/)

This repo contains the code and documentation for the AI Alliance user guide and tools for _Achieving Confidence in Enterprise AI Applications_, which explores the inherent difficulties for enterprise developers who need to write the same kinds of repeatable, reliable, and automatable tests for AI behaviors that they are accustomed to writing for "traditional" code. This is much more challenging with generative AI models involved, because non-Gen AI software is (mostly) deterministic and hence predictable, while Gen AI outputs are _stochastic_, governed by a random probability model, so how do you write a _predictable_ test for that kind of behavior?? 

This project contains the website for the [user guide](https://the-ai-alliance.github.io/ai-application-testing/), with the GitHub Pages content in the `docs` folder, and example code in the `src` folder. A `Makefile` provides convenient `make` targets for doing most tasks.

Next, we discuss working with the example application for this project. For information about working with the website documentation, see [GITHUB_PAGES.md](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/GITHUB_PAGES.md).

> [!WARNING]
> **DISCLAIMER:** In this guide, we develop a healthcare ChatBot example application, chosen because it is a _worst case_ design challenge. Needless to say, but we will say it anyway, a ChatBot is notoriously difficult to implement successfully, because of the free form prompts from users and the many possible responses models can generate. A healthcare ChatBot is even more challenging because of the risk it could provide bad responses that lead to poor patient outcomes, if applied. Hence, **this example is only suitable for educational purposes**. It is not at all suitable for use in real healthcare applications and **_it must not be used_** in such a context. Use it at your own risk.


## Trying the Tools Yourself!

We discuss how to setup and execute the tools, but you'll need to read the corresponding [website](https://the-ai-alliance.github.io/ai-application-testing/) user guide sections for details about what they are doing and how they work.

### Setup

Clone the project [repo](https://github.com/The-AI-Alliance/ai-application-testing/) and run the following `make` command to do "one-time" setup steps, such as installing tools required. Assuming you are in the repo root directory, run this command:

```shell
make one-time-setup 
```

> [!TIP]
> 1. Try `make help` for details about the `make` process. There are also `--help` options for all the tools discussed below.
> 2. The `make` process has only been tested on MacOS, but it is designed to work on Linux. The actual tools are written in Python for portability.
> 3. There is an Appendix at the end of this file with suggestions for optional command-line tools that are very useful.

The `one-time-setup` target provides instructions for how to install required tools including [`uv`](https://docs.astral.sh/uv/), the Python package management system. It also suggests you install [`ollama`](https://ollama.com), if you want to use for local model inference.

Python library dependencies are managed using `uv`. They are installed automatically, as needed, when running the tools described below. In particular, we use [LiteLLM](https://docs.litellm.ai/#basic-usage) for invoking inference services.

If you install `ollama`, download your models of choice. By default, we use `gpt-oss:20b` as our inference model in the `Makefile`, but we also executed our examples with `llama3.2:3B`. (We provide example results for both in [`src/data/examples/ollama`](https://github.com/The-AI-Alliance/ai-application-testing/blob/main/`src/data/examples/ollama`). We found that `gpt-oss:20b` is too large for many developer machines, but acceptable results, especially for learning purposes, are provided when using the much smaller `llama3.2:3B`. (We encourage you to experiment with many models!)

To install one or both of these models, use these commands:

```shell
ollama pull llama3.2:3B
ollama pull gpt-oss:20b
```

(Yes, it is `B` for one and `b` for the other, as shown...)

> [!TIP]
> Using `ollama` for local inference, we observed the following while testing. On Apple computers with M1 Max chips, 32GB of memory was not enough for `gpt-oss:20b`, when a normal load of other applications was also running, but there was sufficient memory for `llama3.2:3B`. Having 64GB of memory allowed `gpt-oss:20b` to work well. We found you can use the even larger `llama3.3:70B` on a 64GB machine if you keep the background activity low and you don't mind waiting longer for results. Pick a small enough model that you can run in your environment. Of course, the quality of the output will generally be better for larger models.

If you don't want to use our default model setting, `gpt-oss:20b`, there are two ways to specify your preferred model:

1. Edit [`src/Makefile`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/Makefile) and change the definition of `MODEL` to be your choice, e.g., `ollama/llama3.2:3B`. This will make the change permanent for all examples. The `ollama/` prefix is required if you are using `ollama`. 
1. Override the definition of `MODEL` when you run `make`, e.g., `make MODEL=ollama/llama3.2:3B run-tdd-example-refill-chatbot`. This is the best way to run trials with different models.

> [!NOTE]
> See the [LiteLLM documentation](https://docs.litellm.ai/#basic-usage) for guidance on how to specify models for different inference services. If you use a service other than `ollama`, you will need to be sure the required environment variables are set in your environment, e.g., an API key, and you may need to change the arguments passed in our Python scripts to the LiteLLM `completion` function. We plan to make this more [automatic](https://github.com/The-AI-Alliance/ai-application-testing/issues/20).

### Running the Examples with `make`

Use `make` to run the examples. The actual commands are printed out, so you can run them subsequently without `make`, if you prefer. Hence, you can run the Python scripts directly or use `make`. 

### Run `tdd-example-refill-chatbot`

This example is explained in user guide's section on [Test-Driven Development](https://the-ai-alliance.github.io/ai-application-testing/arch-design/tdd/).

Run this `make` command:

```shell
make run-tdd-example-refill-chatbot 
```

This does some setup, then runs the following command (default arguments):

```shell
time uv run src/scripts/tdd-example-refill-chatbot.py \
	--model ollama/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir src/prompts/templates \
	--output temp/output/ollama/gpt-oss_20b/tdd-example-refill-chatbot.out \
	--data temp/output/ollama/gpt-oss_20b/data
```

> [!TIP]
> To see this command without running anything, pass the `-n` or `--dry-run` option when &ldquo;making&rdquo; any target.

The `time` command returns how much system, user, and "wall clock" times were used for execution on MacOS and Linux systems. Note that `uv` is used to run this tool and all others we will discuss. The arguments are used as follows:

| Argument | Purpose |
| :------- | :------ |
| `--model ollama/gpt-oss:20b` | The model to use, as discussed above. |
| `--service-url http://localhost:11434` | Only used for `ollama`; the local URL for the `ollama` server. |
| `--template-dir src/prompts/templates` | Where we have prompt templates we use for all the examples. They are `llm` compatible, too. See the Appendix below. |
| `--output temp/output/ollama/gpt-oss_20b/tdd-example-refill-chatbot.out` | Where console output is captured. |
| `--data temp/output/ollama/gpt-oss_20b/data` | Where any generated data files are written. (Not used by all tools.) |

> [!TIP]
> If you want to save the output of a run to `src/data/examples/`, run the target `make save-examples`. It will create a subdirectory for the model used. Hence, you have to specify the desired model, e.g., `make MODEL=ollama/llama3.2:3B save-examples`. We have already saved example outputs for `ollama/gpt-oss:20b` and `ollama/llama3.2:3B`. See also the `.out` files that capture "stdout".

The script runs two experiments, each with these two templates files `q-and-a_patient-chatbot-prescriptions.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions.yaml) and once with `q-and-a_patient-chatbot-prescriptions-with-examples.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml). The only difference is the second file contains embedded examples in the prompt, so in principal the results should be better, but in fact, they are often the same.

> [!NOTE]
> These template files are designed for use with the `llm` CLI (see the Appendix). In our Python scripts, [LiteLLM](https://docs.litellm.ai/#basic-usage) is used to invoke inference and we extract the content we need from these files and use it to construct the prompts we send through LiteLLM.

This program passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. As the [TDD chapter](https://the-ai-alliance.github.io/ai-application-testing/arch-design/tdd/) explains, this is a very ad-hoc approach to creating and testing a _unit benchmark_.

### Run `unit-benchmark-data-synthesis`

Described in [Unit Benchmarks](https://the-ai-alliance.github.io/ai-application-testing/testing-strategies/unit-benchmarks/), this script uses an LLM to generate Q&A (question and answer) pairs for _unit benchmarks_. It addresses some of the limitations of the more ad-hoc approach to benchmark creation used in the TDD example:

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

The arguments are the same as before, but in this case, the `--data` argument specifies the location where the Q&A pairs are written, one file per unit benchmark, with subdirectories for each model used. For example, after running this script with `ollama/gpt-oss:20b`, `temp/output/data/ollama/gpt-oss_20b` (`:` is an invalid character for MacOS file paths) will have these files of synthetic Q&A pairs:

* `synthetic-q-and-a_patient-chatbot-emergency-data.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`

They cover three unit-benchmarks:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should stop using the ChatBot and call 911 (in the US) immediately.
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

The actual "answer" is one of these labels and some additional information, rather than a generated text like, "It sounds like you are having an emergency. Please call 911..."

Each of these data files are generated with a single inference invocation, with each invocation using these corresponding template files:

* `synthetic-q-and-a_patient-chatbot-emergency.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-emergency.yaml)
* `synthetic-q-and-a_patient-chatbot-prescription-refills.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-prescription-refills.yaml)
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml)

### Run `unit-benchmark-data-validation`

Described in [LLM as a Judge](https://the-ai-alliance.github.io/ai-application-testing/testing-strategies/llm-as-a-judge/), this script uses a _teacher model_ to _validate_ the quality of the Q&A pairs that were generated in the previous step:

```shell
make run-unit-benchmark-data-validation
```

After some setup, the following command is executed:

```shell
time uv run src/scripts/unit-benchmark-data-validation.py \
	--model ollama/gpt-oss:20b \
	--service-url http://localhost:11434 \
	--template-dir src/prompts/templates \
	--output temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out \
	--data temp/output/ollama/gpt-oss_20b/data
```

In this case, the `--data` argument specifies where to read the previously-generated Q&A files, and for each file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory:

* `synthetic-q-and-a_patient-chatbot-emergency-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.yaml`

These files &ldquo;rate&rdquo; each Q&A pair from 1 (bad) to 5 (great).
Also, summary statistics are written to `stdout` and to the output file `temp/output/ollama/gpt-oss_20b/unit-benchmark-data-validation.out`. Currently, we show the counts of each rating, meaning how good the _teacher LLM_ rates the Q&A pair. (For simplicity, we used the same `gpt-oss:20b` model as the _teacher_ that we used for generation). From one of our test runs a text version of the following table was written:

Files:                                                                            |    1  |    2  |    3  |    4  |    5  | Total |
| :------                                                               | ----: | ----: | ----: | ----: | ----: | ----: |
synthetic-q-and-a_patient-chatbot-emergency-data.json                             |    0  |    4  |    7  |   12  |  168  |  191  |
synthetic-q-and-a_patient-chatbot-prescription-refills-data.json                  |    0  |    0  |    0  |    0  |  108  |  108  |
synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.json              |    2  |    2  |    0  |    1  |  168  |  173  |
| | | | | | | |
Totals:                                                                           |    2  |    6  |    7  |   13  |  444  |  472  |

Total count: 475 (includes errors), total errors: 3

The teacher model is asked to provide _reasoning_ for its ratings. It is instructive to look at the output `*-validation.yaml` files that we saved in [`src/data/examples/gpt-oss_20b`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/data/examples/gpt-oss_20b).

Note that the emergency Q&A pairs had the greatest ambiguities, where the teacher model didn't think that many of the Q&A pairs represented real emergencies (lowest scores) or the situation was "ambiguous" (middle scores). 

In fact, the program deliberately ignores the actual file where the Q&A pair appears. For example, we found that the _emergency_ file contains some _refill_ and _other_ questions. Only the actual label in the answer corresponding to a question was evaluated. 

Is this okay? Each data file is supposed to be for a particular use case, yet in fact the Q&A pairs have some mixing across files. You could decide to resort by label to keep things separate or you could just concatenate all the Q&A pairs into one big set. We think the first choice is more in the spirit of how focused, automated tests are supposed to work, but it is up to you...

The same template file was used for evaluating the three data files:

* `synthetic-q-and-a_patient-chatbot-data-validation.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/prompts/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml)

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
