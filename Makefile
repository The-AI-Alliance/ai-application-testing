# Makefile for the ai-application-testing website and repo example code.

# Some Environment variables
MAKEFLAGS              = --warn-undefined-variables
MAKEFLAGS_RECURSIVE   ?= # --print-directory (only useful for recursive makes...)
UNAME                 ?= $(shell uname)
ARCHITECTURE          ?= $(shell uname -m)
TIMESTAMP             ?= $(shell date +"%Y%m%d-%H%M%S")
## Used for version tagging release artifacts.
GIT_HASH              ?= $(shell git show --pretty="%H" --abbrev-commit |head -1)

# Time execution
TIME                  ?= time  # time execution of long processes

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
MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:e4b
# MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:26b
# MODEL_GEMMA4          ?= ${ollama_prefix}/gemma4:31b
MODEL_QWEN35          ?= ${ollama_prefix}/qwen3.5:35b
MODEL_LLAMA32         ?= ${ollama_prefix}/llama3.2:3B
MODEL_SMOLLM2         ?= ${ollama_prefix}/smollm2:1.7b-instruct-fp16
MODEL_GRANITE4        ?= ${ollama_prefix}/granite4:latest
MODELS                ?= ${MODEL_GPT_OSS} ${MODEL_GEMMA4} ${MODEL_QWEN35} ${MODEL_LLAMA32} ${MODEL_SMOLLM2} ${MODEL_GRANITE4} 
# Default model!
MODEL                 ?= ${MODEL_GEMMA4}

MODEL_FILE_NAME       ?= $(subst :,_,${MODEL})
SRC_DIR               ?= src
OUTPUT_DIR            ?= ${PWD}/output/${MODEL_FILE_NAME}
OUTPUT_LOGS_ROOT_DIR  ?= ${OUTPUT_DIR}/logs
OUTPUT_LOGS_DIR       ?= ${OUTPUT_LOGS_ROOT_DIR}/${TIMESTAMP}
# DATA_DIR: Where the tools write and later read data.
# TEST_DATA_DIR: Where test data is read. RELATIVE to ${SRC_DIR}.
DATA_DIR              ?= ${OUTPUT_DIR}/data
TEST_DATA_DIR         ?= tests/data
CLEAN_CODE_DIRS       ?= ${OUTPUT_DIR}

OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui

# Some specific variables passed as env. vars. to the ChatBot.
# CONFIDENCE_THRESHOLD: What's the minimum confidence (out of 1.0, meaning 100%) for a response that we trust it?
# WHICH_CHATBOT: Which ChatBot implementation to use: 'agent' for ChatBotAgent or 'simple' for ChatBotSimple
CONFIDENCE_THRESHOLD  ?= 0.9
WHICH_CHATBOT         ?= agent

