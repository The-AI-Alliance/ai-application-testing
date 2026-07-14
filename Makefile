# Makefile for the ai-application-testing website and repo example code.

# Common includes. See the end of this file, too!
include .common.mk

# Definitions for the tools and applications.
# Setting the USE_CASES to '' results in all of them being processed.
# Invoke "make JUST_STATS=--just-stats ..." to have stats generated, not validation, too.
INFERENCE_SERVICE     ?= ollama
PORT                  ?= 11434
INFERENCE_URL         ?= http://localhost:${PORT}
USE_CASES             ?= 
JUST_STATS            ?=

# A hook for passing arguments to the programs, e.g., "make APP_ARGS=--help ..."
APP_ARGS              ?=

# Different models we have used. See the "all-models-*" targets:
OLLAMA_PREFIX          = ollama_chat
MODEL_GPT_OSS         ?= ${OLLAMA_PREFIX}/gpt-oss:20b
MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}/gemma4:12b
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}/gemma4:26b
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}/gemma4:31b
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}/gemma4:e4b
MODEL_QWEN35          ?= ${OLLAMA_PREFIX}/qwen3.5:35b
MODEL_LLAMA32         ?= ${OLLAMA_PREFIX}/llama3.2:3B
MODEL_SMOLLM2         ?= ${OLLAMA_PREFIX}/smollm2:1.7b-instruct-fp16
MODEL_GRANITE4        ?= ${OLLAMA_PREFIX}/granite4:latest
MODELS                ?= ${MODEL_GPT_OSS} ${MODEL_GEMMA4} ${MODEL_QWEN35} ${MODEL_LLAMA32} ${MODEL_SMOLLM2} ${MODEL_GRANITE4} 
# Default model!
MODEL                 ?= ${MODEL_GEMMA4}

MODEL_FILE_NAME       ?= $(subst :,_,${MODEL})

# Overrides definition in .common.mk:
OUTPUT_DIR            := ${PWD}/output/${MODEL_FILE_NAME}
# DATA_DIR: Where the tools write and later read data.
# TESTS_DATA_DIR: Where test data is read. RELATIVE to ${SRC_DIR}.
DATA_DIR              := ${OUTPUT_DIR}/data
TESTS_DATA_DIR        := ${TESTS_DIR}/data
OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui

# Some specific variables passed as environment variables to the ChatBot.
# CONFIDENCE_THRESHOLD: What's the minimum confidence (out of 1.0, meaning 100%) for a response that we trust it?
# WHICH_CHATBOT: Which ChatBot implementation to use: 'agent' for ChatBotAgent or 'simple' for ChatBotSimple
CONFIDENCE_THRESHOLD  ?= 0.9
WHICH_CHATBOT         ?= agent

