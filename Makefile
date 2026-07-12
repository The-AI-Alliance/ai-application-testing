# Makefile for the ai-application-testing website and repo example code.

# Common includes. See the end of this file, too!
include .common.mk

# A hook for passing arguments to the programs, e.g., "make APP_ARGS=--help ..."
APP_ARGS              ?=

# Definitions for the tools and applications.
# Setting the USE_CASES to '' results in all of them being processed.
# Invoke "make JUST_STATS=--just-stats ..." to have stats generated, not validation, too.
INFERENCE_SERVICE     ?= ollama
PORT                  ?= 11434
INFERENCE_URL         ?= http://localhost:${PORT}
USE_CASES             ?= 
JUST_STATS            ?=

# Different models we have used. See the "all-models-*" targets:
ollama_prefix          = ollama_chat
MODEL_GPT_OSS         ?= ${ollama_prefix}/gpt-oss:20b
MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:12b
# MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:26b
# MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:31b
# MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:e4b
MODEL_QWEN35          ?= ${ollama_prefix}/qwen3.5:35b
MODEL_LLAMA32         ?= ${ollama_prefix}/llama3.2:3B
MODEL_SMOLLM2         ?= ${ollama_prefix}/smollm2:1.7b-instruct-fp16
MODEL_GRANITE4        ?= ${ollama_prefix}/granite4:latest
MODELS                ?= ${MODEL_GPT_OSS} ${MODEL_GEMMA4} ${MODEL_QWEN35} ${MODEL_LLAMA32} ${MODEL_SMOLLM2} ${MODEL_GRANITE4} 
# Default model!
MODEL                 ?= ${MODEL_GEMMA4}

MODEL_FILE_NAME       ?= $(subst :,_,${MODEL})

# Overrides definition in .common.mk:
OUTPUT_DIR            := ${PWD}/output/${MODEL_FILE_NAME}
# DATA_DIR: Where the tools write and later read data.
# TEST_DATA_DIR: Where test data is read. RELATIVE to ${SRC_DIR}.
DATA_DIR              := ${OUTPUT_DIR}/data
TEST_DATA_DIR         := ${TESTS_DIR}/data
OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui

# Some specific variables passed as env. vars. to the ChatBot.
# CONFIDENCE_THRESHOLD: What's the minimum confidence (out of 1.0, meaning 100%) for a response that we trust it?
# WHICH_CHATBOT: Which ChatBot implementation to use: 'agent' for ChatBotAgent or 'simple' for ChatBotSimple
CONFIDENCE_THRESHOLD        ?= 0.9
WHICH_CHATBOT               ?= agent

