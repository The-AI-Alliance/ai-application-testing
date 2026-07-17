# .common.mk
# See comment at the bottom of this file about "-include .custom.mk".

# Definitions of RED, GREEN, etc., and INFO, ERROR, etc. for console output.
# To see them in action, try "make show-colors".
include .console-colors.mk

# Some of the following definitions may be overridden in Makefile. Some notes:
# TESTS_BASE_DIR: By default, it is UNDER ${SRC_DIR}.
# WHICH_TESTS: By default, it equals ${TESTS_BASE_DIR}, meaning the assumption is
# the uni-tests target should build all tests found under ${TESTS_BASE_DIR}. However,
# some projects separate tests into unit, integration, etc. tests. So, if unit tests
# are in a "unit" subdirectory, for example, the project Makefile should define
# WHICH_TESTS=${TESTS_BASE_DIR}/unit AFTER including .common.mk. WHICH_TESTS can also
# be used to specify an individual test file or test (see https://docs.pytest.org/en/stable/how-to/usage.html).
# OUTPUT_TESTS_DIR: Where some test outputs are written by the AI-related tests,
# but not all tests! It is RELATIVE to ${PWD}, NOT ${SRC_DIR}.
SRC_DIR                   ?= src
TESTS_BASE_DIR            ?= ${SRC_DIR}/tests
WHICH_TESTS               ?= ${TESTS_BASE_DIR}
OUTPUT_DIR                ?= output
OUTPUT_TESTS_DIR          ?= ${OUTPUT_DIR}/tests
OUTPUT_LOGS_ROOT_DIR      ?= ${OUTPUT_DIR}/logs
OUTPUT_LOGS_DIR           ?= ${OUTPUT_LOGS_ROOT_DIR}/${TIMESTAMP}
OUTPUT_LOGS_TESTS_DIR     ?= ${OUTPUT_TESTS_DIR}/logs/${TIMESTAMP}
CLEAN_CODE_DIRS           := ${OUTPUT_DIR}
CLEAN_DIRS                += ${CLEAN_CODE_DIRS}

QUALITY_CHECKS_NO_TESTS   := format ruff pylint type-check
QUALITY_CHECKS            := ${QUALITY_CHECKS_NO_TESTS}
PYLINT_IGNORE_ARGS        := --ignore=.venv --ignore-pattern='.*cache.*'

# Define PYTEST_*_OPT_ARGS in Makefiles to customize behavior.
PYTEST_RUN_OPT_ARGS       ?=
PYTEST_COV_OPT_ARGS       ?=
PYTEST_RUN_CMD            := uv run --active coverage run -m pytest -v -s ${PYTEST_RUN_OPT_ARGS}
PYTEST_COV_REPORT_CMD     := uv run --active coverage report -m ${PYTEST_COV_OPT_ARGS}

# The environment
LOCAL_REPO_PATH           ?= $(shell git rev-parse --show-toplevel)
REPO_NAME                 ?= $(notdir ${LOCAL_REPO_PATH})
MAKEFLAGS                 ?= --warn-undefined-variables
MAKEFLAGS_RECURSIVE       ?= # --print-directory (only useful for recursive makes...)
UNAME                     ?= $(shell uname)
ARCHITECTURE              ?= $(shell uname -m)

# Model extension:
# If the architecture is "arm64" (Apple Silicon), then we define a MODEL_APPENDIX=-mlx,
# which Makefiles can append to variables that specify LLMs. Otherwise, this variable
# is empty. However, it won't change the value if one was already set in the Makefile,
# _before_ this file was included.

ifeq (${ARCHITECTURE}, arm64)
	MODEL_APPENDIX ?= -mlx
else
	MODEL_APPENDIX ?=
endif

# Used for version tagging release artifacts.
GIT_HASH                 ?= $(shell git show --pretty="%H" --abbrev-commit |head -1)
TIMESTAMP                ?= $(shell date +"%Y%m%d-%H%M%S")

# Time execution
TIME                     ?= time  # time execution of long processes

ifndef SRC_DIR
$(error ${ERROR} There is no ${SRC_DIR} directory!${_END})
endif

# When you see ${CODE}${_END} without anything between them, it is there 
# to make it easier to line up multi-line description comments.

define help-message-general
${HIGHLIGHT}Quick help for this make process: General Targets${_END}