# Some specific variables passed as environment variables to the test suites.
# ACCUMULATE_TEST_ERRORS:   Should I run ALL prompts, then report accumulated errors? Leave EMPTY for False, non-empty for True!
# RATING_THRESHOLD:         What's the minimum rating (out of 5) for which a test prompt is "good enough" for the particular use case?
# OUTPUT_LOGS_TESTS_DIRDIR:           (Override definition) Where special AI test logs are written. RELATIVE TO ${SRC_DIR}!
# OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE: A file name pattern, where "{class_name}" will be replaced with the test class name.
# OUTPUT_LOGS_TESTS_DIRFILE_GLOB:     Just used for messages printed by targets.
ACCUMULATE_TEST_ERRORS              ?= True
RATING_THRESHOLD                    ?= 4
OUTPUT_LOGS_TESTS_DIRDIR            ?= tests/logs/${MODEL_FILE_NAME}
OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE  ?= ${OUTPUT_LOGS_TESTS_DIRDIR}/{which_chatbot}-{class_name}-${TIMESTAMP}.jsonl
OUTPUT_LOGS_TESTS_DIRFILE_GLOB      ?= ${OUTPUT_LOGS_TESTS_DIRDIR}/*-${TIMESTAMP}.jsonl

# Sampling rates for different kinds of tests.
UNIT_TESTS_DATA_SAMPLE_RATE         ?= 0.25
INTEGRATION_TESTS_DATA_SAMPLE_RATE  ?= 1.0
DATA_SAMPLE_RATE                    ?= ${UNIT_TESTS_DATA_SAMPLE_RATE}

# These directories will be relative to where the tools and apps are executed.
TOOLS_PROMPTS_TEMPLATES_DIR ?= tools/prompts/templates
CHATBOT_TEMPLATES_DIR       ?= apps/chatbot/prompts/templates
CHATBOT_TESTS_TEMPLATES_DIR ?= tests/prompts/templates
CHATBOT_DATA_DIR            ?= ${DATA_DIR}/chatbot
CHATBOT_OUTPUT_DIR          ?= ${PWD}/output
CHATBOT_API_SERVER_HOST     ?= localhost
CHATBOT_API_SERVER_PORT     ?= 8000
CHATBOT_API_SERVER          ?= ${CHATBOT_API_SERVER_HOST}:${CHATBOT_API_SERVER_PORT}

ALL_TOOLS                   ?= tdd-example-refill-chatbot unit-benchmark-data-synthesis unit-benchmark-data-validation

# We don't lint the src/tools content, because they are intended more as "scripts",
# rather than modules with higher quality expectations.
PYLINT_IGNORE_ARGS  += --ignore=${SRC_DIR}/tools,${SRC_DIR}/tools/langflow

# When you see ${CODE}${_END} without anything between them, it is there 
# to make it easier to line up multi-line description comments.

help:: help-custom
help-custom::
	$(info ${help-custom-message})

define help-custom-message
${HIGHLIGHT}Quick help for this project's specific targets:${_END}

${CODE}make help-code${_END}         # Help on the tools and example ChatBot targets.

endef

define help-code-message
${HIGHLIGHT}Quick help for this make process for the tools and ChatBot example app.${_END}

For the tools used to manage the website, run ${CODE}make help-docs${_END}.

For the following targets that run tools, there are variables defined in this Makefile
that are used to pass arguments to the commands. Run ${CODE}make print-info-code${_END} to see the
list of variables and their default definitions. Specific variables are mentioned for
the corresponding targets:

${CODE}make all-models-*${_END}       # Extract "*" as one of the other targets (such as, ${CODE}all-tools${CODE}),
${CODE}${_END}                        # that is everything to the right of ${CODE}all-models-${_END}, and 
${CODE}${_END}                        # make that target for ALL the models defined by ${CODE}MODELS${_END}:
${CODE}${_END}                        #   ${CODE}${MODELS}${_END}
${CODE}${_END}                        # (Not useful for model-agnostic targets, like ${CODE}setup${_END}...)
${CODE}${_END}                        # You can override the list of models as follows:
${CODE}${_END}                        #   ${CODE}make MODELS="..." all-models-...${_END}
${CODE}make all-tools${_END}          # Clean outputs and run all the tools using the model defined by ${CODE}MODEL${_END}.
${CODE}make all-code${_END}           # Synonym for ${CODE}all-tools${_END}.
${CODE}make run-tools${_END}          # Run all the tools (but not the ChatBot app) without cleaning first. 
${CODE}${_END}                        # Built by ${CODE}all-tools${_END}.
${CODE}make run-code${_END}           # Synonym for ${CODE}run-tools${_END}.

${CODE}make setup${_END}              # One-time setup tasks; e.g., builds target ${CODE}install-uv${_END}.
${CODE}make one-time-setup${_END}     # Synonym for ${CODE}setup${_END}.
${CODE}make install-uv${_END}         # Explain how to install ${CODE}uv${_END}.
${CODE}${_END}                        # Run ${CODE}make help-command-uv${_END} for more information.
${CODE}make install-jq${_END}         # Explain how to install ${CODE}jq${_END} (an optional CLI tool).

${CODE}make build${_END}              # Build a distribution.
${CODE}make install${_END}            # Install the code locally in development mode.

${CODE}make tests${_END}              # Following convention, this target runs the unit tests only, building
${CODE}${_END}                        # the targets ${CODE}unit-tests-non-ai${_END}", ${CODE}unit-tests-ai${_END}, and ${CODE}unit-tests-appointments${_END}.
${CODE}make test${_END}               # Synonym for ${CODE}tests${_END}.
${CODE}make unit-tests${_END}         # Synonym for ${CODE}tests${_END}.
${CODE}make unit-tests-non-ai${_END}  # All unit tests that don't involve inference invocations.
${CODE}make unit-tests-ai${_END}      # All unit tests that do involve inference invocations, which take a long time to run.
${CODE}make unit-tests-appointments${_END}
${CODE}${_END}                        # Unit tests for the appointment management tool.
${CODE}make unit-tests-langflow${_END}
${CODE}${_END}                        # Run unit tests for the Langflow components. NOT built by ${CODE}tests${_END} or ${CODE}integration-tests${_END},
${CODE}${_END}                        # so we don't force you to have Langflow installed.

${CODE}make integration-tests${_END}  # Run the integration tests, including "dedicated" integration tests
${CODE}${_END}                        # and all unit tests with more "exhaustive" sample data flags.
${CODE}make integration-tests-dedicated${_END}
${CODE}${_END}                        # The "dedicated" integration tests, omitting the unit tests.

${CODE}make all-tests${_END}          # Run the unit and integration tests.
${CODE}make all-tests-langflow${_END} # Run all the tests for the Langflow integration.

${CODE}make clean-setup${_END}        # Undoes everything done by the setup target or provides
${CODE}${_END}                        # instructions for what you must do manually in some cases.
${CODE}make uninstall-uv${_END}       # Explain how to uninstall "uv".

${TIP_LABEL}See also the list of common targets, like ${CODE}tests${_END} and ${CODE}lint${_END}, which are shown
${TIP_LABEL}by ${CODE}make help${_END}.

For tools run by the following targets, which invoke inference, the model 
${CODE}${MODEL}${_END} is served by ollama. The make variable ${CODE}MODEL${_END} specifies the model, 
so if you want to use a different model, invoke make as in this example:

  ${CODE}make MODEL=ollama_chat/llama3.2:3B run-tdd-example-refill-chatbot${_END}

See also the description of ${CODE}all-models-*${_END} above.

All the following targets may setup dependencies that are redundant most of the time,
but easy to forgot when important! See also the ${CODE}help-*${_END} targets below.

${CODE}make run-tdd-example-refill-chatbot${_END}
${CODE}${_END}                        # Run the code for the TDD example "unit benchmark".
${CODE}${_END}                        # See the TDD chapter in the website for details.
${CODE}make run-terc${_END}           # Synonym for ${CODE}run-tdd-example-refill-chatbot${_END}.
${CODE}make terc${_END}               # Synonym for ${CODE}run-tdd-example-refill-chatbot${_END}.

${CODE}make run-unit-benchmark-data-synthesis${_END}
${CODE}${_END}                        # Run the code for "unit benchmark" data synthesis.
${CODE}${_END}                        # See the Unit Benchmark chapter in the website for details.
${CODE}make run-ubds${_END}           # Synonym for ${CODE}run-unit-benchmark-data-synthesis${_END}.
${CODE}make ubds${_END}               # Synonym for ${CODE}run-unit-benchmark-data-synthesis${_END}.

${CODE}make run-unit-benchmark-data-validation${_END}
${CODE}${_END}                        # Run the code for validating the synthetic data for the unit benchmarks.
${CODE}${_END}                        # See the Unit Benchmark chapter in the website for details.
${CODE}make run-ubdv${_END}           # Synonym for ${CODE}run-unit-benchmark-data-validation${_END}.
${CODE}make ubdv${_END}               # Synonym for ${CODE}run-unit-benchmark-data-validation${_END}.

${CODE}make run-langflow-pipeline${_END}
${CODE}${_END}                        # Run the Langflow benchmark pipeline (synthesis + validation).
${CODE}${_END}                        # This orchestrates both synthesis and validation in a single flow.
${CODE}make langflow-pipeline${_END}  # Synonym for ${CODE}run-langflow-pipeline${_END}.

The following targets are for the example ChatBot application. See also the ${CODE}help-*${_END} targets next.

${CODE}make chatbot${_END}            # Run the ${CODE}${WHICH_CHATBOT}${_END} implementation of the ChatBot application.
${CODE}make run-chatbot${_END}        # Synonym for ${CODE}chatbot${_END}.
${CODE}make agent-chatbot${_END}      # Run the ${CODE}agent${_END} implementation of the ChatBot.
${CODE}make simple-chatbot${_END}     # Run the ${CODE}simple${_END} implementation of the ChatBot.

${CODE}make mcp-server${_END}         # Run the ChatBot's MCP server.
${CODE}make run-mcp-server${_END}     # Synonym for ${CODE}mcp-server${_END}.
${CODE}make api-server${_END}         # Run the ChatBot's OpenAI-compatible API server.
${CODE}make run-api-server${_END}     # Synonym for ${CODE}api-server${_END}.

Tasks for help, debugging, setup, etc.

${CODE}make help-tools${_END}         # Prints this output.
${CODE}make help-code${_END}          # Same as ${CODE}help-tools${_END}.
${CODE}make help-tools-all${_END}     # Prints this output and makes ${CODE}help-terc${_END}, ${CODE}help-ubds${_END} and ${CODE}help-ubdv${_END}.
${CODE}make help-coce-all${_END}      # Same as ${CODE}help-tools-all${_END}.

${CODE}make help-terc${_END}          # Synonym for ${CODE}help-tdd-example-refill-chatbot${_END}.
${CODE}make help-tdd-example-refill-chatbot${_END}
${CODE}${_END}                        # Show help for the TDD example code by passing the ${CODE}--help${_END} flag.

${CODE}make help-ubds${_END}          # Synonym for ${CODE}help-unit-benchmark-data-synthesis${_END}.
${CODE}make help-unit-benchmark-data-synthesis${_END}
${CODE}${_END}                        # Show help for the "unit benchmark" data synthesis code by passing the ${CODE}--help${_END} flag.

${CODE}make help-ubdv${_END}          # Synonym for ${CODE}help-unit-benchmark-data-validation${_END}.
${CODE}make help-unit-benchmark-data-validation${_END}
${CODE}${_END}                        # Show help for the synthetic data validation code by passing the ${CODE}--help${_END} flag.
${CODE}${_END}                        # Run the code for validating the synthetic data for the unit benchmarks.

${CODE}make help-langflow-pipeline${_END}
${CODE}${_END}                        # Show help for the Langflow pipeline by passing the ${CODE}--help${_END} flag.
${CODE}make help-langflow${_END}      # Synonym for ${CODE}help-langflow-pipeline${_END}.

${CODE}make help-chatbot${_END}       # Show help for the interactive ChatBot application.
${CODE}make help-mcp-server${_END}    # Show help for the ChatBot's MCP server.
${CODE}make help-api-server${_END}    # Show help for the ChatBot's OpenAI-compatible API server.

${CODE}make view-api-server-docs${_END}  # Open a browser showing the API server ${CODE}docs${_END}.
${CODE}make view-api-server-redoc${_END} # Open a browser showing the API server ${CODE}redoc${_END}.

Several CLI tools are required, like ${CODE}uv${_END}, or only needed for a few special make targets, like ${CODE}jq${_END}:

${CODE}make help-command-uv${_END}    # Prints specific information about ${CODE}uv${_END}, including installation.
${CODE}make help-command-jq${_END}    # Prints specific information about ${CODE}jq${_END}, including installation.
${CODE}make help-command-node${_END}  # Prints specific information about ${CODE}node${_END}, including installation.
endef


# Help and Other Information Targets

.PHONY: help-tools help-tools-all help-code-all

help-tools:: help-code
help-tools-all:: help-code-all
help-code-all:: help-code help-terc help-ubds help-ubdv

.PHONY: clean-tools clean-code

clean clean-tools:: clean-code

.PHONY: print-info-tools print-info-code

print-info print-info-tools:: print-info-code 
print-info-code::
	@echo "${HIGHLIGHT}For the example code and tools:${_END}"
	@echo
	@echo "  ${DARK_GREEN}MODEL:${_END}                       ${CODE}${MODEL}${_END} (the default)"
	@echo "  ${DARK_GREEN}MODELS:${_END}                      ${CODE}${MODELS}${_END}"
	@echo "  ${DARK_GREEN}${_END}                             (all of them that we explicitly list in the ${CODE}Makefile${_END})" 
	@echo "  ${DARK_GREEN}ALL_TOOLS:${_END}                   ${CODE}${ALL_TOOLS}${_END}"
	@echo "  ${DARK_GREEN}INFERENCE_SERVICE:${_END}           ${CODE}${INFERENCE_SERVICE}${_END}"
	@echo "  ${DARK_GREEN}INFERENCE_URL:${_END}               ${CODE}${INFERENCE_URL}${_END}"
	@echo "  ${DARK_GREEN}TOOLS_PROMPTS_TEMPLATES_DIR:${_END} ${CODE}${TOOLS_PROMPTS_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_TEMPLATES_DIR:${_END}       ${CODE}${CHATBOT_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_TESTS_TEMPLATES_DIR:${_END}  ${CODE}${CHATBOT_TESTS_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_OUTPUT_DIR:${_END}          ${CODE}${CHATBOT_OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}APP_ARGS:${_END}                    ${CODE}'${APP_ARGS}'${_END} (A user hook for passing custom arguments, like ${CODE}-h${_END})"
	@echo
	@echo "${HIGHLIGHT}The following depend on the value of MODEL (${MODEL}):${_END}"
	@echo
	@echo "  ${DARK_GREEN}OUTPUT_DIR:${_END}                  ${CODE}${OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}OUTPUT_LOGS_DIR:${_END}             ${CODE}${OUTPUT_LOGS_DIR}${_END}"
	@echo "  ${DARK_GREEN}OUTPUT_LOGS_TESTS_DIRDIR:${_END}              ${CODE}${OUTPUT_LOGS_TESTS_DIRDIR}${_END} (relative to ${CODE}SRC_DIR${_END} == ${CODE}${SRC_DIR}${_END})"
	@echo "  ${DARK_GREEN}DATA_DIR:${_END}                    ${CODE}${DATA_DIR}${_END}"
	@echo "  ${DARK_GREEN}ACCUMULATE_TEST_ERRORS:${_END}      ${CODE}${ACCUMULATE_TEST_ERRORS}${_END} (For tests, run all examples, then report errors. Set to ${CODE}''${_END} for ${CODE}False${_END})"
	@echo


${OUTPUT_DIR} ${OUTPUT_TESTS_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR} ${DATA_DIR} ${CHATBOT_DATA_DIR}::
	mkdir -p $@

# Code Targets

.PHONY: all-tools all-code run-tools run-code
.PHONY: run-terc run-tdd-example-refill-chatbot 
.PHONY: run-ubds run-unit-benchmark-data-synthesis 
.PHONY: run-ubdv run-unit-benchmark-data-validation 
.PHONY: before-run silent-before-run run-command-checks save-examples post-all-models
.PHONY: help-terc help-tdd-example-refill-chatbot 
.PHONY: help-ubds help-unit-benchmark-data-synthesis 
.PHONY: help-ubdv help-unit-benchmark-data-validation 

# Extract the "%" as a target, then make it for all the MODELS.
# Use the same timestamp for all of them.
all-models-% :: 
	@timestamp=${TIMESTAMP}; \
	target=${@:all-models-%=%}; \
	echo "${INFO_LABEL} Making target \"$$target\" for all models:"; \
	echo "  ${CODE}${MODELS}${_END}"; \
	for model in ${MODELS}; \
	do \
		echo && echo "${INFO_LABEL}For model = ${CODE}$$model${_END}" && \
		echo "${INFO_LABEL}${CODE}${MAKE} ${MAKEFLAGS} TIMESTAMP=${TIMESTAMP} MODEL=$$model $$target${_END}"; \
		${MAKE} ${MAKEFLAGS} TIMESTAMP=${TIMESTAMP} MODEL=$$model $$target; \
	done; \
	echo "\n${NOTE_LABEL}Output log files (if any) can be found under:${_END}"; \
	for model in ${MODELS}; \
	do \
		echo "${INFO_LABEL}  ${CODE}output/$$model/logs/${TIMESTAMP}${_END}"; \
	done

all-tools all-code:: run-tools
run-tools run-code:: 
	${MAKE} TIMESTAMP=${TIMESTAMP} ${ALL_TOOLS:%=run-%} 

terc run-terc:: run-tdd-example-refill-chatbot run-tdd-example-refill-chatbot-preamble
ubds run-ubds:: run-unit-benchmark-data-synthesis run-unit-benchmark-data-synthesis-preamble
ubdv run-ubdv:: run-unit-benchmark-data-validation run-unit-benchmark-data-validation-preamble

help-terc:: help-tdd-example-refill-chatbot
help-ubds:: help-unit-benchmark-data-synthesis
help-ubdv:: help-unit-benchmark-data-validation

${ALL_TOOLS:%=help-%}::
	@echo "${INFO_LABEL}Help on ${CODE}${@:help-%=%}.py${_END}:"
	@echo
	cd ${SRC_DIR} && uv run tools/${@:help-%=%}.py --help
	@echo

# LITELLM_LOG=ERROR turns off some annoying INFO messages, sufficient
# for our purposes. See the LiteLLM docs for logging configuration details.
# Define APP_ARGS on the command line to pass custom arguments, e.g., 
#   make APP_ARGS='--help' run-tdd-example-refill-chatbot
# just prints help.

run-tdd-example-refill-chatbot:: before-run run-tdd-example-refill-chatbot-preamble
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${NOOP} ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-tdd-example-refill-chatbot-preamble::
	@echo "${BOLD}${INFO}*** Running the TDD example.${_END}"
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%-preamble=%}.log${_END}\n"

run-unit-benchmark-data-synthesis:: before-run run-unit-benchmark-data-synthesis-preamble
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${NOOP} ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--use-cases ${USE_CASES} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-synthesis-preamble::
	@echo "${BOLD}${INFO}*** Running the unit benchmark data synthesis example.${_END}"
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%-preamble=%}.log${_END}\n"

run-unit-benchmark-data-validation:: before-run run-unit-benchmark-data-validation-preamble
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${NOOP} ${TIME} uv run tools/${@:run-%=%}.py \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-cases ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
	  ${JUST_STATS} ${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-validation-preamble::
	@echo "${BOLD}${INFO}*** Running the unit benchmark synthetic data validation example.${_END}"
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${@:run-%-preamble=%}.log${_END}\n"

before-run:: silent-before-run
	@echo "${TIP_LABEL}If errors occur, try ${CODE}make setup${_END} or ${CODE}make clean-setup setup${_END}, then try again."

silent-before-run:run-command-checks ${OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${DATA_DIR}  
run-command-checks:: command-check-uv provider-server-check

provider-server-check::
	@[[ ${INFERENCE_SERVICE} != 'ollama' ]] || ollama ps > /dev/null || ! echo "${ERROR}Ollama is not running!${_END}" || exit 1

# Langflow targets
.PHONY: run-langflow-pipeline langflow-pipeline langflow-pipeline-preamble help-langflow-pipeline  
.PHONY: unit-tests-langflow all-tests-langflow

run-langflow-pipeline:: langflow-pipeline
langflow-pipeline:: langflow-pipeline-preamble
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${NOOP} ${TIME} uv run python -m tools.langflow.unit_benchmark_flow \
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

help-lf help-langflow help-langflow-pipeline::
	@echo "${INFO_LABEL}Help on the Langflow unit benchmark pipeline:"
	cd ${SRC_DIR} && uv run python -m tools.langflow.unit_benchmark_flow --help
	@echo

all-tests-langflow unit-tests-langflow:: run-command-checks
	@echo "${INFO_LABEL} Running the langflow unit tests..."
	cd ${SRC_DIR} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export DATA_DIR=${DATA_DIR} && \
	  uv run python -m unittest discover \
	    --start-directory tests/unit/langflow \
	    --top-level-directory .

.PHONY: run-chatbot chatbot before-chatbot before-chatbot-preamble check-model-which-chatbot do-run-chatbot agent-chatbot simple-chatbot after-chatbot

run-chatbot:: chatbot
chatbot:: before-chatbot do-run-chatbot after-chatbot
do-run-chatbot::
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${NOOP} ${TIME} uv run python -m apps.chatbot.main \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${CHATBOT_TEMPLATES_DIR} \
		--data-dir ${CHATBOT_DATA_DIR} \
		--output-dir ${CHATBOT_OUTPUT_DIR} \
		--confidence-threshold ${CONFIDENCE_THRESHOLD} \
		--which-chatbot ${WHICH_CHATBOT} \
		--log-file ${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log \
		--verbose ${APP_ARGS}

agent-chatbot simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:%-chatbot=%} chatbot

.PHONY: help-chatbot help-agent-chatbot help-simple-chatbot 

help-agent-chatbot help-simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:help-%-chatbot=%} help-chatbot

help-chatbot::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.main --help

before-chatbot:: before-chatbot-preamble check-model-which-chatbot run-command-checks ${OUTPUT_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${CHATBOT_DATA_DIR}
check-model-which-chatbot::
	@if [[ ! ${MODEL} = ${OLLAMA_PREFIX}/gpt-oss ]] || [[ ! ${WHICH_CHATBOT} = agent ]]; then exit 0; else \
		echo "${ERROR_LABEL}Model ${CODE}${MODEL}${_END} currently can't be used with the ${CODE}${WHICH_CHATBOT}${_END} ChatBot!"; \
		echo "${ERROR_LABEL}(${CODE}https://github.com/langchain-ai/langchain/issues/33116${_END}). Try using model ${CODE}${MODEL_GEMMA4}${_END}, for example."; \
		exit 1; \
	fi

before-chatbot-preamble::
	@echo "${INFO_LABEL}Running the ${CODE}${WHICH_CHATBOT}${_END} ChatBot..."
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}"

after-chatbot::
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}"

.PHONY: mcp-server run-mcp-server help-mcp-server check-mcp-server inspect-mcp-server

# See inspect-mcp-server for information about ${INSPECTOR}, which is otherwise
# blank.
run-mcp-server:: mcp-server
mcp-server:: before-chatbot
	@echo "${INFO_LABEL}Running the ChatBot MCP Server..."
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${INSPECTOR} uv run python -m apps.chatbot.mcp_server.server \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${CHATBOT_TEMPLATES_DIR} \
		--data-dir ${CHATBOT_DATA_DIR} \
		--output-dir ${CHATBOT_OUTPUT_DIR} \
		--confidence-threshold ${CONFIDENCE_THRESHOLD} \
		--which-chatbot ${WHICH_CHATBOT} \
		--log-file ${OUTPUT_LOGS_DIR}/$@.log \
		${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}"

inspect-mcp-server:: command-check-node
	@echo "${INFO_LABEL}Running the ${CODE}@modelcontextprotocol/inspector${_END} with the ChatBot MCP Server..."
	${MAKE} INSPECTOR="npx @modelcontextprotocol/inspector" mcp-server

help-mcp-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.mcp_server.server --help

.PHONY: api-server run-api-server help-api-server check-api-server 
.PHONY: view-api-server-docs view-api-server-redoc view-api-server-docs-preamble

run-api-server:: api-server
api-server:: before-chatbot
	@echo "${INFO_LABEL}Running the ChatBot OpenAI-compatible API Server..."
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && uv run python -m apps.chatbot.api_server.server \
		--host ${CHATBOT_API_SERVER_HOST} \
		--port ${CHATBOT_API_SERVER_PORT} \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${CHATBOT_TEMPLATES_DIR} \
		--data-dir ${CHATBOT_DATA_DIR} \
		--output-dir ${CHATBOT_OUTPUT_DIR} \
		--confidence-threshold ${CONFIDENCE_THRESHOLD} \
		--which-chatbot ${WHICH_CHATBOT} \
		--log-file ${OUTPUT_LOGS_DIR}/$@.log \
		${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

help-api-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.api_server.server --help

check-api-server::
	@echo "${INFO_LABEL}'Sanity check' that the OpenAI-compatible API server works:"
	@echo "${INFO_LABEL}Running the server in the background..."
	${NOOP} ${MAKE} api-server & 
	@echo
	@echo "  ${HIGHLIGHT}Hit the 'return' key!${_END}"
	@echo
	@echo "${INFO_LABEL}Running ${CODE}apps/chatbot//api_server/example_client.py${_END} ..."
	@echo
	cd ${SRC_DIR} && ${NOOP} uv run python apps/chatbot/api_server/example_client.py
	@echo
	@echo " ${HIGHLIGHT}Using a hack: Find the process id for the server and kill it...${_END}" 
	@echo
	${NOOP} kill %1

view-api-server-docs view-api-server-redoc:: view-api-server-docs-preamble
	@uv run python -m webbrowser "http://${CHATBOT_API_SERVER}/${@:view-api-server-%=%}"

view-api-server-docs-preamble::
	@echo
	@echo "${INFO_LABEL}Opening ${HIGHLIGHT}http://${CHATBOT_API_SERVER}/${@:view-api-server-%=%}${_END}"
	@echo "${open-url-message}"
	@echo "${INFO_LABEL}If the URL isn't found, make sure the server is running! For example,"
	@echo "${INFO_LABEL}run ${CODE}make api-server${_END} in another terminal window, then rerun this target." 

.PHONY: run-open-webui open-webui open-webui-preamble open-webui-setup help-open-webui remove-open-webui

run-open-webui open-webui:: open-webui-preamble open-webui-setup
	cd ${OPEN_WEBUI_DIR} && \
		DATA_DIR=${CHATBOT_DATA_DIR} uv tool run --with greenlet open-webui serve

open-webui-preamble::
	@echo "${INFO_LABEL}Running Open WebUI (${CODE}https://docs.openwebui.com/getting-started/${_END}) out of directory ${CODE}${OPEN_WEBUI_DIR}${_END}."
	@echo "${INFO_LABEL}Make sure the OpenAI-compatible API Server is running first, i.e., ${CODE}make api-server${_END} in another terminal!"
	@echo "${INFO_LABEL}"
	@echo "${INFO_LABEL}Open ${CODE}http://localhost:8080${_END} when it is up (it takes a few minutes)."
	@echo "${open-url-message}"

open-webui-setup::
	@test -d ${OPEN_WEBUI_DIR}/.venv || (\
		echo "${INFO_LABEL}Setting up Open WebUI in the ${CODE}${OPEN_WEBUI_DIR}${_END} directory." && \
		cd ${OPEN_WEBUI_DIR} && uv venv && uv sync && uv tool install open-webui)
	cd ${OPEN_WEBUI_DIR} && . .venv/bin/activate

help-open-webui:: 
	DATA_DIR=${CHATBOT_DATA_DIR} uvx --python 3.13 --with greenlet open-webui@latest serve --help

remove-open-webui::
	uv tool uninstall open-webui
	rm -rf $HOME/.open-webui

.PHONY: all-tests note-all-tests test tests unit-tests unit-tests-non-ai 
.PHONY: unit-tests-ai unit-tests-ai-agent unit-tests-ai-simple
.PHONY: integ-tests integration-tests integration-tests-dedicated unit-tests-as-integration-tests

all-tests:: note-all-tests unit-tests-non-ai integration-tests
note-all-tests::
	@echo "${NOTE_LABEL}The ${CODE}all-tests${_END} target does ${BOLD}${RED}NOT${_END} run the AI-related unit tests!"
	@echo "${NOTE_LABEL}"
	@echo "${NOTE_LABEL}The integration tests are a strict superset of the unit tests, they run"
	@echo "${NOTE_LABEL}the same suite, but with all Q&A examples sampled, etc., plus some other"
	@echo "${NOTE_LABEL}integration tests. We do this so we don't run those (expensive) tests 'twice'."
	@echo

test tests unit-tests:: run-command-checks unit-tests-non-ai unit-tests-ai unit-tests-appointments

# The --pattern argument is unnecessary here, as we pass the default value, but it is
# included for "symmetry" with the unit-tests-ai target.
unit-tests-non-ai::
	@echo "${INFO_LABEL}Running the non-AI unit tests..."
	cd ${SRC_DIR} && \
	  uv run python -m unittest discover \
	    --pattern 'test*.py' \
	    --start-directory tests/unit \
	    --top-level-directory .

.PHONY: unit-tests-appointments

unit-tests-appointments::
	@echo "${INFO_LABEL}Running the appointment tool unit tests..."
	cd ${SRC_DIR} && \
	  uv run python -m unittest discover \
	    --pattern 'test_appointment*.py' \
	    --start-directory tests/unit/apps/chatbot \
	    --top-level-directory .

unit-tests-ai:: unit-tests-ai-agent unit-tests-ai-simple

# The "funky" ending command line, "uv run ... && make ... || ! make ...", is a hack
# to make the "show-test-logs" target whether or not the tests pass, and also
# effectively return success (==0) or failure (!=0) status from the tests.
# (Note we are in the src directory so we have to tell make to go to the parent...)
unit-tests-ai-agent unit-tests-ai-simple:: ${OUTPUT_TESTS_DIR} ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR} 
	@echo "${INFO_LABEL}Running the AI unit tests with the ${CODE}${@:unit-tests-ai-%=%}${_END} ChatBot..."
	@echo "${INFO_LABEL}AI test log files: ${CODE}${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRFILE_GLOB}${_END}"
		cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
    export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
    export CHATBOT_TESTS_TEMPLATES_DIR=${CHATBOT_TESTS_TEMPLATES_DIR} && \
	  export DATA_DIR=${TESTS_DATA_DIR} && \
	  export OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE=${OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export WHICH_CHATBOT=${@:unit-tests-ai-%=%} && \
	  export VERBOSE='True' && \
	  ${TIME} uv run python -m unittest discover \
	  	--pattern 'ai_test*.py' \
	  	--start-directory tests/unit \
	  	--top-level-directory . ${APP_ARGS}
	  ${MAKE} OUTPUT_LOGS_TESTS_DIRFILE_GLOB=${OUTPUT_LOGS_TESTS_DIRFILE_GLOB} --directory .. post-proc-test-logs


# A special target for running one of the AI tests. Invoke as follows:
# make TEST=tests/.../ai_test_foo.py WHICH_CHATBOT=agent|simple one-test-ai
# Note that src is considered the root directory for TEST.

one-test-ai:: ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR}
	@echo "${INFO_LABEL}Running one AI unit test: TEST = ${TEST} ..."
	@echo "${TIP_LABEL}Use ${CODE}make list-unit-tests-ai${_END} to see the list of tests."
	@echo "${INFO_LABEL}AI test log files: ${CODE}${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRFILE_GLOB}${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
    export CHATBOT_TESTS_TEMPLATES_DIR=${CHATBOT_TESTS_TEMPLATES_DIR} && \
	  export DATA_DIR=${TESTS_DATA_DIR} && \
	  export OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE=${OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export WHICH_CHATBOT=${WHICH_CHATBOT} && \
	  export VERBOSE='True' && \
	  ${TIME} uv run python -m unittest ${TEST}
	  ${MAKE} OUTPUT_LOGS_TESTS_DIRFILE_GLOB=${OUTPUT_LOGS_TESTS_DIRFILE_GLOB} --directory .. post-proc-test-logs

.PHONY: list-unit-tests-ai
list-unit-tests-ai::
	cd ${SRC_DIR} && find . -name 'ai_test*.py'

.PHONY: post-proc-test-logs show-test-logs

post-proc-test-logs:: 
	@echo
	@echo "${INFO_LABEL}Time-stamped JSONL log files were written to:"
	@echo "  ${CODE}${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRFILE_GLOB}${_END}"
	@echo "${INFO_LABEL}(They may be empty!)"
	@echo "${INFO_LABEL}The corresponding ${CODE}*.json${_END} files (if any) were generated"
	@echo "${INFO_LABEL}using ${CODE}jq${_END} and target ${CODE}nice-ai-test-logs${_END}. They are easier to read."
	@echo "${INFO_LABEL}"
	@echo "${INFO_LABEL}  ${CODE}${MAKE} nice-ai-test-logs${_END}"
	@echo "${INFO_LABEL}  ${CODE}${MAKE} show-test-logs${_END}"

show-test-logs::
	@ls -l ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR}/*.json*
	@echo
	@echo "${TIP_LABEL}Run ${CODE}make nice-ai-test-logs${_END} to make a nicely-formatted JSON file from each JSONL file."
	@echo "${TIP_LABEL}(The ${CODE}jq${_END} CLI tool required.)"
	@echo 

.PHONY: nice-ai-test-logs

# This target nicely formats the AI-related test logs into more readable JSON. Requires jq
nice-ai-test-logs:: silent-command-check-jq 
	@for f in ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR}/*.jsonl; do ff=$${f%l}; [[ -f $$ff  ]] || \
	  echo "${INFO_LABEL}Writing ${CODE}$$ff${_END}:"; \
	  jq . $$f > $$ff; \
	done
	@echo "${INFO_LABEL}Contents of ${CODE}${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR}/*.json*:${_END}"
	@ls -l ${SRC_DIR}/${OUTPUT_LOGS_TESTS_DIRDIR}/*.json*

integ-tests integration-tests:: integration-tests-dedicated integration-tests-from-unit-tests

# This target runs all the unit-tests, the AI-related, but more exhaustively, as well as the non-AI unit tests.
integration-tests-from-unit-tests:: run-command-checks
	@echo "${INFO_LABEL}Running the unit tests as integration tests with 100% sampling and trying all test query examples..."
	${MAKE} DATA_SAMPLE_RATE=${INTEGRATION_TESTS_DATA_SAMPLE_RATE} tests

integration-tests-dedicated:: run-command-checks
	@echo "${INFO_LABEL}Running the 'dedicated' integration tests..."
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${INTEGRATION_TESTS_DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
	  export DATA_DIR=${TESTS_DATA_DIR} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export VERBOSE='True' && \
	  uv run python -m unittest discover \
	  	--start-directory tests/integration \
	  	--top-level-directory .


# The next section of this Makefile includes some convenience targets for working 
# with the "llm" CLI tool. It is NOT required to install and use this tool.
# See the Appendix in the README.md for details.

define help_message_llm

The ${CODE}llm${_END} CLI is used by many of the tools here. For more details, see:
  ${CODE}https://github.com/simonw/llm${_END}

You can install ${CODE}llm${_END} using ${CODE}uv${_END}:
  ${CODE}uv add -U llm bs4${_END}
or if you use ${CODE}pip${_END}:
  ${CODE}pip install -U llm bs4${_END}

To remove ${CODE}llm${_END}, use the corresponding commands, one of:
  ${CODE}pip uninstall llm bs4${_END}
  ${CODE}uv remove llm bs4${_END}

If you want to serve models locally using ${CODE}ollama${_END}, see the installation 
instructions:
  ${CODE}https://ollama.com${_END}

Then install the ${CODE}llm${_END} plugin for ${CODE}ollama${_END}:
  ${CODE}llm install llm-ollama${_END}

The tools also use several ${CODE}llm${_END} "templates". These need to be installed into
the directory output by this ${CODE}llm${_END} command:
  ${CODE}llm templates path${_END}

Use the following ${CODE}make${_END} command to do this automatically:
  ${CODE}make install-llm-templates${_END}

${WARNING_LABEL}If you edit the templates in ${CODE}${TOOLS_PROMPTS_TEMPLATES_DIR}${_END}, rerun  
  ${CODE}make install-llm-templates${_END}

(${CODE}llm${_END} is required to run this target, because it uses ${CODE}llm templates path${_END}
to determine the installation location.)

So, to summarize the ${CODE}llm${_END}-related targets (and mention the rest of them):
 
${CODE}make help-llm${_END}               # This information!
${CODE}make install-llm${_END}            # Instructions for installing ${CODE}llm${_END}.
${CODE}make install-llm-templates${_END}  # Install our ${CODE}llm${_END} "templates" into ${CODE}llm${_END}.
${CODE}make clean-llm${_END}              # Instructions for uninstalling ${CODE}llm${_END}. Also makes ${CODE}clean-llm-templates${_END}.
${CODE}make clean-llm-templates${_END}    # Remove our ${CODE}llm${_END} "templates" from the ${CODE}llm${_END} installation location.

endef

.PHONY: help-llm clean-llm clean-llm-templates install-llm

help-llm::
	$(info ${help_message_llm})
	@echo

clean-llm:: help-llm clean-llm-templates
	@echo
	@echo "${NOTE_LABEL}The command ${CODE}make clean-llm-templates${_END} was already executed to uninstall our templates."
	@echo

clean-llm-templates::
	@cd ${TOOLS_PROMPTS_TEMPLATES_DIR} && \
		llmdir="$$(llm templates path)" && \
		for t in *.yaml; do \
			echo "${INFO_LABEL}Removing: ${CODE}$$llmdir/$$t${_END}"; \
			rm -f "$$llmdir/$$t"; \
		done && \
		ls -l "$$llmdir"

install-llm:: help-llm install-llm-templates
	@echo
	@echo "${NOTE_LABEL}The command ${CODE}make install-llm-templates${_END} was already executed to install our templates."
	@echo

install-llm-templates:: command-check-llm
	@llmdir="$$(llm templates path)" && \
	echo "${INFO_LABEL}Installing the ${CODE}llm${_END} templates from ${CODE}${TOOLS_PROMPTS_TEMPLATES_DIR}${_END} into ${CODE}$$llmdir${_END} ..." && \
	cp ${TOOLS_PROMPTS_TEMPLATES_DIR}/*.yaml "$$llmdir" && \
	ls -l "$$llmdir"


.PHONY: build install

build::
	@echo "${INFO_LABEL}Building a distribution..."
	rm -rf dist
	uv build
	@echo "${INFO_LABEL}Contents of 'dist':"
	@ls -l dist

install::
	@echo "${INFO_LABEL}Installing the code locally in development mode..."
	uv sync

# Common includes. See the beginning of this file, too!
# The reason the following are put at the end, rather than the beginning, is to 
# control the ordering of dependencies for "global" targets, like "help".
include .website.mk