# Some specific variables passed as env. vars. to the test suites.
# ACCUMULATE_TEST_ERRORS:   Should I run ALL prompts, then report accumulated errors? Leave EMPTY for False, non-empty for True!
# RATING_THRESHOLD:         What's the minimum rating (out of 5) for which a test prompt is "good enough" for the particular use case?
# TESTS_LOGS_DIR:           Where special AI test logs are written. RELATIVE TO ${SRC_DIR}!
# TESTS_LOGS_FILE_TEMPLATE: A file name pattern, where "{class_name}" will be replaced with the test class name.
# TESTS_LOGS_FILE_GLOB:     Just used for messages printed by targets.
ACCUMULATE_TEST_ERRORS      ?= True
RATING_THRESHOLD            ?= 4
TESTS_LOGS_DIR              ?= tests/logs/${MODEL_FILE_NAME}
TESTS_LOGS_FILE_TEMPLATE    ?= ${TESTS_LOGS_DIR}/{which_chatbot}-{class_name}-${TIMESTAMP}.jsonl
TESTS_LOGS_FILE_GLOB        ?= ${TESTS_LOGS_DIR}/*-${TIMESTAMP}.jsonl

# Sampling rates for different kinds of tests.
UNIT_TEST_DATA_SAMPLE_RATE        ?= 0.25
INTEGRATION_TEST_DATA_SAMPLE_RATE ?= 1.0
DATA_SAMPLE_RATE                  ?= ${UNIT_TEST_DATA_SAMPLE_RATE}

# These directories will be relative to where the tools and apps are executed.
TOOLS_PROMPTS_TEMPLATES_DIR ?= tools/prompts/templates
CHATBOT_TEMPLATES_DIR       ?= apps/chatbot/prompts/templates
CHATBOT_TEST_TEMPLATES_DIR  ?= tests/prompts/templates
CHATBOT_DATA_DIR            ?= ${DATA_DIR}/chatbot
CHATBOT_OUTPUT_DIR          ?= ${PWD}/output
CHATBOT_API_SERVER_HOST     ?= localhost
CHATBOT_API_SERVER_PORT     ?= 8000
CHATBOT_API_SERVER          ?= ${CHATBOT_API_SERVER_HOST}:${CHATBOT_API_SERVER_PORT}

ALL_TOOLS                   ?= tdd-example-refill-chatbot unit-benchmark-data-synthesis unit-benchmark-data-validation


# When you see ${CODE}${_END} without anything between them, it is there 
# to make it easier to line up multi-line description comments.

help:: help-quick
help-quick::
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

${CODE}make help-code${_END}          # Prints this output.
${CODE}make help-code-all${_END}      # Prints this output and makes ${CODE}help-terc${_END}, ${CODE}help-ubds${_END} and ${CODE}help-ubdv${_END}.

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

.PHONY: help-code-all

help-code-all:: help-code help-terc help-ubds help-ubdv

.PHONY: clean-tools clean-code

clean clean-code:: clean-tools

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
	@echo "  ${DARK_GREEN}CHATBOT_TEST_TEMPLATES_DIR:${_END}  ${CODE}${CHATBOT_TEST_TEMPLATES_DIR}${_END}"
	@echo "  ${DARK_GREEN}CHATBOT_OUTPUT_DIR:${_END}          ${CODE}${CHATBOT_OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}APP_ARGS:${_END}                    ${CODE}'${APP_ARGS}'${_END} (A user hook for passing custom arguments, like ${CODE}-h${_END})"
	@echo
	@echo "${HIGHLIGHT}The following depend on the value of MODEL (${MODEL}):${_END}"
	@echo
	@echo "  ${DARK_GREEN}OUTPUT_DIR:${_END}                  ${CODE}${OUTPUT_DIR}${_END}"
	@echo "  ${DARK_GREEN}OUTPUT_LOGS_DIR:${_END}             ${CODE}${OUTPUT_LOGS_DIR}${_END}"
	@echo "  ${DARK_GREEN}TESTS_LOGS_DIR:${_END}              ${CODE}${TESTS_LOGS_DIR}${_END} (relative to ${CODE}SRC_DIR${_END} == ${CODE}${SRC_DIR}${_END})"
	@echo "  ${DARK_GREEN}DATA_DIR:${_END}                    ${CODE}${DATA_DIR}${_END}"
	@echo "  ${DARK_GREEN}ACCUMULATE_TEST_ERRORS:${_END}      ${CODE}${ACCUMULATE_TEST_ERRORS}${_END} (For tests, run all examples, then report errors. Set to ${CODE}''${_END} for ${CODE}False${_END})"
	@echo

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
	echo "${INFO} Making target \"$$target\" for all models:${_END} ${MODELS}"; \
	for model in ${MODELS}; \
	do \
		echo && echo "${INFO} Model = $$model${_END}" && \
		echo "${INFO} ${MAKE} ${MAKEFLAGS} TIMESTAMP=${TIMESTAMP} MODEL=$$model $$target${_END}"; \
		echo ${MAKE} MODEL="$$model" $$target; \
	done; \
	echo "\n${NOTE} Output log files (if any) can be found under:${_END}"; \
	for model in ${MODELS}; \
	do \
		echo "  ${HIGHLIGHT}output/$$model/logs/${TIMESTAMP}${_END}"; \
	done

all-tools all-code:: run-tools
run-tools run-code:: 
	${MAKE} TIMESTAMP=${TIMESTAMP} ${ALL_TOOLS:%=run-%} 

clean-tools:: clean-code

terc run-terc:: run-tdd-example-refill-chatbot
ubds run-ubds:: run-unit-benchmark-data-synthesis
ubdv run-ubdv:: run-unit-benchmark-data-validation

help-terc:: help-tdd-example-refill-chatbot
help-ubds:: help-unit-benchmark-data-synthesis
help-ubdv:: help-unit-benchmark-data-validation

${ALL_TOOLS:%=help-%}::
	@echo "${GREEN}Help on ${@help-%=%}.py:${_END}"
	@echo
	cd ${SRC_DIR} && uv run tools/${@:help-%=%}.py --help
	@echo

# LITELLM_LOG=ERROR turns off some annoying INFO messages, sufficient
# for our purposes. See the LiteLLM docs for logging configuration details.
# Define APP_ARGS on the command line to pass custom arguments, e.g., 
#   make APP_ARGS='--help' run-tdd-example-refill-chatbot
# just prints help.

run-tdd-example-refill-chatbot:: before-run
	@echo "${INFO} *** Running the TDD example.${_END}"
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-synthesis:: before-run
	@echo "${INFO} *** Running the unit benchmark data synthesis example.${_END}"
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--use-cases ${USE_CASES} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-validation:: before-run
	@echo "${INFO} *** Running the unit benchmark synthetic data validation example. ${_END}"
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-cases ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
	  ${JUST_STATS} ${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

before-run:: silent-before-run
	@echo "${ORANGE} If errors occur, try ${HIGHLIGHT}make setup${ORANGE} or ${HIGHLIGHT}make clean-setup setup${ORANGE}, then try again.${_END}"

silent-before-run:run-command-checks ${OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${DATA_DIR}  
run-command-checks:: command-check-uv provider-server-check

provider-server-check::
	@[[ ${INFERENCE_SERVICE} != 'ollama' ]] || ollama ps > /dev/null || ! echo "${ERROR} Ollama is not running!${_END}" || exit 1

# Langflow targets
.PHONY: run-langflow-pipeline langflow-pipeline help-langflow-pipeline  
.PHONY: unit-tests-langflow all-tests-langflow

run-langflow-pipeline:: langflow-pipeline
langflow-pipeline:: 
	@echo "${INFO} Running the Langflow unit benchmark pipeline (synthesis + validation)...${_END}"
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run python -m tools.langflow.unit_benchmark_flow \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${TOOLS_PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-case ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/$@.log \
	  ${JUST_STATS} ${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

help-lf help-langflow help-langflow-pipeline::
	@echo "${INFO} Help on the Langflow unit benchmark pipeline:${_END}"
	@echo
	cd ${SRC_DIR} && uv run python -m tools.langflow.unit_benchmark_flow --help
	@echo

all-tests-langflow unit-tests-langflow:: run-command-checks
	@echo "${INFO} Running the langflow unit tests...${_END}"
	cd ${SRC_DIR} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export DATA_DIR=${DATA_DIR} && \
	  uv run python -m unittest discover \
	    --start-directory tests/unit/langflow \
	    --top-level-directory . || ${MAKE} STATUS=$$? MSG="$@ failed" error 

.PHONY: run-chatbot chatbot do-run-chatbot agent-chatbot simple-chatbot before-chatbot after-chatbot

run-chatbot:: chatbot
chatbot:: before-chatbot do-run-chatbot after-chatbot
do-run-chatbot::
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && uv run python -m apps.chatbot.main \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${CHATBOT_TEMPLATES_DIR} \
		--data-dir ${CHATBOT_DATA_DIR} \
		--output-dir ${CHATBOT_OUTPUT_DIR} \
		--confidence-threshold ${CONFIDENCE_THRESHOLD} \
		--which-chatbot ${WHICH_CHATBOT} \
		--log-file ${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log \
		--verbose ${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 

agent-chatbot simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:%-chatbot=%} chatbot

.PHONY: help-chatbot help-agent-chatbot help-simple-chatbot 

help-agent-chatbot help-simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:help-%-chatbot=%} help-chatbot

help-chatbot::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.main --help

before-chatbot:: run-command-checks ${OUTPUT_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${CHATBOT_DATA_DIR}
	@echo "${INFO} Running the \"${WHICH_CHATBOT}\" ChatBot...${_END}" && \
	echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}\n" && \
		[[ ${MODEL} =~ gpt-oss ]] && [[ ${WHICH_CHATBOT} = agent ]] && \
		echo "${ERROR} ${MODEL} currently can't be used with the \"${WHICH_CHATBOT}\" ChatBot!${_END}" && \
    echo " (https://github.com/langchain-ai/langchain/issues/33116). Try using model ${CODE}${MODEL_GEMMA4}${_END}." && \
    exit 1 || \
		echo ""

after-chatbot::
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}\n"

.PHONY: mcp-server run-mcp-server help-mcp-server check-mcp-server inspect-mcp-server

# See inspect-mcp-server for information about ${INSPECTOR}, which is otherwise
# blank.
run-mcp-server:: mcp-server
mcp-server:: before-chatbot
	@echo "${INFO} Running the ChatBot MCP Server...${_END}"
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
		${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

inspect-mcp-server:: command-check-node
	@echo "${INFO} Running the @modelcontextprotocol/inspector with the ChatBot MCP Server...${_END}"
	${MAKE} INSPECTOR="npx @modelcontextprotocol/inspector" mcp-server

help-mcp-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.mcp_server.server --help

.PHONY: api-server run-api-server help-api-server check-api-server view-api-server-docs view-api-server-redoc

run-api-server:: api-server
api-server:: before-chatbot
	@echo "${INFO} Running the ChatBot OpenAI-compatible API Server...${_END}"
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"
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
		${APP_ARGS} || ${MAKE} STATUS=$$? MSG="$@ failed" error 
	@echo "\n${INFO} Log output:${_END}\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

help-api-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.api_server.server --help

check-api-server::
	@echo "${INFO} 'Sanity check' that the OpenAI-compatible API server works:${_END}"
	@echo "Running the server in the background..."
	${MAKE} api-server & 
	@echo
	@echo "  ${HIGHLIGHT}Hit the 'return' key!${_END}"
	@echo
	@echo "  ${HIGHLIGHT}Running 'apps/chatbot//api_server/example_client.py'...${_END}"
	cd ${SRC_DIR} && uv run python apps/chatbot/api_server/example_client.py
	@echo "  ${TIP} Hack: Find the process id for the server and kill it...${_END}" 
	kill %1

view-api-server-docs view-api-server-redoc::
	@echo
	@echo "${INFO} Opening ${HIGHLIGHT}http://${CHATBOT_API_SERVER}/${@:view-api-server-%=%}${_END}"
	@echo
	@echo "${open-url-message}"
	@echo
	@echo "${WARNING} If the URL isn't found, make sure the server is running! For example,"
	@echo "run ${HIGHLIGHT}make api-server${ORANGE} in another terminal window, then rerun this target.${_END}" 
	@uv run python -m webbrowser "http://${CHATBOT_API_SERVER}/${@:view-api-server-%=%}"

.PHONY: run-open-webui open-webui open-webui-preamble open-webui-setup help-open-webui remove-open-webui

run-open-webui open-webui:: open-webui-preamble open-webui-setup
	cd ${OPEN_WEBUI_DIR} && \
		DATA_DIR=${CHATBOT_DATA_DIR} uv tool run --with greenlet open-webui serve \
		 || ${MAKE} STATUS=$$? MSG="$@ failed" error 

open-webui-preamble::
	@echo "${INFO}Running Open WebUI (https://docs.openwebui.com/getting-started/) out of directory ${OPEN_WEBUI_DIR}.${_END}"
	@echo "${INFO}Make sure the OpenAI-compatible API Server is running first, i.e., make api-server in another terminal!${_END}"
	@echo "\nOpen ${RED}http://localhost:8080${_END} when it is up (it takes a few minutes)."
	@echo "${open-url-message}"

open-webui-setup::
	@test -d ${OPEN_WEBUI_DIR}/.venv || (\
		echo "${INFO} Setting up Open WebUI in the ${HIGHLIGHT}${OPEN_WEBUI_DIR}${DARK_GREEN} directory.${_END}" && \
		cd ${OPEN_WEBUI_DIR} && uv venv && uv sync && uv tool install open-webui)
	cd ${OPEN_WEBUI_DIR} && . .venv/bin/activate

help-open-webui:: 
	DATA_DIR=${CHATBOT_DATA_DIR} uvx --python 3.13 --with greenlet open-webui@latest serve --help

remove-open-webui::
	uv tool uninstall open-webui
	rm -rf $HOME/.open-webui

${OUTPUT_DIR} ${OUTPUT_TEST_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${SRC_DIR}/${TESTS_LOGS_DIR} ${DATA_DIR} ${CHATBOT_DATA_DIR}::
	mkdir -p $@

.PHONY: all-tests note-all-tests test tests unit-tests unit-tests-non-ai 
.PHONY: unit-tests-ai unit-tests-ai-agent unit-tests-ai-simple
.PHONY: integ-tests integration-tests integration-tests-dedicated unit-tests-as-integration-tests

all-tests:: note-all-tests unit-tests-non-ai integration-tests
note-all-tests::
	@echo "${NOTE} The 'all-tests' target does NOT run the AI-related unit tests!${_END}"
	@echo 
	@echo "The integration tests are a strict superset of the unit tests, they run"
	@echo "the same suite, but with all Q&A examples sampled, etc., plus some other"
	@echo "integration tests. Hence, we don't run those tests 'twice'."
	@echo

test tests unit-tests:: run-command-checks unit-tests-non-ai unit-tests-ai unit-tests-appointments

# The --pattern argument is unnecessary here, as we pass the default value, but it is
# included for "symmetry" with the unit-tests-ai target.
unit-tests-non-ai::
	@echo "${INFO} Running the non-AI unit tests...${_END}"
	cd ${SRC_DIR} && \
	  uv run python -m unittest discover \
	    --pattern 'test*.py' \
	    --start-directory tests/unit \
	    --top-level-directory . || ${MAKE} STATUS=$$? MSG="$@ failed" error 

.PHONY: unit-tests-appointments

unit-tests-appointments::
	@echo "${INFO} Running the appointment tool unit tests...${_END}"
	cd ${SRC_DIR} && \
	  uv run python -m unittest discover \
	    --pattern 'test_appointment*.py' \
	    --start-directory tests/unit/apps/chatbot \
	    --top-level-directory . || ${MAKE} STATUS=$$? MSG="$@ failed" error 

unit-tests-ai:: unit-tests-ai-agent unit-tests-ai-simple

# The "funky" ending command line, "uv run ... && make ... || ! make ...", is a hack
# to make the "show-test-logs" target whether or not the tests pass, and also
# effectively return success (==0) or failure (!=0) status from the tests.
# (Note we are in the src directory so we have to tell make to go to the parent...)
unit-tests-ai-agent unit-tests-ai-simple:: ${OUTPUT_TEST_DIR} ${SRC_DIR}/${TESTS_LOGS_DIR} 
	@echo "${INFO} Running the AI unit tests with the \"${@:unit-tests-ai-%=%}\" ChatBot...${_END}"
	@echo "${INFO} AI test log files:${_END}"
	@echo "  ${HIGHLIGHT}${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
    export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
    export CHATBOT_TEST_TEMPLATES_DIR=${CHATBOT_TEST_TEMPLATES_DIR} && \
	  export DATA_DIR=${TEST_DATA_DIR} && \
	  export TESTS_LOGS_FILE_TEMPLATE=${TESTS_LOGS_FILE_TEMPLATE} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export WHICH_CHATBOT=${@:unit-tests-ai-%=%} && \
	  export VERBOSE='True' && \
	  ${TIME} uv run python -m unittest discover \
	  	--pattern 'ai_test*.py' \
	  	--start-directory tests/unit \
	  	--top-level-directory . ${APP_ARGS} && \
	      ${MAKE} TESTS_LOGS_FILE_GLOB=${TESTS_LOGS_FILE_GLOB} --directory .. post-proc-test-logs || \
	    ! ${MAKE} TESTS_LOGS_FILE_GLOB=${TESTS_LOGS_FILE_GLOB} --directory .. post-proc-test-logs


# A special target for running one of the AI tests. Invoke as follows:
# make TEST=tests/.../ai_test_foo.py WHICH_CHATBOT=agent|simple one-test-ai
# Note that src is considered the root directory for TEST.

one-test-ai:: ${SRC_DIR}/${TESTS_LOGS_DIR}
	@echo "${INFO} Running one AI unit test: TEST = ${TEST} ...${_END}"
	@echo "${TIP} Use ${HIGHLIGHT}make list-unit-tests-ai to see the list of tests.${_END}"
	@echo
	@echo "${INFO} AI test log files:${_END}"
	@echo "  ${HIGHLIGHT}${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
    export CHATBOT_TEST_TEMPLATES_DIR=${CHATBOT_TEST_TEMPLATES_DIR} && \
	  export DATA_DIR=${TEST_DATA_DIR} && \
	  export TESTS_LOGS_FILE_TEMPLATE=${TESTS_LOGS_FILE_TEMPLATE} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export WHICH_CHATBOT=${WHICH_CHATBOT} && \
	  export VERBOSE='True' && \
	  ${TIME} uv run python -m unittest ${TEST} && \
	      ${MAKE} TESTS_LOGS_FILE_GLOB=${TESTS_LOGS_FILE_GLOB} --directory .. post-proc-test-logs || \
	    ! ${MAKE} TESTS_LOGS_FILE_GLOB=${TESTS_LOGS_FILE_GLOB} --directory .. post-proc-test-logs

.PHONY: list-unit-tests-ai
list-unit-tests-ai::
	cd ${SRC_DIR} && find . -name 'ai_test*.py'

.PHONY: post-proc-test-logs show-test-logs

post-proc-test-logs:: 
	@echo
	@echo "${INFO} Time-stamped JSONL log files were written to:${_END}"
	@echo "  ${HIGHLIGHT}${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${_END}"
	@echo "${INFO} (They may be empty!)${_END}"
	@echo "${INFO} The corresponding '*.json' files (if any) were generated${_END}"
	@echo "${INFO} using 'jq' and target 'nice-ai-test-logs'. They are easier to read.${_END}"
	@echo
	@echo ${MAKE} nice-ai-test-logs || ${MAKE} show-test-logs

show-test-logs::
	@ls -l ${SRC_DIR}/${TESTS_LOGS_DIR}/*.json*
	@echo
	@echo "${TIP} Run 'make nice-ai-test-logs' to make a nicely-formatted JSON file${_END}"
	@echo "${TIP} from each JSONL file. (The 'jq' CLI tool required).${_END}"
	@echo 

.PHONY: nice-ai-test-logs

# This target nicely formats the AI-related test logs into more readable JSON. Requires jq
nice-ai-test-logs:: silent-command-check-jq 
	@for f in ${SRC_DIR}/${TESTS_LOGS_DIR}/*.jsonl; do ff=$${f%l}; [[ -f $$ff  ]] || \
	  echo "${INFO} Writing $$ff:${_END}"; \
	  jq . $$f > $$ff; \
	done
	@echo "${HIGHLIGHT}"
	@ls -l ${SRC_DIR}/${TESTS_LOGS_DIR}/*.json*
	@echo "${_END}"

integ-tests integration-tests:: integration-tests-dedicated integration-tests-from-unit-tests

# This target runs all the unit-tests, the AI-related, but more exhaustively, as well as the non-AI unit tests.
integration-tests-from-unit-tests:: run-command-checks
	@echo "${INFO} Running the unit tests as integration tests with 100% sampling and trying all test query examples...${_END}"
	${MAKE} DATA_SAMPLE_RATE=${INTEGRATION_TEST_DATA_SAMPLE_RATE} tests

integration-tests-dedicated:: run-command-checks
	@echo "${INFO} Running the 'dedicated' integration tests...${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${INTEGRATION_TEST_DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export TOOLS_PROMPTS_TEMPLATES_DIR=${TOOLS_PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
	  export DATA_DIR=${TEST_DATA_DIR} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export VERBOSE='True' && \
	  uv run python -m unittest discover \
	  	--start-directory tests/integration \
	  	--top-level-directory . || ${MAKE} STATUS=$$? MSG="$@ failed" error 

.PHONY: before-pr format-lint-type-check flt
before-pr:: format-lint-type-check tests
format-lint-type-check flt:: format lint type-check

.PHONY: format lint ruff pylint type-check type-check-watch

format::
	@echo "${INFO} $@: Running 'black' on the code.${_END}"
	uv run black ${SRC_DIR}

lint:: ruff pylint

ruff::
	@echo "${INFO} $@: Running 'ruff' to lint the code.${_END}"
	uv run ruff check --fix ${SRC_DIR}

# We don't lint the src/tools content, because they are intended more as "scripts",
# rather than modules with higher quality expectations.
pylint2:: 
	@echo "${INFO} $@: Running 'pylint' on the code.${_END} (configuration in pylintrc.toml)"
	uv run pylint --ignore=${SRC_DIR}/tools,${SRC_DIR}/tools/langflow ${SRC_DIR}
pylint::
	@echo "${INFO} $@: Not currently running 'pylint' on the code due to excessive 'noise'.${_END}"

type-check::
	@echo "${INFO} Running 'ty' on the code.${_END}"
	uv run ty check ${SRC_DIR} 
type-check-watch::
	@echo "${INFO} Running 'ty' on the code in 'watch' mode.${_END}"
	uv run ty check --watch ${SRC_DIR} 


# The next section of this Makefile includes some convenience targets for working 
# with the "llm" CLI tool. It is NOT required to install and use this tool.
# See the Appendix in the README.md for details.

define help_message_llm

The "llm" CLI is used by many of the tools here. For more details, see:
  ${GREEN}https://github.com/simonw/llm${_END}

You can install llm using pip:
  ${GREEN}pip install -U llm bs4${_END}
or if you use uv:
  ${GREEN}uv add -U llm bs4${_END}

To remove llm, use the corresponding commands, one of:
  ${GREEN}pip uninstall llm bs4${_END}
  ${GREEN}uv remove llm bs4${_END}

If you want to serve models locally using "ollama", see the installation 
instructions:
  ${GREEN}https://ollama.com${_END}

Then install the llm plugin for ollama:
  ${GREEN}llm install llm-ollama${_END}

The tools also use several llm "templates". These need to be installed into
the directory output by this llm command:
  ${GREEN}llm templates path${_END}

Use the following make command to do this automatically:
  ${GREEN}make install-llm-templates${_END}

${WARNING} If you edit the templates in ${HIGHLIGHT}${TOOLS_PROMPTS_TEMPLATES_DIR}${ORANGE}, rerun  
  ${GREEN}make install-llm-templates${_END}

(llm is required to run this target, because it uses 'llm templates path'
to determine the installation location.)

So, to summarize the llm-related targets (and mention the rest of them):
 
${GREEN}make help-llm${_END}               # This information!
${GREEN}make install-llm${_END}            # Instructions for installing llm.
${GREEN}make install-llm-templates${_END}  # Install our llm "templates" into llm.
${GREEN}make clean-llm${_END}              # Instructions for uninstalling llm. Also makes clean-llm-templates.
${GREEN}make clean-llm-templates${_END}    # Remove our llm "templates" from the llm installation location.

endef

.PHONY: help-llm clean-llm clean-llm-templates install-llm

help-llm::
	$(info ${help_message_llm})
	@echo

clean-llm:: help-llm clean-llm-templates
	@echo
	@echo "${NOTE} ${GREEN}make clean-llm-templates${BLUE} was already executed to uninstall our templates.${_END}"
	@echo

clean-llm-templates::
	@cd ${TOOLS_PROMPTS_TEMPLATES_DIR} && \
		llmdir="$$(llm templates path)" && \
		for t in *.yaml; do \
			echo "${INFO} removing: ${HIGHLIGHT}$$llmdir/$$t${_END}"; \
			rm -f "$$llmdir/$$t"; \
		done && \
		ls -l "$$llmdir"

install-llm:: help-llm install-llm-templates
	@echo
	@echo "${NOTE} ${GREEN}make install-llm-templates${BLUE} was already executed to install our templates.${_END}"
	@echo

install-llm-templates:: command-check-llm
	@llmdir="$$(llm templates path)" && \
	echo "${INFO} Installing the llm templates from ${HIGHLIGHT}${TOOLS_PROMPTS_TEMPLATES_DIR}${GREEN} into ${HIGHLIGHT}$$llmdir${GREEN} ...${_END}" && \
	cp ${TOOLS_PROMPTS_TEMPLATES_DIR}/*.yaml "$$llmdir" && \
	ls -l "$$llmdir"


.PHONY: build install

build::
	@echo "${INFO} Building a distribution...${_END}"
	rm -rf dist
	uv build
	@echo "${INFO} Contents of 'dist': ${_END}"
	@ls -l dist

install::
	@echo "${INFO} Installing the code locally in development mode...${_END}"
	uv sync

# Common includes. See the beginning of this file, too!
# The reason the following are put at the end, rather than the beginning, is to 
# control the ordering of dependencies for "global" targets, like "help".
include .website.mk