${CODE}make all${_END}                # Makes the ${CODE}help${_END} and ${CODE}print-info${_END} targets.
${CODE}make help${_END}               # Prints this output.
${CODE}make print-info${_END}         # Print the current values of some make and environment variables.

${HIGHLIGHT}Working with code:${_END}

${CODE}make one-time-setup${_END}     # "One time setup" of dependencies. Requires MacOS or Linux.
${CODE}make unit-tests${_END}         # Run the unit test suite.
${CODE}make tests${_END}              # Alias for ${CODE}tests${_END}.
${CODE}make clean${_END}              # Remove built artifacts, etc.
${CODE}make format${_END}             # Format the Python code with ${CODE}black${_END}.
${CODE}make lint${_END}               # Lint the Python code by making the ${CODE}ruff${_END} and ${CODE}pylint${_END} targets.
${CODE}make ruff${_END}               # Lint the Python code with ${CODE}ruff${_END}.
${CODE}make pylint${_END}             # Lint the Python code with ${CODE}pylint${_END}.
${CODE}make type-check${_END}         # Type check the Python code with ${CODE}ty${_END}.
${CODE}make type-check-watch${_END}   # Type check the Python code with ${CODE}ty${_END} in "watch" mode,
${CODE}${_END}                        # so you can fix mistakes and keep it updating.
${CODE}make before-pr${_END}          # Make ${CODE}format${_END}, ${CODE}lint${_END}, ${CODE}type-check${_END}, and ${CODE}tests${_END}.
${CODE}${_END}                        # DO THIS BEFORE SUBMITTING A PR!
${CODE}before-pr-no-tests${_END}      # Everything in ${CODE}before-pr${_END} except ${CODE}tests${_END}
${CODE}make clean${_END}              # Delete temporary artifacts under ${CODE}CLEAN_DIRS${_END} = ${CODE}${CLEAN_DIRS}${_END}.
${CODE}make clean-code${_END}         # Delete temporary artifacts under ${CODE}CLEAN_CODE_DIRS${_END} = ${CODE}${CLEAN_CODE_DIRS}${_END}.

${NOTE_LABEL}
Use the ${CODE}clean${_END} and ${CODE}clean-code${_END} targets with caution, since they both delete the ${CODE}OUTPUT_CODE_DIR${_END} 
content, which can take a ${RED}LOT${_END} of compute to generate due to the inference involved!

${help-top-level-message}
endef


.PHONY: all help help-general help-command-not-installed print-info clean clean-code
all:: help print-info

clean::
	rm -rf ${CLEAN_DIRS}

clean-code::
	rm -rf ${CLEAN_CODE_DIRS}

help:: help-general 
	@true
help-general::
	$(info )
	$(info ${help-message-general})

# NOTE: help-command-% must be defined BEFORE help-% or it is ignored!
help-command-%::
	$(info ${INFO_LABEL}Help on ${CODE}${@:help-command-%=%}${_END}:)
	$(info ${${@}-message})
	$(info ${INFO_LABEL})
	$(info ${INFO_LABEL}(If no help is shown, then none is defined for ${CODE}${@:help-command-%=%}${_END} in this Makefile.))
	@true

