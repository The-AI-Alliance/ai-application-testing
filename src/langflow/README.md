# Langflow Integration for Benchmark Data Pipeline

This directory contains components and orchestration code for running the benchmark data synthesis and validation pipeline in [Langflow](https://www.langflow.org/).

## Overview

The benchmark pipeline consists of two main steps:

1. **Data Synthesis** - Generates synthetic Q&A pairs for healthcare chatbot testing
2. **Data Validation** - Validates the quality and correctness of the synthetic data

## Files

* `unit_benchmark_flow.py` - Main orchestrator that can run the pipeline programmatically or export Langflow JSON.
* `synthesizer_component.py` - Langflow custom component for data synthesis.
* `__init__.py` - Package initialization

## Usage

### Running the Pipeline Programmatically

You can run the complete pipeline (synthesis + validation):

```shell
cd src
uv run python -m langflow.unit_benchmark_flow \
    --model ollama_chat/gpt-oss:20b \
    --service-url http://localhost:11434 \
    --template-dir prompts/templates \
    --data-dir .../output/ollama_chat/gpt-oss_20b/data \
    --log-file .../output/ollama_chat/gpt-oss_20b/logs/TIMESTAMP/langflow-pipeline.log \
```

Here, `TIMESTAMP` will be the current time in the format `YYYYMMDD-HHMMSS`.

Add `--help` to see all the command-line arguments, which are the following:

* `-m, --model` - Model name to use (default: `ollama_chat/gpt-oss:20b`).
* `-s, --service-url` - Inference service URL (default: `http://localhost:11434`).
* `-t, --template-dir` - Template directory (default: `prompts/templates`).
* `-d, --data-dir` - Data directory (default: `data`).
* `-u, --use-case` - Specific use case to generate, one of `prescription-refills`, `non-prescription-refills`, or `emergency` (default: all the use cases).
* `-j, --just-stats` - Only compute validation statistics.
* `--export-json` - Export Langflow JSON definition to the specified file.
* `-l, --log-file` - Log file path (default: logs/benchmark-flow.log).
* `--log-level` - Logging level (default: INFO).

To run for a specific use case, add the `--use-case USE_CASE` argument, e.g., `--use-case "prescription refills"`

To only compute validation statistics, which skips validation, use the `--just-stats` argument.

To generate a Langflow-compatible JSON flow definition, add the `--export-json PATH` argument, e.g.,:

```shell
cd src
uv run python -m langflow.unit_benchmark_flow \
    --export-json ../flows/benchmark-pipeline.json \
    --model ollama_chat/gpt-oss:20b \
    --service-url http://localhost:11434 \
    --template-dir prompts/templates \
    --data-dir .../output/ollama_chat/gpt-oss_20b/data \
    --log-file .../output/ollama_chat/gpt-oss_20b/logs/TIMESTAMP/langflow-pipeline.log \
```

This creates a JSON file that can be imported into Langflow's visual editor.

### Using with the Langflow Application (Visual Editor) (Optional)

If you have Langflow installed, you can:

1. Export the flow JSON as shown above.
2. Import it into Langflow's UI.
3. Customize the flow visually.
4. Run it through Langflow's execution engine.

## Integration with Existing Tools

The orchestrator uses the existing `UnitBenchmarkDataSynthesizer` and `UnitBenchmarkDataValidator` classes from the `tools` directory, `unit_benchmarks.py` file.

## Testing

Unit tests are located in `src/tests/unit/langflow/` and can be run with:

```shell
make all-tests-langflow
```
