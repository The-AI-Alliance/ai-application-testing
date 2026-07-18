# Makefile for the ai-application-testing website and repo example code.

# Common includes. See the end of this file, too!
# See the discussion of MODEL_APPENDIX in .common.mk or README.md. If you
# want to set a specific value, e.g., for a quantized model, define it here
# before the include .common.mk line.
# MODEL_APPENDIX = ...

# By default we DON'T run all the unit tests, because the AI-based tests are
# slow and expensive, so we filter them by default using the following:
PYTEST_RUN_OPT_ARGS ?= -m 'not ai'

# This project further divides src/tests into src/tests/unit, src/tests/integration,
# etc., so we define two new variables for unit and integration test locations, then
# "predefine" WHICH_TESTS to have the default value equal to TESTS_UNIT_DIR. Several
# targets below nest invocations of make with different definitions, e.g., to pick
# specific tests, use TESTS_INTEGRATION_DIR, etc.
TESTS_UNIT_DIR        ?= src/tests/unit
TESTS_INTEGRATION_DIR ?= src/tests/integration
WHICH_TESTS           ?= ${TESTS_UNIT_DIR}

include .common.mk

# Definitions for the tools and applications.
# See the README.md for instructions on what definitions to change to
# use alternatives to ollama.
# Setting the USE_CASES to '' results in all of them being processed.
# Invoke "make JUST_STATS=--just-stats ..." to have stats generated, not validation, too.
# If you don't use ollama, set OLLAMA_PREFIX to be empty.

INFERENCE_SERVICE     ?= ollama
OLLAMA_PREFIX         ?= ollama_chat/
PORT                  ?= 11434
INFERENCE_URL         ?= http://localhost:${PORT}
USE_CASES             ?=
JUST_STATS            ?=

# NOTE: Export variables that we want to be visible inside apps as environment variables:

export INFERENCE_SERVICE
export INFERENCE_URL


# A hook for passing arguments to the programs, e.g., "make APP_ARGS=--help ..."
APP_ARGS              ?=

# Different models we have used. See the "all-models-*" targets.
# MODEL_APPENDIX is set in .common.mk and will be "-mlx" when executed on
# Apple Silicon Macs. This "appendix" is used for models that have MLX-optimized
# variants.
MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}gemma4:12b${MODEL_APPENDIX}
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}gemma4:26b${MODEL_APPENDIX}
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}gemma4:31b${MODEL_APPENDIX}
# MODEL_GEMMA4          ?= ${OLLAMA_PREFIX}gemma4:e4b${MODEL_APPENDIX}
MODEL_GPT_OSS         ?= ${OLLAMA_PREFIX}gpt-oss:20b
MODEL_GRANITE4        ?= ${OLLAMA_PREFIX}granite4.1:8b
MODEL_LLAMA32         ?= ${OLLAMA_PREFIX}llama3.2:3B
MODEL_QWEN35          ?= ${OLLAMA_PREFIX}qwen3.5:35b${MODEL_APPENDIX}
MODELS                ?= ${MODEL_GEMMA4} ${MODEL_GPT_OSS} ${MODEL_GRANITE4} ${MODEL_LLAMA32} ${MODEL_QWEN35}

# Default model!
MODEL                 ?= ${MODEL_GEMMA4}
MODEL_FILE_NAME       ?= $(subst :,_,${MODEL})

export MODEL

# Overrides definition in .common.mk:
# DATA_DIR: Where the tools write and later read data.
# TESTS_DATA_DIR: Where test data is read. RELATIVE to ${SRC_DIR}.
OUTPUT_DIR            := output/${MODEL_FILE_NAME}
DATA_DIR              := ${OUTPUT_DIR}/data
TESTS_DATA_DIR        := ${TESTS_DIR}/data

OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui

