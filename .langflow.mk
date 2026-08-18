# Definitions for the API server support.

OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui

define help-langflow-message
${HIGHLIGHT} Quick help for the make targets for the Langflow support for some of the tools. ${_END}

${CODE}make run-langflow-pipeline${_END}
${CODE}${_END}                        # Run the Langflow pipeline.
${CODE}make run-langflow${_END}       # Synonym for ${CODE}run-langflow-pipeline${_END}.
${CODE}make langflow-pipeline${_END}  # Synonym for ${CODE}run-langflow-pipeline${_END}.
${CODE}make help-langflow-cli${_END}  # Run the Langflow server with the --help flag to show its CLI options.
endef


# Langflow targets
.PHONY: run-langflow-pipeline run-langflow langflow-pipeline langflow-pipeline-preamble show-langflow-cli
.PHONY: unit-tests-langflow

run-langflow-pipeline run-langflow:: langflow-pipeline
langflow-pipeline:: langflow-pipeline-preamble
	export LITELLM_LOG=ERROR; \
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/langflow/unit_benchmark_flow.py \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-case ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/$@.log \
	  ${JUST_STATS} ${APP_ARGS}
	@echo "${INFO_LABEL} Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

langflow-pipeline-preamble::
	@echo "${INFO_LABEL} Running the Langflow unit benchmark pipeline (synthesis + validation)..."
	@echo "${INFO_LABEL} Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:%-preamble=%}.log${_END}\n"

help-langflow-cli::
	@echo "${INFO_LABEL}Help on the Langflow unit benchmark pipeline:"
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/langflow/unit_benchmark_flow.py --help
	@echo

unit-tests-langflow:: run-command-checks
	@echo "${INFO_LABEL} Running the langflow unit tests..."
	${MAKE} WHICH_TESTS=tests/unit/langflow unit-tests
