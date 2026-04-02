# Langflow Integration for Benchmark Data Pipeline

This directory contains preliminary support for the components and orchestration code required to run the benchmark data synthesis and validation pipeline in [Langflow](https://www.langflow.org/).

> **NOTE:** the `make type-check` target, which uses `ty`, skips this directory, so that we don't have to add the langflow dependency to the project, since not everyone will want to use it.

## Overview

The benchmark pipeline consists of two main steps, but in one Langflow component:

1. **Data Synthesis** - Generates synthetic Q&A pairs for healthcare chatbot testing
2. **Data Validation** - Validates the quality and correctness of the synthetic data

## Files

* `unit_benchmark_flow.py` - Main orchestrator that can run the pipeline programmatically.
* `synthesizer_component.py` - Langflow custom component for data synthesis and validation.
* `__init__.py` - Package initialization

## Usage

### Running the Pipeline Programmatically

You can run the complete pipeline (synthesis + validation) using `make` or an explicit command:

```shell
make run-langflow-pipeline

# Or showing the default arguments the make target uses:
cd src
uv run python -m tools.langflow.unit_benchmark_flow \
    --model ollama_chat/gpt-oss:20b \
    --service-url http://localhost:11434 \
    --template-dir prompts/templates \
    --data-dir .../output/ollama_chat/gpt-oss_20b/data \
    --log-file .../output/ollama_chat/gpt-oss_20b/logs/TIMESTAMP/langflow-pipeline.log \
```

Here, `TIMESTAMP` will be the current time in the format `YYYYMMDD-HHMMSS`.

Run `make help-langflow-pipeline` for a complete list and description of the command-line arguments. For example, there are three steps executed by default, with flags to have the tool all or a few of them:

* `--just-synthesis` - Only run the synthesis step, generating data files written to the directory specified by `--data-dir`.
* `--just-validation` - Only run the validation step, which analyzes the synthetic data files it finds in the data directory and writes companion files there. Some final statistics are printed from the validation analysis.
* `--just-stats` - Just print the statistics. Requires that the validation files are present in the data directory. (This is a useful flag for some quick sanity testing, too.)

Also, by default, all the _use cases_ for which prompt files are found in `src/prompts/templates` are processed. Pass `--use-case USE_CASE` to run process just a single use case. The valid values for `USE_CASE` are:

* `prescription-refills`
* `non-prescription-refills`
* `emergency`

(This tool only allows one of them to be specified, in contrast to the underlying tools themselves.)

If you want to use the `make` target and pass any of these arguments, use the `APP_ARGS` variable, for example:

```shell
make APP_ARGS="--just-validation --use-case emergency" run-langflow-pipeline
```

### Use in the Langflow Application (Visual Editor)

Install the [Langflow desktop app](https://langflow.org). 

At this time, until we have a pip-installable release of this project's tools, you will have to build this project, then install the local _wheel_ file in the [Langflow app](https://langflow.org). Do the follow steps.

First check that the file `$HOME/.langflow/data/requirements.txt` exists. If not, run the Langflow application once, then exist, which should create the directory and the necessary files.

Now, in a terminal window in the root directory of this project, run these commands:

```shell
make build
echo $PWD/dist/*.whl >> $HOME/.langflow/data/requirements.txt
```

This will add the local path to the wheel so Langflow can find the code.

Start (or restart...) the Langflow app:

1. Click the _New flow_ button on the upper left.
1. In the popup, select _Blank flow_.
1. Drag and drop the JSON flow file, [`src/tools/langflow/Unit-Benchmark-Data-Synthesis.json`](https://github.com/The-AI-Alliance/ai-application-testing/tree/main/src/tools/langflow/Unit-Benchmark-Data-Synthesis.json), onto the canvas. You should see two components:
    1. The main _orchestrator_ component, with controls for specifying paths, etc. analogous to the CLI options discussed above.
    1. A file component for writing the results to a local file, S3 location, etc.
1. Fill in the desired values in the _orchestrator_ comopnent. Some default values are shown. Note where paths start with `...`; they need to be replaced with absolute paths: 
    1. Specify your preferred model.
    1. Specify the service URL.
    1. Enter the _absolute_ path to the `src/prompts/templates` directory in this repo or copy that directory somewhere else more convenient and use that path.
    1. Enter the _absolute_ path to _either_ the `data` directory used in the CLI commands above or to another more convenient location. This is an output directory, so anywhere is fine.
    1. For the _Use Case_ field, leave it blank to process all use cases or enter one of the values discussed above for the `--use-case` CLI option.
1. Fill in the output location in the _Write Output_ component, enter an _absolute_ path to the output file (or pick an S3 location, etc.).
4. Run the flow by clicking the right-pointing triangle on the upper right-hand side of the orchestrator component.

Expect it to run for many minutes!

## How the Orchestrator Works

The `UnitBenchmarkFlowOrchestrator` in the `tools.langflow.unit_benchmark_flow.py` file drives the existing `tools/UnitBenchmarkDataSynthesizer` and `tools/UnitBenchmarkDataValidator` classes, in `unit_benchmarks.py`.

## Testing

Very basic tests (they need more work...) are located in `src/tests/unit/langflow/`. They are executed as part of the unit tests, but they can also be run separately with:

```shell
make all-tests-langflow
```