# Some specific variables passed as env. vars. to the test suites.
# ACCUMULATE_TEST_ERRORS:   Should I run ALL prompts, then report accumulated errors? Leave EMPTY for False, non-empty for True!
# RATING_THRESHOLD:         What's the minimum rating (out of 5) for which a test prompt is "good enough" for the particular use case?
# TESTS_LOGS_DIR:           Where special AI test logs are written. RELATIVE TO ${SRC_DIR}!
# TESTS_LOGS_FILE_TEMPLATE: A file name pattern, where "{class_name}" will be replaced with the test class name.
# TESTS_LOGS_FILE_GLOB:     Just used for messages printed by targets.
ACCUMULATE_TEST_ERRORS    ?= True
RATING_THRESHOLD          ?= 4
TESTS_LOGS_DIR            ?= tests/logs/${MODEL_FILE_NAME}
TESTS_LOGS_FILE_TEMPLATE  ?= ${TESTS_LOGS_DIR}/{which_chatbot}-{class_name}-${TIMESTAMP}.jsonl
TESTS_LOGS_FILE_GLOB      ?= ${TESTS_LOGS_DIR}/*-${TIMESTAMP}.jsonl

# Sampling rates for different kinds of tests.
UNIT_TEST_DATA_SAMPLE_RATE        ?= 0.25
INTEGRATION_TEST_DATA_SAMPLE_RATE ?= 1.0
DATA_SAMPLE_RATE                  ?= ${UNIT_TEST_DATA_SAMPLE_RATE}

# These directories will be relative to where the tools and apps are executed.
PROMPTS_TEMPLATES_DIR   ?= tools/prompts/templates
CHATBOT_TEMPLATES_DIR   ?= apps/chatbot/prompts/templates
CHATBOT_DATA_DIR        ?= ${DATA_DIR}/chatbot
CHATBOT_OUTPUT_DIR      ?= ${PWD}/output
CHATBOT_API_SERVER_HOST ?= localhost
CHATBOT_API_SERVER_PORT ?= 8000
CHATBOT_API_SERVER      ?= ${CHATBOT_API_SERVER_HOST}:${CHATBOT_API_SERVER_PORT}

ALL_TOOLS               ?= tdd-example-refill-chatbot unit-benchmark-data-synthesis unit-benchmark-data-validation

# Definitions for the website.
GITHUB_PAGES_URL      ?= https://the-ai-alliance.github.io/ai-application-testing/
DOCS_DIR              ?= docs
SITE_DIR              ?= ${DOCS_DIR}/_site
CLEAN_DOCS_DIRS       ?= ${SITE_DIR} ${DOCS_DIR}/.sass-cache

## Override when running `make view-local` using e.g., `JEKYLL_PORT=8000 make view-local`
JEKYLL_PORT           ?= 4000

# Colors used to make some messages stand out more than others...
RED          = \033[31m
BOLD_RED     = \033[1;31m
GREEN        = \033[32m
BOLD_GREEN   = \033[1;32m
YELLOW       = \033[33m
BOLD_YELLOW  = \033[1;33m
BLUE         = \033[34m
BOLD_BLUE    = \033[1;34m
PURPLE       = \033[35m
BOLD_PURPLE  = \033[1;35m
CYAN         = \033[36m
BOLD_CYAN    = \033[1;36m

ERROR        = ${BOLD_RED}ERROR:
WARN         = ${BOLD_YELLOW}WARNING:
NOTE         = ${BOLD_PURPLE}NOTE:
INFO         = ${BOLD_PURPLE}
TIP          = ${BOLD_BLUE}TIP:
HIGHLIGHT    = ${BOLD_GREEN}
_END         = \033[0m


ifndef DOCS_DIR
$(error ERROR: There is no ${DOCS_DIR} directory!)
endif
ifndef SRC_DIR
$(error ERROR: There is no ${SRC_DIR} directory!)
endif


define help_message

Quick help for this make process. 

Try these more specific help targets:

make help-docs          # Help on the website targets.
make help-tools         # Help on the tools and example ChatBot targets.
make help-code          # Synonym for "help-tools".

make print-info         # Print the current values of some make and env. variables.
make clean              # Makes clean-docs and clean-code, but not clean-setup, uninstall-uv
endef

define help_message_docs

Quick help for this make process. This Makefile is used for the website management.
For running the example tools described there, see src/Makefile or run "make help-src".

make help-docs          # Help on the website make targets.
make all-docs           # Clean and locally view the document.
make clean-docs         # Remove build artifacts, etc.
make view-pages         # View the published GitHub pages in a browser.
make view-local         # View the pages locally (requires Jekyll).
                        # Tip: "JEKYLL_PORT=8000 make view-local" uses port 8000 instead of 4000!

make setup-jekyll       # Install Jekyll. Make sure Ruby is installed. 
                        # (Only needed for local viewing of the document.)
make run-jekyll         # Used by "view-local"; assumes everything is already built.
                        # Tip: "JEKYLL_PORT=8000 make run-jekyll" uses port 8000 instead of 4000!

endef

define help_message_code

Quick help for this make process for the tools and ChatBot example app.
For the tools used to manage the website, run "make help-docs".

For the following targets that run tools, there are variables defined in this Makefile
that are used to pass arguments to the commands. Run 'make print-info-code' to see the
list of variables and their default definitions. Specific variables are mentioned for
the corresponding targets:

make all-models-*       # Extract "*" as one of the other targets (such as, "all-tools"),
                        # that is everything to the right of "all-models-", and 
                        # make that target for ALL the models defined by "MODELS":
                        #   ${MODELS}
                        # (Not useful for model-agnostic targets, like "setup"...)
                        # You can override the list of models as follows:
                        #   make MODELS="..." all-models-...
make all-tools          # Clean outputs and run all the tools using the model defined by "MODEL".
make all-code           # Synonym for "all-tools".
make run-tools          # Run all the tools (but not the ChatBot app) without cleaning first. 
                        # Built by "all-tools".
make run-code           # Synonym for "run-tools".

make setup              # One-time setup tasks; e.g., builds target install-uv.
make one-time-setup     # Synonym for "setup".
make install-uv         # Explain how to install "uv".
                        # Run "make help-command-uv" for more information.
make install-jq         # Explain how to install "jq" (an optional CLI tool).

make build              # Build a distribution
make install            # Install the code locally in development mode

make tests              # Following convention, this target runs the unit tests only, building
                        # the targets "unit-tests-non-ai", "unit-tests-ai", and "unit-tests-appointments".
make test               # Synonym for "tests".
make unit-tests         # Synonym for "tests".
make unit-tests-non-ai  # All unit tests that don't involve inference invocations.
make unit-tests-ai      # All unit tests that do involve inference invocations, which take a long time to run.
make unit-tests-appointments
                        # Unit tests for the appointment management tool.
make unit-tests-langflow
                        # Run unit tests for the Langflow components. NOT built by "tests" or "integration-tests",
                        # so we don't force you to have Langflow installed.

make integration-tests  # Run the integration tests, including "dedicated" integration tests
                        # and all unit tests with more "exhaustive" sample data flags.
make integration-tests-dedicated
                        # The "dedicated" integration tests, omitting the unit tests.

make all-tests          # Run the unit and integration tests.
make all-tests-langflow # Run all the tests for the Langflow integration.

make type-check         # Run the "ty" type checker on the code.

make clean-tools        # Remove build artifacts in ${OUTPUT_DIR}.
make clean-code         # Synonym for "clean-tools".
make clean-setup        # Undoes everything done by the setup target or provides
                        # instructions for what you must do manually in some cases.
make uninstall-uv       # Explain how to uninstall "uv".

For tools run by the following targets, which invoke inference, the model 
${MODEL} is served by ollama. The make variable MODEL specifies the model, 
so if you want to use a different model, invoke make as in this example:

  make MODEL=ollama_chat/llama3.2:3B run-tdd-example-refill-chatbot

See also the description of "all-models-*" above.

All the following" targets may run setup dependencies that are redundant most of the time,
but easy to forgot when important! See also the "help-*" targets below.

make run-tdd-example-refill-chatbot   
                        # Run the code for the TDD example "unit benchmark".
                        # See the TDD chapter in the website for details.
make run-terc           # Synonym for "run-tdd-example-refill-chatbot".
make terc               # Synonym for "run-tdd-example-refill-chatbot".

make run-unit-benchmark-data-synthesis
                        # Run the code for "unit benchmark" data synthesis.
                        # See the Unit Benchmark chapter in the website for details.
make run-ubds           # Synonym for "run-unit-benchmark-data-synthesis".
make ubds               # Synonym for "run-unit-benchmark-data-synthesis".

make run-unit-benchmark-data-validation
                        # Run the code for validating the synthetic data for the unit benchmarks.
                        # See the Unit Benchmark chapter in the website for details.
make run-ubdv           # Synonym for "run-unit-benchmark-data-validation".
make ubdv               # Synonym for "run-unit-benchmark-data-validation".

make run-langflow-pipeline
                        # Run the Langflow benchmark pipeline (synthesis + validation).
                        # This orchestrates both synthesis and validation in a single flow.
make langflow-pipeline  # Synonym for "run-langflow-pipeline".

The following targets are for the example ChatBot application. See also the "help-*" targets next.

make chatbot            # Run the ${WHICH_CHATBOT} implementation of the ChatBot application.
make run-chatbot        # Synonym for "chatbot".
make agent-chatbot      # Run the 'agent' implementation of the ChatBot.
make simple-chatbot     # Run the 'simple' implementation of the ChatBot.

make mcp-server         # Run the ChatBot's MCP server.
make run-mcp-server     # Synonym for "mcp-server".
make api-server         # Run the ChatBot's OpenAI-compatible API server.
make run-api-server     # Synonym for "api-server".

Tasks for help, debugging, setup, etc.

make help-tools         # Prints this output.
make help-code          # Synonym for "help-tools".
make help-tools-all     # Prints this output and makes "help-terc", "help-ubds" and "help-ubdv".
make help-code-all      # Synonym for "help-tools-all".

make help-terc          # Synonym for "help-tdd-example-refill-chatbot".
make help-tdd-example-refill-chatbot   
                        # Show help for the TDD example code by passing the "--help" flag.

make help-ubds          # Synonym for "help-unit-benchmark-data-synthesis".
make help-unit-benchmark-data-synthesis
                        # Show help for the "unit benchmark" data synthesis code by passing the "--help" flag.

make help-ubdv          # Synonym for "help-unit-benchmark-data-validation".
make help-unit-benchmark-data-validation
                        # Show help for the synthetic data validation code by passing the "--help" flag.
                        # Run the code for validating the synthetic data for the unit benchmarks.

make help-langflow-pipeline
                        # Show help for the Langflow pipeline by passing the "--help" flag.
make help-langflow      # Synonym for "help-langflow-pipeline".

make help-chatbot       # Show help for the interactive ChatBot application.
make help-mcp-server    # Show help for the ChatBot's MCP server.
make help-api-server    # Show help for the ChatBot's OpenAI-compatible API server.

make view-api-server-docs  # Open a browser showing the API server "docs".
make view-api-server-redoc # Open a browser showing the API server "redoc".

Several CLI tools are required, like "uv", or only needed for a few special make targets, like "jq":

make help-command-uv    # Prints specific information about "uv", including installation.
make help-command-jq    # Prints specific information about "jq", including installation.
endef

define help_message_uv

The Python environment management tool "uv" is required.
See https://docs.astral.sh/uv/ for installation instructions.

If you want to uninstall uv and you used HomeBrew to install it,
use 'brew uninstall uv'. Otherwise, if you executed one of the
installation commands on the website above, find the installation
location and delete uv.

endef


define help_message_jq

The CLI command 'jq' is useful, but not required, for processing JSON file.
See https://jqlang.org/download/ for installation instructions.

endef

define help_message_node
The JavaScript runtime "node" is required if you want to use the MCP server
inspector `@modelcontextprotocol/inspector`. Otherwise, node is not used in
this project. See https://nodejs.org/en/download/ for installation instructions.
endef

open-url-message = Try ${HIGHLIGHT}⌘+click${_END} or ${HIGHLIGHT}^+click${_END} on the URL.

define gem-error-message

ERROR: Did the gem command fail with a message like this?
ERROR: 	 "You don't have write permissions for the /Library/Ruby/Gems/2.6.0 directory."
ERROR: To run the "gem install ..." command for the MacOS default ruby installation requires "sudo".
ERROR: Instead, use Homebrew (https://brew.sh) to install ruby and make sure "/usr/local/.../bin/gem"
ERROR: is on your PATH before "user/bin/gem".
ERROR:
ERROR: Or did the gem command fail with a message like this?
ERROR:   Bundler found conflicting requirements for the RubyGems version:
ERROR:     In Gemfile:
ERROR:       foo-bar (>= 3.0.0) was resolved to 3.0.0, which depends on
ERROR:         RubyGems (>= 3.3.22)
ERROR:   
ERROR:     Current RubyGems version:
ERROR:       RubyGems (= 3.3.11)
ERROR: In this case, try "brew upgrade ruby" to get a newer version.

endef

define bundle-error-message

ERROR: Did the bundle command fail with a message like this?
ERROR: 	 "/usr/local/opt/ruby/bin/bundle:25:in `load': cannot load such file -- /usr/local/lib/ruby/gems/3.1.0/gems/bundler-X.Y.Z/exe/bundle (LoadError)"
ERROR: Check that the /usr/local/lib/ruby/gems/3.1.0/gems/bundler-X.Y.Z directory actually exists. 
ERROR: If not, try running the clean-jekyll command first:
ERROR:   make clean-jekyll setup-jekyll
ERROR: Answer "y" (yes) to the prompts and ignore any warnings that you can't uninstall a "default" gem.

endef

define command_check_message
Shell command \"$$cmd\" is required for a make target. Try \"make help-command-$$cmd\" for more information, or \"make install-$$cmd\" may be able to install it. See also the project's README.md for more information.
endef

define missing_ruby_gem_or_command_error_message
is needed by ${PWD}/Makefile. Try "gem install ..."
endef

define ruby_and_gem_required_message
'ruby' and 'gem' are required. See ruby-lang.org for installation instructions.
endef

define gem_required_message
Ruby's 'gem' is required. See ruby-lang.org for installation instructions.
endef

# Help and Other Information Targets

.PHONY: help help-docs help-tools help-code help-tools-all help-code-all help-command-uv help-command-uvx  help-command-jq

all:: help

help::
	$(info ${help_message})
	@echo

help-tools:: help-code
help-docs help-code::
	$(info ${help_message_${@:help-%=%}})
	@echo
help-command-uv help-command-uvx::
	$(info ${help_message_uv})
	@echo
help-command-jq::
	$(info ${help_message_jq})
	@echo

help-command-%::
	@echo "${GREEN}${RED}Sorry, no built-in help is available for CLI command '${@:help-command-%=%}'.${_END}"

help-tools-all help-code-all:: help-code help-terc help-ubds help-ubdv

.PHONY: clean clean-docs clean-tools clean-code clean-jekyll

clean:: clean-docs clean-tools clean-jekyll
clean-code:: clean-tools

.PHONY: print-info print-info-docs print-info-tools print-info-code print-info-env

print-info:: print-info-docs print-info-code print-info-env 
print-info-docs::
	@echo "${GREEN}For the GitHub Pages website:${_END}"
	@echo "  ${GREEN}GITHUB_PAGES_URL:${_END}        ${GITHUB_PAGES_URL}"
	@echo "  ${GREEN}PWD:${_END}                     ${PWD} ('print working directory')"
	@echo "  ${GREEN}DOCS_DIR:${_END}                ${DOCS_DIR}"
	@echo "  ${GREEN}SITE_DIR:${_END}                ${SITE_DIR}"
	@echo "  ${GREEN}JEKYLL_PORT:${_END}             ${JEKYLL_PORT}"
	@echo

print-info-tools:: print-info-code
print-info-code::
	@echo "${GREEN}For the example code and tools:${_END}"
	@echo "  ${GREEN}MODEL:${_END}                   ${MODEL} (the default)"
	@echo "  ${GREEN}MODELS:${_END} (all we use)     ${MODELS}"
	@echo "  ${GREEN}ALL_TOOLS:${_END}               ${ALL_TOOLS}"
	@echo "  ${GREEN}INFERENCE_SERVICE:${_END}       ${INFERENCE_SERVICE}"
	@echo "  ${GREEN}INFERENCE_URL:${_END}           ${INFERENCE_URL}"
	@echo "  ${GREEN}PROMPTS_TEMPLATES_DIR:${_END}   ${PROMPTS_TEMPLATES_DIR}"
	@echo "  ${GREEN}CHATBOT_TEMPLATES_DIR:${_END}   ${CHATBOT_TEMPLATES_DIR}"
	@echo "  ${GREEN}CHATBOT_OUTPUT_DIR:${_END}      ${CHATBOT_OUTPUT_DIR}"
	@echo "  ${GREEN}SRC_DIR:${_END}                 ${SRC_DIR}"
	@echo "  ${GREEN}APP_ARGS:${_END}                ${APP_ARGS} (User hook for passing custom arguments, like '-h')"
	@echo "  ${GREEN}The following depend on the value of MODEL:${_END}"
	@echo "  ${GREEN}OUTPUT_DIR:${_END}              ${OUTPUT_DIR}"
	@echo "  ${GREEN}OUTPUT_LOGS_DIR:${_END}         ${OUTPUT_LOGS_DIR}"
	@echo "  ${GREEN}TESTS_LOGS_DIR:${_END}          ${TESTS_LOGS_DIR} (relative to ${SRC_DIR})"
	@echo "  ${GREEN}DATA_DIR:${_END}                ${DATA_DIR}"
	@echo "  ${GREEN}ACCUMULATE_TEST_ERRORS:${_END}  ${ACCUMULATE_TEST_ERRORS} (For tests, run all examples, then report errors. '' == False)"
	@echo
print-info-env::
	@echo "${GREEN}The environment:${_END}"
	@echo "  ${GREEN}GIT_HASH:${_END}                ${GIT_HASH}"
	@echo "  ${GREEN}TIMESTAMP:${_END}               ${TIMESTAMP}"
	@echo "  ${GREEN}MAKEFLAGS:${_END}               ${MAKEFLAGS}"
	@echo "  ${GREEN}MAKEFLAGS_RECURSIVE:${_END}     ${MAKEFLAGS_RECURSIVE}"
	@echo "  ${GREEN}UNAME:${_END}                   ${UNAME}"
	@echo "  ${GREEN}ARCHITECTURE:${_END}            ${ARCHITECTURE}"
	@echo "  ${GREEN}GIT_HASH:${_END}                ${GIT_HASH}"
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
	echo "Making target \"$$target\" for all models: ${MODELS}"; \
	for model in ${MODELS}; \
	do \
		echo "\nModel = $$model"; \
		echo ${MAKE} ${MAKEFLAGS} TIMESTAMP=${TIMESTAMP} MODEL="$$model" $$target; \
		${MAKE} MODEL="$$model" $$target; \
	done; \
	echo "Output log files (if any) can be found under:"; \
	for model in ${MODELS}; \
	do \
		echo "  output/$$model/logs/${TIMESTAMP}"; \
	done

all-tools all-code:: run-tools
run-tools run-code:: 
	${MAKE} TIMESTAMP=${TIMESTAMP} ${ALL_TOOLS:%=run-%} 

clean-tools clean-code:: 
	rm -rf ${CLEAN_CODE_DIRS}   

terc run-terc:: run-tdd-example-refill-chatbot
ubds run-ubds:: run-unit-benchmark-data-synthesis
ubdv run-ubdv:: run-unit-benchmark-data-validation

help-terc:: help-tdd-example-refill-chatbot
help-ubds:: help-unit-benchmark-data-synthesis
help-ubdv:: help-unit-benchmark-data-validation

${ALL_TOOLS:%=help-%}::
	@echo "${GREEN}Help on ${@help-%=%}.py:"
	@echo
	cd ${SRC_DIR} && uv run tools/${@:help-%=%}.py --help
	@echo

# LITELLM_LOG=ERROR turns off some annoying INFO messages, sufficient
# for our purposes. See the LiteLLM docs for logging configuration details.
# Define APP_ARGS on the command line to pass custom arguments, e.g., 
#   make APP_ARGS='--help' run-tdd-example-refill-chatbot
# just prints help.

run-tdd-example-refill-chatbot:: before-run
	@echo "${INFO} *** Running the TDD example. ${_END}"
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS}
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-synthesis:: before-run
	@echo "${INFO} *** Running the unit benchmark data synthesis example. ${_END}"
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${PROMPTS_TEMPLATES_DIR} \
		--data-dir ${DATA_DIR} \
		--use-cases ${USE_CASES} \
		--log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
		${APP_ARGS}
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

run-unit-benchmark-data-validation:: before-run
	@echo "${INFO} *** Running the unit benchmark synthetic data validation example. ${_END}"
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run tools/${@:run-%=%}.py \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-cases ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/${@:run-%=%}.log \
	  ${JUST_STATS} ${APP_ARGS}
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${@:run-%=%}.log${_END}\n"

before-run:: silent-before-run
	@echo "${WARN}${_END} If errors occur, try ${HIGHLIGHT}make setup${_END} or ${HIGHLIGHT}make clean-setup setup${_END}, then try again."

silent-before-run:run-command-checks ${OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${DATA_DIR}  
run-command-checks:: command-check-uv provider-server-check

provider-server-check::
	@[[ ${INFERENCE_SERVICE} != 'ollama' ]] || ollama ps > /dev/null || ! echo "${ERROR}: Ollama is not running!${_END}" || exit 1

# Langflow targets
.PHONY: run-langflow-pipeline langflow-pipeline help-langflow-pipeline  
.PHONY: unit-tests-langflow all-tests-langflow

run-langflow-pipeline:: langflow-pipeline
langflow-pipeline:: 
	@echo "${INFO}Running the Langflow unit benchmark pipeline (synthesis + validation)...${_END}"
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@}.log${_END}\n"
	export LITELLM_LOG=ERROR; \
	cd ${SRC_DIR} && ${TIME} uv run python -m tools.langflow.unit_benchmark_flow \
	  --model ${MODEL} \
	  --service-url ${INFERENCE_URL} \
	  --template-dir ${PROMPTS_TEMPLATES_DIR} \
	  --data-dir ${DATA_DIR} \
	  --use-case ${USE_CASES} \
	  --log-file ${OUTPUT_LOGS_DIR}/$@.log \
	  ${JUST_STATS} ${APP_ARGS}
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

help-lf help-langflow help-langflow-pipeline::
	@echo "${INFO}Help on the Langflow unit benchmark pipeline:${_END}"
	@echo
	cd ${SRC_DIR} && uv run python -m tools.langflow.unit_benchmark_flow --help
	@echo

all-tests-langflow unit-tests-langflow:: run-command-checks
	@echo "${INFO}Running the langflow unit tests...${_END}"
	cd ${SRC_DIR} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export PROMPTS_TEMPLATES_DIR=${PROMPTS_TEMPLATES_DIR} && \
	  export DATA_DIR=${DATA_DIR} && \
	  uv run python -m unittest discover \
	    --start-directory tests/unit/langflow \
	    --top-level-directory .

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
		--verbose ${APP_ARGS}

agent-chatbot simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:%-chatbot=%} chatbot

.PHONY: help-chatbot help-agent-chatbot help-simple-chatbot 

help-agent-chatbot help-simple-chatbot:: 
	${MAKE} WHICH_CHATBOT=${@:help-%-chatbot=%} help-chatbot

help-chatbot::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.main --help

before-chatbot:: run-command-checks ${OUTPUT_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${CHATBOT_DATA_DIR}
	@echo "${INFO}Running the \"${WHICH_CHATBOT}\" ChatBot...${_END}" && \
	echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}\n" && \
		[[ ${MODEL} =~ gpt-oss ]] && [[ ${WHICH_CHATBOT} = agent ]] && \
		echo "${ERROR} ${MODEL} currently can't be used with the \"${WHICH_CHATBOT}\" ChatBot!${_END} (https://github.com/langchain-ai/langchain/issues/33116). Try using ${MODEL_GEMMA4}" && exit 1 || \
		echo ""

after-chatbot::
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/${WHICH_CHATBOT}-chatbot.log${_END}\n"

.PHONY: mcp-server run-mcp-server help-mcp-server check-mcp-server inspect-mcp-server

# See inspect-mcp-server for information about ${INSPECTOR}, which is otherwise
# blank.
run-mcp-server:: mcp-server
mcp-server:: before-chatbot
	@echo "${INFO}Running the ChatBot MCP Server...${_END}"
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
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

inspect-mcp-server:: command-check-node
	@echo "${INFO}Running the @modelcontextprotocol/inspector with the ChatBot MCP Server...${_END}"
	${MAKE} INSPECTOR="npx @modelcontextprotocol/inspector" mcp-server

help-mcp-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.mcp_server.server --help

.PHONY: api-server run-api-server help-api-server check-api-server view-api-server-docs view-api-server-redoc

run-api-server:: api-server
api-server:: before-chatbot
	@echo "${INFO}Running the ChatBot OpenAI-compatible API Server...${_END}"
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"
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
	@echo "\nLog output:\n  ${HIGHLIGHT}${OUTPUT_LOGS_DIR}/$@.log${_END}\n"

help-api-server::
	cd ${SRC_DIR} && uv run python -m apps.chatbot.api_server.server --help

check-api-server::
	@echo "${INFO}'Sanity check' that the OpenAI-compatible API server works:${_END}"
	@echo "Running the server in the background..."
	${MAKE} api-server & 
	@echo
	@echo "  ${HIGHLIGHT}Hit the 'return' key!${_END}"
	@echo
	@echo "  Running 'apps/chatbot//api_server/example_client.py'..."
	cd ${SRC_DIR} && uv run python apps/chatbot/api_server/example_client.py
	@echo "  ${INFO}Hack: Find the process id for the server and kill it...${_END}" 
	kill %1

view-api-server-docs view-api-server-redoc::
	@echo
	@echo "Opening ${INFO}http://${CHATBOT_API_SERVER}/${@:view-api-server-%=%}${_END}"
	@echo
	@echo "${open-url-message}"
	@echo "If the URL isn't found, make sure the server is running! For example,"
	@echo "run ${HIGHLIGHT}make api-server${_END} in another terminal window, then rerun this target." 
	@uv run python -m webbrowser "http:${_END}//${CHATBOT_API_SERVER}/${@:view-api-server-%=%}"

.PHONY: run-open-webui open-webui open-webui-preamble open-webui-setup help-open-webui remove-open-webui

run-open-webui open-webui:: open-webui-preamble open-webui-setup
	cd ${OPEN_WEBUI_DIR} && DATA_DIR=${CHATBOT_DATA_DIR} uv tool run --with greenlet open-webui serve

open-webui-preamble::
	@echo "${INFO}Running Open WebUI (https://docs.openwebui.com/getting-started/) out of directory ${OPEN_WEBUI_DIR}.${_END}"
	@echo "${INFO}Make sure the OpenAI-compatible API Server is running first, i.e., make api-server in another terminal!${_END}"
	@echo "\nOpen ${RED}http://localhost:8080${_END} when it is up (it takes a few minutes)."
	@echo "${open-url-message}"

open-webui-setup::
	@test -d ${OPEN_WEBUI_DIR}/.venv || (\
		echo "Setting up Open WebUI in the ${HIGHLIGHT}${OPEN_WEBUI_DIR}${_END} directory." && \
		cd ${OPEN_WEBUI_DIR} && uv venv && uv sync && uv tool install open-webui)
	cd ${OPEN_WEBUI_DIR} && . .venv/bin/activate

help-open-webui:: 
	DATA_DIR=${CHATBOT_DATA_DIR} uvx --python 3.12 --with greenlet open-webui@latest serve --help

remove-open-webui::
	uv tool uninstall open-webui
	rm -rf $HOME/.open-webui

${OUTPUT_DIR} ${CHATBOT_OUTPUT_DIR} ${OUTPUT_LOGS_DIR} ${SRC_DIR}/${TESTS_LOGS_DIR} ${DATA_DIR} ${CHATBOT_DATA_DIR}::
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
	@echo "${INFO}Running the non-AI unit tests...${_END}"
	cd ${SRC_DIR} && \
	  uv run python -m unittest discover \
	    --pattern 'test*.py' \
	    --start-directory tests/unit \
	    --top-level-directory .

.PHONY:${_END} unit-tests-appointments

unit-tests-appointments::
	@echo "${INFO}Running the appointment tool unit tests...${_END}"
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
unit-tests-ai-agent unit-tests-ai-simple:: ${SRC_DIR}/${TESTS_LOGS_DIR} 
	@echo "${INFO}Running the AI unit tests with the \"${@:unit-tests-ai-%=%}\" ChatBot...${_END}"
	@echo "${INFO}AI test log files: ${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export PROMPTS_TEMPLATES_DIR=${PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
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
# make TEST=path/to/test.py one-test-ai

one-test-ai:: ${SRC_DIR}/${TESTS_LOGS_DIR}
	@echo "${INFO}Running one AI unit test: TEST = ${TEST} ...${_END}"
	@echo "${TIP}${_END} Use ${BOLD_PURPLE}make list-unit-tests-ai${_END} to see the list of tests."
	@echo
	@echo "${INFO}AI test log files: ${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export PROMPTS_TEMPLATES_DIR=${PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
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
	@echo "${INFO}Time-stamped JSONL log files were written to:\n  ${BOLD_PURPLE}${SRC_DIR}/${TESTS_LOGS_FILE_GLOB}${INFO}.\nThey may be empty!${_END}"
	@echo "${INFO}The corresponding '*.json' files (if any) were generated using 'jq' and target 'nice-ai-test-logs'. They are easier to read.${_END}"
	@echo
	@echo ${MAKE} nice-ai-test-logs || ${MAKE} show-test-logs

show-test-logs::
	@ls -l ${SRC_DIR}/${TESTS_LOGS_DIR}/*.json*
	@echo
	@echo "${TIP}${_END} Run ${HIGHLIGHT}make nice-ai-test-logs${_END} to make a nicely-formatted JSON file from each JSONL file ('jq' CLI tool required)."
	@echo 

.PHONY: nice-ai-test-logs

# This target nicely formats the AI-related test logs into more readable JSON. Requires jq
nice-ai-test-logs:: silent-command-check-jq 
	@for f in ${SRC_DIR}/${TESTS_LOGS_DIR}/*.jsonl; do ff=$${f%l}; [[ -f $$ff  ]] || \
	  echo "writing $$ff:"; \
	  jq . $$f > $$ff; \
	done
	@ls -l ${SRC_DIR}/${TESTS_LOGS_DIR}/*.json*

integ-tests integration-tests:: integration-tests-dedicated integration-tests-from-unit-tests

# This target runs all the unit-tests, the AI-related, but more exhaustively, as well as the non-AI unit tests.
integration-tests-from-unit-tests:: run-command-checks
	@echo "${INFO}Running the unit tests as integration tests with 100% sampling and trying all test query examples...${_END}"
	${MAKE} DATA_SAMPLE_RATE=${INTEGRATION_TEST_DATA_SAMPLE_RATE} tests

integration-tests-dedicated:: run-command-checks
	@echo "${INFO}Running the 'dedicated' integration tests...${_END}"
	cd ${SRC_DIR} && \
	  export DATA_SAMPLE_RATE=${INTEGRATION_TEST_DATA_SAMPLE_RATE} && \
	  export MODEL=${MODEL} && \
	  export INFERENCE_URL=${INFERENCE_URL} && \
	  export PROMPTS_TEMPLATES_DIR=${PROMPTS_TEMPLATES_DIR} && \
	  export CHATBOT_TEMPLATES_DIR=${CHATBOT_TEMPLATES_DIR} && \
	  export DATA_DIR=${TEST_DATA_DIR} && \
	  export ACCUMULATE_TEST_ERRORS=${ACCUMULATE_TEST_ERRORS} && \
	  export RATING_THRESHOLD=${RATING_THRESHOLD} && \
	  export CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD} && \
	  export VERBOSE='True' && \
	  uv run python -m unittest discover \
	  	--start-directory tests/integration \
	  	--top-level-directory .

.PHONY:${_END} type-check type-check-watch

type-check::
	@echo "${INFO}Running 'ty' on the code.${_END}"
	uvx ty check ${SRC_DIR} 
type-check-watch::
	@echo "${INFO}Running 'ty' on the code in 'watch' mode.${_END}"
	uvx ty check --watch ${SRC_DIR} 

.PHONY:${_END} one-time-setup setup clean-setup 
.PHONY: uninstall-uv 
.PHONY: install-uv uv-venv install-jq

setup one-time-setup:: install-uv uv-venv install-jq

clean-setup:: uninstall-uv

uninstall-uv:: 
	@echo "${INFO}You have to uninstall ${@:uninstall-%=%} manually:${_END}"
	@echo
	$(info ${help_message_${@:uninstall-%=%}})

install-uv:: 
	@cmd=${@:install-%=%} && command -v $$cmd > /dev/null && \
		echo "${INFO}$$cmd is already installed${_END}" || ${MAKE} help-$$cmd

uv-venv:: command-check-uv 
	uv venv

install-jq:: help-command-jq

%-error:
	$(error ${${@}-message})

# Check if a command is on the path.
command-check-%:
	@cmd=${@:command-check-%=%} && ${MAKE} silent-$@ || \
		! echo "${ERROR} ${command_check_message}${_END}" || exit 1

silent-command-check-%:
	@cmd=${@:silent-command-check-%=%} && command -v $$cmd > /dev/null

# The next section of this Makefile includes some convenience targets for working 
# with the "llm" CLI tool. It is NOT required to install and use this tool.
# See the Appendix in the README.md for details.

define help_message_llm

The "llm" CLI is used by many of the tools here. For more details, see:
  https://github.com/simonw/llm

You can install llm using pip:
  pip install -U llm bs4
or if you use uv:
  uv add -U llm bs4

To remove llm, use the corresponding commands, one of:
  pip uninstall llm bs4
  uv remove llm bs4

If you want to serve models locally using "ollama", see the installation 
instructions:
  https://ollama.com 

Then install the llm plugin for ollama:
  llm install llm-ollama

The tools also use several llm "templates". These need to be installed into
the directory output by this llm command:
  llm templates path

Use the following make command to do this automatically:
  make install-llm-templates 

WARNING: If you edit the templates in ${PROMPTS_TEMPLATES_DIR}, rerun  
  make install-llm-templates 

(llm is required to run this target, because it uses 'llm templates path'
to determine the installation location.)

So, to summarize the llm-related targets (and mention the rest of them):

make help-llm               # This information!
make install-llm            # Instructions for installing llm.
make install-llm-templates  # Install our llm "templates" into llm.
make clean-llm              # Instructions for uninstalling llm. Also makes clean-llm-templates.
make clean-llm-templates    # Remove our llm "templates" from the llm installation location.

endef

.PHONY: help-llm clean-llm clean-llm-templates install-llm

help-llm::
	$(info ${help_message_llm})
	@echo

clean-llm:: help-llm clean-llm-templates
	@echo
	@echo "${NOTE}${_END} ${HIGHLIGHT}make clean-llm-templates${_END} was already executed to uninstall our templates."
	@echo

clean-llm-templates::
	@cd ${PROMPTS_TEMPLATES_DIR} && \
		llmdir="$$(llm templates path)" && \
		for t in *.yaml; do echo "removing: $$llmdir/$$t"; rm -f "$$llmdir/$$t"; done && \
		ls -l "$$llmdir"

install-llm:: help-llm install-llm-templates
	@echo
	@echo "${NOTE}${_END} ${HIGHLIGHT}make install-llm-templates${_END} was already executed to install our templates."
	@echo

install-llm-templates:: command-check-llm
	@llmdir="$$(llm templates path)" && \
	echo "${INFO}${_END}Installing the llm templates from ${HIGHLIGHT}${PROMPTS_TEMPLATES_DIR}${_END} into ${HIGHLIGHT}$$llmdir${_END} ..." && \
	cp ${PROMPTS_TEMPLATES_DIR}/*.yaml "$$llmdir" && \
	ls -l "$$llmdir"


.PHONY: build install

build::
	@echo "${INFO}Building a distribution...${_END}"
	rm -rf dist
	uv build
	@echo "${INFO}Contents of 'dist':${_END}${_END}"
	@ls -l dist

install::
	@echo "${INFO}Installing the code locally in development mode...${_END}"
	uv sync

# Docs Targets - for the website.
# These targets are only needed when you want to preview edits locally, by running
# Jekyll. The exception is "view-pages", which opens the published site in a browser.

.PHONY: all-docs clean-docs
.PHONY: view-pages view-local setup-jekyll run-jekyll run-jekyll-message

all-docs:: clean-docs view-local

clean-docs::
	rm -rf ${CLEAN_DOCS_DIRS}   

view-pages::
	@echo "${GREEN}Opening ${GITHUB_PAGES_URL} ..."
	@uv run python -m webbrowser "${GITHUB_PAGES_URL}" || \
		(echo "${ERROR}${_END} I could not open the GitHub Pages URL:\n  ${HIGHLIGHT}${GITHUB_PAGES_URL}${_END}\n${_END}" && \
		 echo "${open-url-message}" && \
		 exit 1 )

view-local:: setup-jekyll run-jekyll

# Passing --baseurl '' allows us to use `localhost:4000` rather than require
# `localhost:4000/The-AI-Alliance/ai-application-testing` when running locally.
run-jekyll: clean-docs run-jekyll-message
	cd ${DOCS_DIR} && bundle exec jekyll serve --port ${JEKYLL_PORT} --baseurl '' --incremental || ( echo "ERROR: Failed to run Jekyll. Try running 'make setup-jekyll'." && exit 1 )

run-jekyll-message::
	@echo
	@echo "${NOTE}${_END}You will see the ${HIGHLIGHT}http://127.0.0.1:${JEKYLL_PORT}/${_END} URL printed when ready."
	@echo "${open-url-message}"

setup-jekyll:: ruby-installed-check command-check-ruby-bundle
	@echo "${INFO}Updating Ruby gems required for local viewing of the docs, including jekyll.${_END}"
	gem install jekyll bundler jemoji || ${MAKE} gem-error
	bundle install || ${MAKE} bundle-error
	bundle update html-pipeline || ${MAKE} bundle-error


ruby-installed-check:
	@command -v ruby > /dev/null || \
		( echo "${ERROR}${_END} ${ruby_and_gem_required_message}" && exit 1 )
	@command -v gem  > /dev/null || \
		( echo "${ERROR}${_END} ${gem_required_message}" && exit 1 )

command-check-ruby-%:
	@command -v ${@:command-check-ruby-%=%} > /dev/null || \
		( echo "${ERROR}${_END} Ruby command/gem \"${@:command-check-ruby-%=%}\" ${missing_ruby_gem_or_command_error_message}" && \
			exit 1 )


# NOTE: We call make to run these %-error targets, because if you try
# some_command || $(error "didn't work"), the $(error ...) function is always
# invoked, independent of the shell script logic. Hence, the only way to make
# this invocation conditional is to use a make target invocation, as shown above.
jekyll-error:
	$(error "ERROR: Failed to run Jekyll. Try running 'make setup-jekyll'.")
ruby-missing-error:
	$(error "ERROR: 'ruby' is required. ${ruby_installation_message}")
gem-missing-error:
	$(error "ERROR: Ruby's 'gem' is required. ${ruby_installation_message}")
gem-error:
	$(error ${gem-error-message})
bundle-error:
	$(error ${bundle-error-message})
bundle-missing-error:
	$(error "ERROR: Ruby gem command 'bundle' is required. I tried 'gem install bundle', but it apparently didn't work!")