# Some specific variables passed as environment variables to the ChatBot.
# CONFIDENCE_THRESHOLD: What's the minimum confidence (out of 1.0, meaning 100%) for a response that we trust it?
# WHICH_CHATBOT: Which ChatBot implementation to use: 'agent' for ChatBotAgent or 'simple' for ChatBotSimple
export CONFIDENCE_THRESHOLD  ?= 0.9
export WHICH_CHATBOT         ?= agent

# Some specific variables passed as environment variables to the test suites.
# ACCUMULATE_TEST_ERRORS:   Should I run ALL prompts, then report accumulated errors? Leave EMPTY for False, non-empty for True!
# RATING_THRESHOLD:         What's the minimum rating (out of 5) for which a test prompt is "good enough" for the particular use case?
# OUTPUT_LOGS_TESTS_DIRDIR:           (Override definition) Where special AI test logs are written. RELATIVE TO ${SRC_DIR}!
# OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE: A file name pattern, where "{class_name}" will be replaced with the test class name.
# OUTPUT_LOGS_TESTS_DIRFILE_GLOB:     Just used for messages printed by targets.
export ACCUMULATE_TEST_ERRORS              ?= True
export RATING_THRESHOLD                    ?= 4
export OUTPUT_LOGS_TESTS_DIRDIR            ?= ${OUTPUT_DIR}/tests/logs/${MODEL_FILE_NAME}
export OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE  ?= ${OUTPUT_LOGS_TESTS_DIRDIR}/{which_chatbot}-{class_name}-${TIMESTAMP}.jsonl
export OUTPUT_LOGS_TESTS_DIRFILE_GLOB      ?= ${OUTPUT_LOGS_TESTS_DIRDIR}/*-${TIMESTAMP}.json*

# Sampling rates for different kinds of tests.
UNIT_TESTS_DATA_SAMPLE_RATE         ?= 0.25
INTEGRATION_TESTS_DATA_SAMPLE_RATE  ?= 1.0
export DATA_SAMPLE_RATE             ?= ${UNIT_TESTS_DATA_SAMPLE_RATE}

# These directories will be relative to where the tools and apps are executed.
export TOOLS_PROMPTS_TEMPLATES_DIR ?= ${SRC_DIR}/tools/prompts/templates
export CHATBOT_TEMPLATES_DIR       ?= ${SRC_DIR}/apps/chatbot/prompts/templates
export CHATBOT_TESTS_TEMPLATES_DIR ?= ${SRC_DIR}/tests/prompts/templates
export CHATBOT_DATA_DIR            ?= ${DATA_DIR}/chatbot
export CHATBOT_OUTPUT_DIR          ?= ${OUTPUT_DIR}/chatbot
CHATBOT_API_SERVER_HOST            ?= localhost
CHATBOT_API_SERVER_PORT            ?= 8000
export CHATBOT_API_SERVER          ?= ${CHATBOT_API_SERVER_HOST}:${CHATBOT_API_SERVER_PORT}

ALL_TOOLS                   ?= tdd-example-refill-chatbot unit-benchmark-data-synthesis unit-benchmark-data-validation

# We don't lint the src/tools content, because they are intended more as "scripts",
# rather than modules with higher quality expectations.
PYLINT_IGNORE_ARGS  += --ignore=${SRC_DIR}/tools,${SRC_DIR}/tools/langflow

# Add custom help for the application here, which will be shown when the user
# types "make help".
# When you see ${CODE}${_END} without anything between them in help messages,
# it is there to make it easier to line up multi-line description comments.

.PHONY: help-custom

help:: help-custom
help-custom::
	$(info ${help-custom-message})

define help-custom-message
${HIGHLIGHT}Quick help for this project's specific targets:${_END}

${CODE}make help-code${_END}         # Help on the make processes unique to this project.
${CODE}make help-tools${_END}        # Help on the tools and example ChatBot targets.

endef

define help-code-message
${HIGHLIGHT}Quick help for this make process on extra targets available.${_END}

For help on the targets for this project's tools and ChatBot apps, run ${CODE}make help-tools${_END}.

For help on the tools used to manage the website, run ${CODE}make help-docs${_END}.

For many targets tools, there are variables defined in this Makefile that are used to pass
arguments to the corresponding commands. Run ${CODE}make print-info-code${_END} to see the
list of these variables and their default definitions. Specific variables are mentioned for
some targets.

${CODE}make all-models-*${_END}         # Extract "*" as one of the other targets (such as, ${CODE}all-tools${CODE}),
${CODE}${_END}                          # that is everything to the right of ${CODE}all-models-${_END}, and
${CODE}${_END}                          # make that target for ALL the models defined by ${CODE}MODELS${_END}:
${CODE}${_END}                          #   ${CODE}${MODELS}${_END}
${CODE}${_END}                          # (Not useful for model-agnostic targets, like ${CODE}setup${_END}...)
${CODE}${_END}                          # You can override the list of models as follows:
${CODE}${_END}                          #   ${CODE}make MODELS="..." all-models-...${_END}
${CODE}make all-tools${_END}            # Clean outputs and run all the tools using the model defined by ${CODE}MODEL${_END}.
${CODE}make all-code${_END}             # Synonym for ${CODE}all-tools${_END}.
${CODE}make run-tools${_END}            # Run all the tools (but not the ChatBot app) without cleaning first.
${CODE}${_END}                          # Built by ${CODE}all-tools${_END}.
${CODE}make run-code${_END}             # Synonym for ${CODE}run-tools${_END}.

${CODE}make setup${_END}                # One-time setup tasks; e.g., builds target ${CODE}install-uv${_END}.
${CODE}make one-time-setup${_END}       # Synonym for ${CODE}setup${_END}.
${CODE}make install-uv${_END}           # Explain how to install ${CODE}uv${_END}.
${CODE}${_END}                          # Run ${CODE}make help-command-uv${_END} for more information.
${CODE}make install-jq${_END}           # Explain how to install ${CODE}jq${_END} (an optional CLI tool).

${CODE}make build${_END}                # Build a distribution.
${CODE}make install${_END}              # Install the code locally in development mode.

${CODE}make all-tests${_END}            # Run the unit tests (AI and non-AI) and integration tests.
${CODE}${_END}                          # Equivalent to ${CODE}unit-tests-non-ai${_END} and ${CODE}unit-tests-ai${_END}.

${CODE}make unit-tests${_END}           # Following convention, this target runs the unit tests only and, by default,
${CODE}${_END}                          # it only runs the "non-AI" unit tests by building ${CODE}unit-tests-non-ai${_END}.
${CODE}make tests${_END}                # Synonym for ${CODE}unit-tests${_END}.
${CODE}make unit-tests-non-ai${_END}    # All unit tests that don't involve inference invocations.
${CODE}${_END}                          # These all don't have the ${CODE}pytest${_END} mark ${CODE}ai${_END}, which is used to filter them.
${CODE}${_END}                          # Effectively, this target is a synonym for ${CODE}unit-tests${_END}.
${CODE}make unit-tests-ai${_END}        # All unit tests that DO involve inference invocations, which take a long time to run.
${CODE}${_END}                          # These all have the ${CODE}pytest${_END} mark ${CODE}ai${_END}, which is used to filter them.
${CODE}make unit-tests-qna${_END}       # Convenience target that runs just the AI unit tests involving QnA pairs.
${CODE}${_END}                          # These all have the ${CODE}pytest${_END} marks ${CODE}ai${_END} and  ${CODE}qna${_END} for filtering.
${CODE}make unit-tests-scenario${_END}  # Convenience target that runs just the AI unit tests involving scenario interactions.
${CODE}${_END}                          # These all have the ${CODE}pytest${_END} marks ${CODE}scenario${_END} and  ${CODE}qna${_END} for filtering.
${CODE}make unit-tests-simple${_END}    # Effectively a synonym for ${CODE}unit-tests-qna${_END}.
${CODE}make unit-tests-agent${_END}     # Effectively a synonym for ${CODE}unit-tests-scenario${_END}.

${CODE}make integration-tests${_END}    # Run the integration tests, including "dedicated" integration tests
${CODE}${_END}                          # and all unit tests with more "exhaustive" sample data flags.
${CODE}${_END}                          # (See https://the-ai-alliance.github.io/ai-application-testing/working-example/ for details)
${CODE}make integration-tests-dedicated${_END}
${CODE}${_END}                          # The "dedicated" integration tests, omitting the unit tests.

${CODE}make clean-setup${_END}          # Undoes everything done by the setup target or provides
${CODE}${_END}                          # instructions for what you must do manually in some cases.
${CODE}make uninstall-uv${_END}         # Explain how to uninstall "uv".

Several CLI tools are required, like ${CODE}uv${_END}, or only needed for a few special make targets, like ${CODE}jq${_END}:

${CODE}make help-command-uv${_END}      # Prints specific information about ${CODE}uv${_END}, including installation.
${CODE}make help-command-jq${_END}      # Prints specific information about ${CODE}jq${_END}, including installation.
${CODE}make help-command-node${_END}    # Prints specific information about ${CODE}node${_END}, including installation.

${TIP_LABEL}See also the list of common targets, like ${CODE}tests${_END} and ${CODE}lint${_END}, which are shown
${TIP_LABEL}by ${CODE}make help${_END}.
endef

define help-tools-message
${HIGHLIGHT}Quick help for this make process for the tools and ChatBot example app.${_END}

For help on the extra process targets defined in this Makefile, run ${CODE}make help-code${_END}.

For many targets tools, there are variables defined in this Makefile that are used to pass
arguments to the corresponding commands. Run ${CODE}make print-info-code${_END} to see the
list of these variables and their default definitions. Specific variables are mentioned for
some targets.

For tools run by the following targets, which invoke inference, the model
${CODE}${MODEL}${_END} is served by ollama. The make variable ${CODE}MODEL${_END} specifies the model,
so if you want to use a different model, invoke make as in this example:

  ${CODE}make MODEL=ollama_chat/llama3.2:3B run-tdd-example-refill-chatbot${_END}

Also, many targets can be used with the target "pattern" ${CODE}all-models-*${_END}.
It is described by ${CODE}make help-code${_END}.

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
${CODE}make unit-tests-langflow${_END}
${CODE}${_END}                        # Run tests for the Langflow components, which are NOT run by ${CODE}unit-tests${_END} or
${CODE}${_END}                        # ${CODE}integration-tests${_END}, so we don't force you to have Langflow installed
${CODE}${_END}                        # for this optional capability.

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
${CODE}make help-tools-all${_END}     # Prints this output and then makes the following targets:
${CODE}${_END}                        # ${CODE}help-terc${_END}, ${CODE}help-ubds${_END} and ${CODE}help-ubdv${_END}, and ${CODE}help-chatbot${_END}

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

${CODE}make help-chatbot${_END}       # Show help for the interactive ChatBot application.
${CODE}make help-mcp-server${_END}    # Show help for the ChatBot's MCP server.
${CODE}make help-api-server${_END}    # Show help for the ChatBot's OpenAI-compatible API server.
${CODE}make view-api-server-docs${_END}
${CODE}${_END}                        # Open a browser showing the API server ${CODE}docs${_END}.
${CODE}make view-api-server-redoc${_END}
${CODE}${_END}                        # Open a browser showing the API server ${CODE}redoc${_END}.

${CODE}make help-langflow-pipeline${_END}
${CODE}${_END}                        # Show help for the Langflow pipeline by passing the ${CODE}--help${_END} flag.
${CODE}make help-langflow${_END}      # Synonym for ${CODE}help-langflow-pipeline${_END}.
endef


# Help and Other Information Targets

.PHONY: help-tools-all

help-tools-all:: help-tools help-terc help-ubds help-ubdv help-chatbot

.PHONY: clean-tools clean-code

clean clean-tools:: clean-code

.PHONY: print-info-code

print-info:: print-info-code
print-info-code::
	@echo "${HIGHLIGHT}For the example code and tools:${_END}"
	@echo
	@echo "  ${DARK_GREEN}MODEL:${_END}                       ${CODE}${MODEL}${_END} (the default)"
	@echo "  ${DARK_GREEN}MODELS:${_END}                      (all of them that we explicitly list in the ${CODE}Makefile${_END})"
	@for model in ${MODELS}; do \
	 echo "  ${DARK_GREEN}${_END}                             ${CODE}$$model${_END}"; done
	@echo "  ${DARK_GREEN}ALL_TOOLS:${_END}                   ${CODE}${ALL_TOOLS}${_END}"
	@echo "  ${DARK_GREEN}INFERENCE_SERVICE:${_END}           ${CODE}${INFERENCE_SERVICE}${_END}"
	@echo "  ${DARK_GREEN}OLLAMA_PREFIX:${_END}               ${CODE}${OLLAMA_PREFIX}${_END} (ignored if not using ollama)"
	@echo "  ${DARK_GREEN}INFERENCE_URL:${_END}               ${CODE}${INFERENCE_URL}${_END}"
	@echo "  ${DARK_GREEN}TOOLS_PROMPTS_TEMPLATES_DIR:${_END} ${CODE}${TOOLS_PROMPTS_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_TEMPLATES_DIR:${_END}       ${CODE}${CHATBOT_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_TESTS_TEMPLATES_DIR:${_END} ${CODE}${CHATBOT_TESTS_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_OUTPUT_DIR:${_END}          ${CODE}${CHATBOT_OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}APP_ARGS:${_END}                    ${CODE}'${APP_ARGS}'${_END} (A user hook for passing custom arguments, like ${CODE}-h${_END})"
	@echo
	@echo "${HIGHLIGHT}The following depend on the value of MODEL (${MODEL}):${_END}"
	@echo
	@echo "  ${DARK_GREEN}OUTPUT_DIR:${_END}                  ${CODE}${OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}OUTPUT_LOGS_DIR:${_END}             ${CODE}${OUTPUT_LOGS_DIR}${_END}"
	@echo "  ${DARK_GREEN}OUTPUT_LOGS_TESTS_DIRDIR:${_END}    ${CODE}${OUTPUT_LOGS_TESTS_DIRDIR}${_END} (relative to ${CODE}SRC_DIR${_END} == ${CODE}${SRC_DIR}${_END})"
	@echo "  ${DARK_GREEN}DATA_DIR:${_END}                    ${CODE}${DATA_DIR}${_END}"
	@echo "  ${DARK_GREEN}ACCUMULATE_TEST_ERRORS:${_END}      ${CODE}${ACCUMULATE_TEST_ERRORS}${_END} (For tests, run all examples, then report errors. Set to ${CODE}''${_END} for ${CODE}False${_END})"
	@echo


${OUTPUT_DIR} ${OUTPUT_TESTS_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${OUTPUT_LOGS_TESTS_DIRDIR} ${DATA_DIR} ${CHATBOT_DATA_DIR}::
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
	uv run ${SRC_DIR}/tools/${@:help-%=%}.py --help
	@echo

# LITELLM_LOG=ERROR turns off some annoying INFO messages, sufficient
# for our purposes. See the LiteLLM docs for logging configuration details.
# Define APP_ARGS on the command line to pass custom arguments, e.g.,
#   make APP_ARGS='--help' run-tdd-example-refill-chatbot
# just prints help.

run-tdd-example-refill-chatbot:: before-run run-tdd-example-refill-chatbot-preamble
	export LITELLM_LOG=ERROR; \
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/${@:run-%=%}.py \
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
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/${@:run-%=%}.py \
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
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/${@:run-%=%}.py \
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
.PHONY: unit-tests-langflow

run-langflow-pipeline:: langflow-pipeline
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

help-lf help-langflow help-langflow-pipeline::
	@echo "${INFO_LABEL}Help on the Langflow unit benchmark pipeline:"
	${NOOP} ${TIME} uv run ${SRC_DIR}/tools/langflow/unit_benchmark_flow.py --help
	@echo

unit-tests-langflow:: run-command-checks
	@echo "${INFO_LABEL} Running the langflow unit tests..."
	${MAKE} WHICH_TESTS=${SRC_DIR}/tests/unit/langflow unit-tests

.PHONY: run-chatbot chatbot before-chatbot before-chatbot-preamble check-model-which-chatbot do-run-chatbot agent-chatbot simple-chatbot after-chatbot

run-chatbot:: chatbot
chatbot:: before-chatbot do-run-chatbot after-chatbot
do-run-chatbot::
	export LITELLM_LOG=ERROR; \
	${NOOP} ${TIME} uv run python ${SRC_DIR}/apps/chatbot/main.py \
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
	@echo "${INFO_LABEL}Help on the ${CODE}${WHICH_CHATBOT}${_END} ChatBot:"
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/main.py --help

before-chatbot:: before-chatbot-preamble check-model-which-chatbot run-command-checks ${OUTPUT_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${CHATBOT_DATA_DIR}
check-model-which-chatbot::
	@if [[ ! ${MODEL} = ${OLLAMA_PREFIX}gpt-oss ]] || [[ ! ${WHICH_CHATBOT} = agent ]]; then exit 0; else \
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
	${NOOP} ${INSPECTOR} uv run python ${SRC_DIR}/apps/chatbot/mcp_server/server.py \
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
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/mcp_server/server.py --help

.PHONY: api-server run-api-server help-api-server check-api-server
.PHONY: view-api-server-docs view-api-server-redoc view-api-server-docs-preamble

run-api-server:: api-server
api-server:: before-chatbot
	@echo "${INFO_LABEL}Running the ChatBot OpenAI-compatible API Server..."
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	${NOOP} ${TIME} uv run python ${SRC_DIR}/apps/chatbot/api_server/server.py \
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
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/api_server/server.py --help

check-api-server::
	@echo "${INFO_LABEL}'Sanity check' that the OpenAI-compatible API server works:"
	@echo "${INFO_LABEL}Running the server in the background..."
	${NOOP} ${MAKE} api-server &
	@echo
	@echo "  ${HIGHLIGHT}Hit the 'return' key!${_END}"
	@echo
	@echo "${INFO_LABEL}Running ${CODE}apps/chatbot//api_server/example_client.py${_END} ..."
	@echo
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/api_server/example_client.py
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

# Because the full unit-tests suite is too costly to run for PRs, we use a
# special-purpose definition of "before-pr-default".

before-pr-default: before-pr-no-tests unit-tests-non-ai

.PHONY: all-tests note-all-tests unit-tests-non-ai
.PHONY: unit-tests-ai unit-tests-ai-scenario unit-tests-ai-qna  unit-tests-ai-agent unit-tests-ai-simple
.PHONY: integ-tests integration-tests integration-tests-dedicated unit-tests-as-integration-tests

all-tests:: note-all-tests unit-tests-non-ai integration-tests
note-all-tests::
	@echo "${NOTE_LABEL}The ${CODE}all-tests${_END} target does ${BOLD}${RED}NOT${_END} run the AI-related unit tests!"
	@echo "${NOTE_LABEL}"
	@echo "${NOTE_LABEL}The integration tests are a strict superset of the unit tests, they run"
	@echo "${NOTE_LABEL}the same suite, but with all Q&A examples sampled, etc., plus some other"
	@echo "${NOTE_LABEL}integration tests. We do this so we don't run those (expensive) tests 'twice'."
	@echo

# This is effectively an alias for the default behavior of unit-tests!
unit-tests-non-ai:: unit-tests

.PHONY: unit-tests-appointments

unit-tests-ai:: unit-tests-ai-qna unit-tests-ai-scenario

unit-tests-scenario unit-tests-agent::
	@echo "${INFO_LABEL}Running the 'scenario' use case unit tests with the 'agent' ChatBot."
	@${MAKE} \
		PYTEST_RUN_OPT_ARGS="-m 'ai and scenario'" \
	  WHICH_CHATBOT=agent \
		do-unit-tests-ai

unit-tests-qna unit-tests-simple::
	@echo "${INFO_LABEL}Running the 'QnA' use case unit tests with the 'simple' ChatBot."
	@${MAKE} \
		PYTEST_RUN_OPT_ARGS="-m 'ai and qna'" \
	  WHICH_CHATBOT=simple \
		do-unit-tests-ai

# We capture the success or failure status of the "uv" command, post-process the
# JSONL log files, then exit with the same status.
# We pass TIMESTAMP explicitly, because we don't want it to change from one step to
# the next!
do-unit-tests-ai:: ${OUTPUT_TESTS_DIR} ${OUTPUT_LOGS_TESTS_DIRDIR}
	@echo "${INFO_LABEL}Using the pytest filter \"${PYTEST_RUN_OPT_ARGS}\"."
	@echo "${INFO_LABEL}Special log files: ${CODE}${OUTPUT_LOGS_TESTS_DIRFILE_GLOB}${_END}"
	${NOOP} ${MAKE} \
		TIMESTAMP=${TIMESTAMP} \
		PYTEST_RUN_OPT_ARGS="${PYTEST_RUN_OPT_ARGS}" \
	  WHICH_CHATBOT=${WHICH_CHATBOT} \
		unit-tests; \
		success=$$?; \
	  ${MAKE} TIMESTAMP=${TIMESTAMP} post-proc-test-logs; \
	  exit $$success

.PHONY: post-proc-test-logs show-test-logs

post-proc-test-logs::
	@command -v jq > /dev/null; \
	if [ $$? -ne 0 ]; \
		then echo "CLI tool ${CODE}jq${_END} not found, so we won't convert output JSONL files to JSON..."; \
		else echo "Converting JSONL log files to JSON..."; \
			for f in ${OUTPUT_LOGS_TESTS_DIRDIR}/*.jsonl; \
				do ff=$${f%l}; \
				if [ ! -f $$ff ]; \
					then echo "${INFO_LABEL}Generating ${CODE}$$ff${_END} from ${CODE}$$f${_END}:"; \
		  		jq . $$f > $$ff; \
		  	fi; \
			done; \
	fi
	@echo "${INFO_LABEL}Contents of ${CODE}${OUTPUT_LOGS_TESTS_DIRDIR}/*.json*:${_END}"
	@ls -l ${OUTPUT_LOGS_TESTS_DIRDIR}/*.json*
	@echo
	@echo "${INFO_LABEL}See in particular your time-stamped JSON log files:"
	@echo "  ${CODE}${OUTPUT_LOGS_TESTS_DIRFILE_GLOB}${_END}"
	@echo "${INFO_LABEL}(They may be empty!)"

integ-tests integration-tests:: integration-tests-dedicated integration-tests-from-unit-tests

# This target runs all the unit-tests, the AI-related, but more exhaustively, as well as the non-AI unit tests.
integration-tests-from-unit-tests:: run-command-checks
	@echo "${INFO_LABEL}Running the unit tests as integration tests with 100% sampling and trying all test query examples."
	@echo "${INFO_LABEL}Uses the agent ChatBot."
	${MAKE} \
		WHICH_CHATBOT=simple \
		DATA_SAMPLE_RATE=${INTEGRATION_TESTS_DATA_SAMPLE_RATE} \
		unit-tests

# Uses the simple ChatBot for now!
integration-tests-dedicated:: run-command-checks
	@echo "${INFO_LABEL}Running the 'dedicated' integration tests..."
	${MAKE} \
	  PYTEST_RUN_OPT_ARGS= \
		WHICH_CHATBOT=simple \
		WHICH_TESTS=${TESTS_INTEGRATION_DIR} \
		unit-tests

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
include .llm.mk