help-command-no-message::
	$(warning ${WARNING_LABEL}Sorry, no built-in help is available for CLI command '${CODE}${CMD}${_END}'.")
	@true


help-%::
	$(info )
	$(info ${${@}-message})
	$(info )
	@true

help-command-not-installed::
	$(info ${WARNING_LABEL}Command ${CODE}${CMD}${_END} is not installed.)
	@true

.PHONY: error
error::
	@$(info ${ERROR_LABEL}${MSG} (exit status = ${RED}${STATUS}${_END}))
	@$(info ${${MSG_VARIABLE}})
	@$(error )

define command-failed-error-message
${ERROR_LABEL}${MSG} (exit status = ${RED}${STATUS}${_END})!!
endef

define command-check-failed-message
${TIP_LABEL}Installation help may be defined in this Makefile. Try ${CODE}make help-command-${CMD}${_END} 
${TIP_LABEL}or try ${CODE}make install-${CMD}${_END}. See also the project's ${CODE}README.md${_END}.
endef

# Check if a command is on the path.
command-check-%:
	@CMD=${@:command-check-%=%} && command -v $$CMD > /dev/null || \
		${MAKE} CMD=$$CMD MSG="Command ${CODE}$$CMD${_END} not found! It is required for a make target." MSG_VARIABLE=command-check-failed-message STATUS=1 error

silent-command-check-%:
	cmd=${@:silent-command-check-%=%} && echo $$cmd && command -v $$cmd > /dev/null

# A default definition of a potentially useful message. Override when needed with
# override define help-custom-targets-message
# ...
# endef
define help-custom-targets-message
  ${NOTE}No custom targets defined.${_END}
endef

.PHONY: print-info-env
print-info:: print-info-env
print-info-env::
	@echo "${HIGHLIGHT}Some 'environment' settings:${_END}"
	@echo
	@echo "  ${DARK_GREEN}MAKEFLAGS:${_END}             ${CODE}${MAKEFLAGS}${_END}"
	@echo "  ${DARK_GREEN}MAKEFLAGS_RECURSIVE:${_END}   ${CODE}${MAKEFLAGS_RECURSIVE}${_END}"
	@echo "  ${DARK_GREEN}UNAME:${_END}                 ${CODE}${UNAME}${_END}"
	@echo "  ${DARK_GREEN}ARCHITECTURE:${_END}          ${CODE}${ARCHITECTURE}${_END}"
	@echo "  ${DARK_GREEN}MODEL_APPENDIX:${_END}        ${CODE}${MODEL_APPENDIX}${_END}"
	@echo "  ${DARK_GREEN}TIMESTAMP:${_END}             ${CODE}${TIMESTAMP}${_END}"
	@echo "  ${DARK_GREEN}REPO_NAME:${_END}             ${CODE}${REPO_NAME}${_END}"
	@echo "  ${DARK_GREEN}GIT_HASH:${_END}              ${CODE}${GIT_HASH}${_END}"
	@echo "  ${DARK_GREEN}PWD:${_END}                   ${CODE}${PWD}${_END} (current Directory)"
	@echo "  ${DARK_GREEN}SRC_DIR:${_END}               ${CODE}${SRC_DIR}${_END}"
	@echo "  ${DARK_GREEN}WHICH_TESTS:${_END}           ${CODE}${WHICH_TESTS}${_END}"
	@echo

# The idiom of targets named "*-default" is an override hook. They are declared here
# with a single colon (:), so Makefiles can define their own recipe for the "core" of
# the corresponding targets, e.g., before-pr, pylint, tests, etc.

.PHONY: before-pr before-pr-default before-pr-no-tests

before-pr:: before-pr-default
before-pr-default: before-pr-no-tests tests
before-pr-no-tests:: ${QUALITY_CHECKS}

.PHONY: tests unit-tests unit-tests-prerequisite unit-tests-default unit-tests-postrequisite
.PHONY: format format-prerequisite format-default format-postrequisite
.PHONY: ruff ruff-prerequisite ruff-default ruff-postrequisite
.PHONY: pylint pylint-prerequisite pylint-default pylint-postrequisite
.PHONY: type-check type-check-prerequisite type-check-default type-check-postrequisite
.PHONY: type-check-watch type-check-watch-default
.PHONY: lint

tests:: unit-tests
unit-tests:: unit-tests-prerequisite unit-tests-default unit-tests-postrequisite
unit-tests-prerequisite unit-tests-postrequisite::
unit-tests-default:
	@echo "${INFO_LABEL}Target ${CODE}unit-tests${_END}: Running the unit tests (with coverage): ${CODE}${WHICH_TESTS}${_END}:"
	@echo "${INFO_LABEL}Running: ${CODE}${PYTEST_RUN_CMD} ${WHICH_TESTS}${_END}:"
	${PYTEST_RUN_CMD} ${WHICH_TESTS}
	@echo "${INFO_LABEL}Running: ${CODE}${PYTEST_COV_REPORT_CMD}${_END}:"
	${PYTEST_COV_REPORT_CMD}

# Convenient short hand for the two linters.
lint:: ruff pylint

format:: format-prerequisite format-default format-postrequisite
format-prerequisite format-postrequisite::
format-default:
	@echo "${INFO_LABEL}Target ${CODE}format${_END}: Running ${CODE}black${_END} on the code in ${CODE}${SRC_DIR}${_END}."
	uv run black ${SRC_DIR}

ruff:: ruff-prerequisite ruff-default ruff-postrequisite
ruff-prerequisite ruff-postrequisite::
ruff-default:
	@echo "${INFO_LABEL}Target ${CODE}ruff${_END}: Running ${CODE}ruff${_END} to lint the code in ${CODE}${SRC_DIR}${_END}."
	uv run ruff check --fix ${SRC_DIR}

pylint:: pylint-prerequisite pylint-default pylint-postrequisite
pylint-prerequisite pylint-postrequisite::
pylint-default:
	@echo "${WARNING_LABEL}The ${CODE}pylint${_END} target is currently not passing, so it is disabled. See the repo issue #165."

pylint-default-save:
	@echo "${INFO_LABEL}Target ${CODE}pylint${_END}: Running ${CODE}pylint${_END} on the code in ${CODE}${SRC_DIR}${_END} (configuration in ${CODE}pylintrc.toml${_END})"
	uv run pylint ${PYLINT_IGNORE_ARGS} ${SRC_DIR}

type-check:: type-check-prerequisite type-check-default type-check-postrequisite
type-check-prerequisite type-check-postrequisite::
type-check-default:
	@echo "${INFO_LABEL}Target ${CODE}type-check${_END}: Running ${CODE}ty${_END} to type check the code in ${CODE}${SRC_DIR}${_END}."
	uv run ty check ${SRC_DIR}

type-check-watch:: type-check-prerequisite type-check-watch-default type-check-postrequisite
type-check-watch-default:
	@echo "${INFO_LABEL}Target ${CODE}type-check-watch${_END}: Running ${CODE}ty${_END} to type check the code in ${CODE}${SRC_DIR}${_END} using 'watch' mode."
	uv run ty check --watch ${SRC_DIR}

.PHONY: one-time-setup clean-setup uninstall-uv 
.PHONY: command-check-uv install-uv uv-venv install-dev-dependencies 

setup one-time-setup:: install-uv uv-venv install-dev-dependencies

clean-setup:: uninstall-uv

install-%::
	@cmd=${@:install-%=%} && command -v $$cmd > /dev/null && \
		echo "${INFO_LABEL}command ${CODE}$$cmd${_END} is already installed." || ${MAKE} CMD=$$cmd help-command-not-installed help-command-$$cmd

uv-venv:: command-check-uv
	@test -d .venv && echo "${INFO}Directory ${CODE}.venv${_END} already exists; not running ${CODE}uv venv${_END}." || uv venv
	@echo "${TIP_LABEL}run ${CODE}source .venv/bin/activate${_END} if subsequent commands fail!"

install-dev-dependencies::
	uv pip install -e ".[dev]"

uninstall-uv:: 
	$(info ${help-command-${@}-message})
	@true

command-check-uv::
	@command -v uv > /dev/null || ! ${MAKE} help-command-uv

install-jq:: help-command-jq

%-error:
	$(info ${ERROR}${@} - Error ${_END})
	$(error ${${@}-message})

define help-command-uv-message
${INFO_LABEL}The Python environment management tool ${CODE}uv${_END} is required.
${INFO_LABEL}See ${CODE}https://docs.astral.sh/uv/${_END} for installation instructions.
endef

define help-command-uninstall-uv-message
${WARNING_LABEL}You have to uninstall ${CODE}uv${_END} manually.
${INFO_LABEL}If you used HomeBrew to install it, use ${CODE}brew uninstall uv${_END}. 
${INFO_LABEL}Otherwise, if you executed one of the installation commands from
${INFO_LABEL}${CODE}https://docs.astral.sh/uv/${_END}, find the installation location and delete it.
endef

help-command-uvx-message = ${help-command-uv-message}

define help-command-jq-message
${INFO_LABEL}The CLI command ${CODE}jq${_END} is useful, but not required, for processing JSON file.
${INFO_LABEL}See ${CODE}https://jqlang.org/download/${_END} for installation instructions.
endef

define help-command-node-message
${INFO_LABEL}The JavaScript runtime ${CODE}node${_END} is required if you want to use the MCP server
${INFO_LABEL}inspector ${CODE}@modelcontextprotocol/inspector${_END}. Otherwise, node is not used in
${INFO_LABEL}this project. See ${CODE}https://nodejs.org/en/download/${_END} for installation instructions.
endef

open-url-message = ${TIP_LABEL}Try ${CODE}⌘+click${_END} or ${CODE}^+click${_END} on the URL.
