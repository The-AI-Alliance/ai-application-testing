# README for Achieving Confidence in Enterprise AI Applications

[Published Documentation](https://the-ai-alliance.github.io/ai-application-testing/)

This repo contains the code and documentation for the AI Alliance user guide and tools for _Achieving Confidence in Enterprise AI Applications_, which explores the inherent difficulties for enterprise developers who need to right the kinds of repeatable, reliable, and automatable tests they are accustomed to writing, but which are much more challenging with generative AI models involved. This is because non-Gen AI software is (mostly) deterministic and hence predictable, while Gen AI outputs are _stochastic_, governed by a random probability model.

This project contains the website for the user guide, with the GitHub Pages content in the `docs` folder, and example code in the `src` folder.

## Trying the Tools Yourself!

Here, we discuss how to setup and execute the tools, but you'll need to read the corresponding user guide sections for details about what they are doing and how they work.

### Setup

Clone the project [repo](https://github.com/The-AI-Alliance/ai-application-testing/) and run the following `make` command to do "one-time" setup steps, such as installing tools required. Assuming you are in the repo root directory, run this command:

```shell
make one-time-setup 
```

> [!TIP]
> Try `make help` for details about the `make` process. There are also `--help` options for example scripts discussed below.

This target provides instructions for how to install required tools, like [`uv`](https://docs.astral.sh/uv/), the Python package management system, and [`jq`](https://jqlang.org), the JSON parsing CLI tool. 

Other tools are installed automatically by `one-time-setup`, like the excellent [`llm` CLI tool](https://github.com/simonw/llm) from Simon Willison and the JSON parsing CLI tool [`jq`](https://jqlang.org/download/).

Also installed are our `llm` &ldquo;templates&rdquo;, which we use define system prompts, etc. for several tools. To do this yourself, start by running the following command to see where `llm` has templates installed on your system: 

```shell
llm templates path
```

On MacOS, it will be `$HOME/Library/Application Support/io.datasette.llm/templates`. In the repo, copy all the YAML files in the [`src/llm/templates`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates) directory to the correct location for templates.

Finally, the `one-time-setup` process will tell you to install [`ollama`](https://ollama.com) if you plan to use it for local inference.

If you install `ollama`, download your models of choice. By default, we use `gpt-oss:20b` in our examples, but this is too large for many developer machines (see TIP below). We have also had good results with `llama3.2:3B`. To install one or both of these models, use these commands:

```shell
ollama pull llama3.2:3B
ollama pull gpt-oss:20b
```

(Yes, it is `B` for one and `b` for the other, as shown...)

> [!TIP]
> Using `ollama` for local inference, we observed the following while testing. On Apple computers with M1 Max chips, 32GB of memory was not enough for `gpt-oss:20b`, when a normal load of other applications was also running, but there was sufficient memory for `llama3.2:3B`. Having 64GB of memory allowed `gpt-oss:20b` to work well. Pick a small enough model that you can run, but keep in mind that the quality of the output will decrease for smaller models.

### Running the Examples with `make`

Use `make` to run the examples. The actual commands are printed out, so you can run them subsequently without `make`, if you prefer. You can run the scripts directly or use `make`. 

### Run `tdd-example-refill-chatbot`

This example is explained in user guide's section on [Test-Driven Development](https://the-ai-alliance.github.io/ai-application-testing/arch-design/tdd/).

Run this `make` command:

```shell
make run-tdd-example-refill-chatbot 
```

> [!TIP]
> If you aren't using our default model, `ollama/gpt-oss:20b`, there are two ways to specify your preferred model:
> 1. Edit [`src/Makefile`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/Makefile) and change the defintion of `MODEL` to be your choice, e.g., `ollama/llama3.2:3B`. This will make the change permanent for all examples.
> 1. Override the definition of `MODEL` when you run `make`: `MODEL=ollama/llama3.2:3B make run-tdd-example-refill-chatbot`

This does some setup, then runs this command (default arguments):

```shell
./src/scripts/tdd-example-refill-chatbot.sh --model ollama/gpt-oss:20b --output temp/output/tdd-example-refill-chatbot.out
```

This invokes `llm` twice, once with the template file `q-and-a_patient-chatbot-prescriptions.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/q-and-a_patient-chatbot-prescriptions.yaml) and once with `q-and-a_patient-chatbot-prescriptions-with-examples.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/q-and-a_patient-chatbot-prescriptions-with-examples.yaml). The script passes a number of hand-written prompts that are either prescription refill requests or something else, then checks what was returned by the model. As the [TDD section]() explains, this is a very ad-hoc approach to creating and testing a _unit benchmark_.

### Run `unit-benchmark-data-synthesis.sh`

Described in [Unit Benchmarks](https://the-ai-alliance.github.io/ai-application-testing/testing-strategies/unit-benchmarks/), this script uses `llm` to generate Q&A pairs for _unit benchmarks_:

```shell
make run-unit-benchmark-data-synthesis
```

After some setup, the following command is executed:

```shell
./src/scripts/unit-benchmark-data-synthesis.sh --model ollama/gpt-oss:20b --data temp/output/data
```

The `--data` argument specifies where the Q&A pairs are written, one file per unit benchmark, with subdirectories for each model used. For example, after running this script with `gpt-oss:20b` (the `ollama/` prefix is not included), `temp/output/data/gpt-oss_20b` will have these files of synthetic Q&A pairs:

* `synthetic-q-and-a_patient-chatbot-emergency-data.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml`

They cover three unit-benchmarks:
* `emergency`: The patient prompt suggests the patient needs urgent or emergency care, so they should call 911 (in the US).
* `refill`: The patient is asking for a prescription refill.
* `other`: (i.e., `non-prescription-refills`) All other patient questions.

These files are generated with three invocations of `llm`, each using one of the following, corresponding template files:

* `synthetic-q-and-a_patient-chatbot-emergency.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/synthetic-q-and-a_patient-chatbot-emergency.yaml)
* `synthetic-q-and-a_patient-chatbot-prescription-refills.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/synthetic-q-and-a_patient-chatbot-prescription-refills.yaml)
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/synthetic-q-and-a_patient-chatbot-non-prescription-refills.yaml)


### Run `unit-benchmark-data-validation.sh`

Described in [LLM as a Judge](https://the-ai-alliance.github.io/ai-application-testing/testing-strategies/llm-as-a-judge/), this script uses `llm` to _validate_ how good the Q&A pairs are that we just generated, using a _teacher model_:

```shell
make run-unit-benchmark-data-validation
```

After some setup, the following command is executed:

```shell
./src/scripts/unit-benchmark-data-validation.sh --model ollama/gpt-oss:20b --data temp/output/data
```

The `--data` argument specifies where the previously-generated Q&A pairs are read from, actually `temp/output/data/gpt-oss_20b` if `gpt-oss:20b` is used. For each Q&A file, a corresponding &ldquo;validation&rdquo; file is written back to the same directory:

* `synthetic-q-and-a_patient-chatbot-emergency-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-non-prescription-refills-data-validation.yaml`
* `synthetic-q-and-a_patient-chatbot-prescription-refills-data-validation.yaml`

These files &ldquo;rate&rdquo; each Q&A pair from 1 (bad) to 5 (great).
Also, summary statistics are written to `stdout`, counts of each rating. From one of our test runs a text version of the following table was written:

| Files:                                                                |    1  |    2  |    3  |    4  |    5  | Total |
| :------                                                               | ----: | ----: | ----: | ----: | ----: | ----: |
| synthetic-q-and-a_patient-chatbot-emergency-data.yaml:                |    0  |    0  |    2  |   10  |   44  |   56  |
| synthetic-q-and-a_patient-chatbot-non-prescription-refills-data.yaml: |    0  |    0  |    0  |    1  |   81  |   82  |
| synthetic-q-and-a_patient-chatbot-prescription-refills-data.yaml:     |    0  |    0  |    0  |    0  |   55  |   55  |

The files also contain reasons for the their ratings,  which are instructive to read. Note that the emergency Q&A pairs had the greatest ambiguities, where the _teacher model_ didn't think they represented real emergencies in two cases and it was &ldquo;skeptical&rdquo; in ten cases.

These files are generated with three invocations of `llm`, each using one of the data files and the same template file:

* `synthetic-q-and-a_patient-chatbot-data-validation.yaml`(https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/llm/templates/synthetic-q-and-a_patient-chatbot-data-validation.yaml)

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

The documentation for this repo is published using [GitHub Pages](https://pages.github.com/). See [GITHUB_PAGES](GITHUB_PAGES.md) for details.
