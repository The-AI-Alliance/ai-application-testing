# .common.mk
# See comment at the bottom of this file about "-include .custom.mk".

# Definitions of RED, GREEN, etc., and INFO, ERROR, etc. for console output.
# To see them in action, try "make show-colors".
include .console-colors.mk

# Some of the following definitions may be overridden in Makefile.
# OUTPUT_TEST_DIR: Where test output is written. RELATIVE to ${PWD}, NOT ${SRC_DIR}.
SRC_DIR               ?= src
TESTS_DIR             ?= ${SRC_DIR}/tests
OUTPUT_DIR            ?= ${PWD}/output
OUTPUT_TEST_DIR       ?= ${OUTPUT_DIR}/tests
OUTPUT_LOGS_ROOT_DIR  ?= ${OUTPUT_DIR}/logs
OUTPUT_LOGS_DIR       ?= ${OUTPUT_LOGS_ROOT_DIR}/${TIMESTAMP}
CLEAN_CODE_DIRS       := ${OUTPUT_DIR} ${OUTPUT_TEST_DIR}
CLEAN_DIRS            += ${CLEAN_CODE_DIRS}

QUALITY_CHECKS        := format ruff pylint type-check tests
PYLINT_IGNORE_ARGS    := --ignore=.venv --ignore-pattern='.*cache.*'

PYTEST_RUN_CMD        := uv run --active coverage run -m pytest -q -v -s
PYTEST_COV_REPORT_CMD := uv run --active coverage report -m

# The environment
LOCAL_REPO_PATH       ?= $(shell git rev-parse --show-toplevel)
REPO_NAME             ?= $(notdir ${LOCAL_REPO_PATH})
MAKEFLAGS             ?= --warn-undefined-variables
MAKEFLAGS_RECURSIVE   ?= # --print-directory (only useful for recursive makes...)
UNAME                 ?= $(shell uname)
ARCHITECTURE          ?= $(shell uname -m)

# Used for version tagging release artifacts.
GIT_HASH              ?= $(shell git show --pretty="%H" --abbrev-commit |head -1)
TIMESTAMP             ?= $(shell date +"%Y%m%d-%H%M%S")

# Time execution
TIME                  ?= time  # time execution of long processes

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
${CODE}make tests${_END}              # Run the test suite.
${CODE}make clean${_END}              # Remove built artifacts, etc.
${CODE}make format${_END}             # Format the Python code with ${CODE}black${_END}.
${CODE}make lint${_END}               # Lint the Python code by making the ${CODE}ruff${_END} and ${CODE}pylint${_END} targets.
${CODE}make ruff${_END}               # Lint the Python code with ${CODE}ruff${_END}.
${CODE}make pylint${_END}             # Lint the Python code with ${CODE}pylint${_END}.
${CODE}make type-check${_END}         # Type check the Python code with ${CODE}ty${_END}.
${CODE}make type-check-watch${_END}   # Type check the Python code with ${CODE}ty${_END} in "watch" mode,
${CODE}${_END}                        # so you can fix mistakes and keep it updating.
${CODE}make before-pr${_END}          # Make ${CODE}format${_END}, ${CODE}lint${_END}, ${CODE}type-check${_END}, and ${CODE}tests${_END} for "src" AND
${CODE}${_END}                        # every "contrib" directory.
${CODE}${_END}                        # DO THIS BEFORE SUBMITTING A PR!
${CODE}make clean${_END}              # Delete temporary artifacts under ${CODE}CLEAN_DIRS${_END} = ${CODE}${CLEAN_DIRS}${_END}.
${CODE}make clean-code${_END}         # Delete temporary artifacts under ${CODE}CLEAN_CODE_DIRS${_END} = ${CODE}${CLEAN_CODE_DIRS}${_END}.

${NOTE_LABEL}
Use the ${CODE}clean${_END} and ${CODE}clean-code${_END} targets with caution, since they both delete the ${CODE}OUTPUT_CODE_DIR${_END} 
content, which can take a ${RED}LOT${_END} of compute to generate due to the inference involved!

${help-top-level-message}
endef


.PHONY: all help help-general print-info clean clean-code
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
	$(info ${${@}-message})
	$(info )
	$(info ${INFO_LABEL}If no help is shown, then none is defined for ${CODE}${@:help-command-%=%}${_END} in this Makefile.)
	@true

help-command-no-message::
	$(warning ${WARNING_LABEL}Sorry, no built-in help is available for CLI command '${CODE}${CMD}${_END}'.")
	@true


help-%::
	$(info )
	$(info ${${@}-message})
	$(info )
	@true

error::
	@$(info ${ERROR_LABEL}${MSG} (exit status = ${RED}${STATUS}${_END}))
	@$(info ${${MSG_VARIABLE}})
	@$(error )

define command-failed-error-message
${ERROR_LABEL}${MSG} (exit status = ${RED}${STATUS}${_END})!!
endef

define command-check-failed-message
${TIP_LABEL}Installation help may be defined in this Makefile. Try ${CODE}make help-command-${CMD}${_END} 
${TIP_LABEL}or try ${CODE}make install-${CMD}${_END}.
${TIP_LABEL}See also the project's ${CODE}README.md${_END}.
endef

# Check if a command is on the path.
command-check-%:
	@CMD=${@:command-check-%=%} && command -v $$CMD > /dev/null || \
		${MAKE} CMD=$$CMD MSG="Command ${CODE}$$CMD${_END} not found! It is required for a make target." MSG_VARIABLE=command-check-failed-message STATUS=1 error

silent-command-check-%:
	cmd=${@:silent-command-check-%=%} && echo $$cmd && command -v $$cmd > /dev/null

define help-custom-targets-message
  ${NOTE}No custom targets defined.${_END}
endef

.PHONY: print-info-env
print-info:: print-info-env
print-info-env::
	@echo "${HIGHLIGHT}Some 'environment' settings:${_END}"
	@echo "  ${DARK_GREEN}MAKEFLAGS:${_END}           ${CODE}${MAKEFLAGS}${_END}"
	@echo "  ${DARK_GREEN}MAKEFLAGS_RECURSIVE:${_END} ${MAKEFLAGS_RECURSIVE}"
	@echo "  ${DARK_GREEN}UNAME:${_END}               ${CODE}${UNAME}${_END}"
	@echo "  ${DARK_GREEN}ARCHITECTURE:${_END}        ${CODE}${ARCHITECTURE}${_END}"
	@echo "  ${DARK_GREEN}TIMESTAMP:${_END}           ${CODE}${TIMESTAMP}${_END}"
	@echo "  ${DARK_GREEN}REPO_NAME:${_END}           ${CODE}${REPO_NAME}${_END}"
	@echo "  ${DARK_GREEN}GIT_HASH:${_END}            ${CODE}${GIT_HASH}${_END}"
	@echo "  ${DARK_GREEN}PWD:${_END}                 ${CODE}${PWD}${_END} (current Directory)"
	@echo "  ${DARK_GREEN}SRC_DIR:${_END}             ${CODE}${SRC_DIR}${_END}"
	@echo "  ${DARK_GREEN}TESTS_DIR:${_END}           ${CODE}${TESTS_DIR}${_END}"
	@echo

.PHONY: before-pr do-before-pr

before-pr:: do-before-pr
do-before-pr:: ${QUALITY_CHECKS}

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
	@echo "${INFO_LABEL} $@: Running the unit tests (with coverage) in ${CODE}${SRC_DIR}/tests${_END}:"
	@if [ ! -d "${SRC_DIR}/tests" ]; then echo "${WARN_LABEL} No test directory ${CODE}${SRC_DIR}/tests${_END} found!"; \
	else \
		cd ${SRC_DIR}; \
		echo "${INFO_LABEL} Running: ${CODE}${PYTEST_RUN_CMD} && ${PYTEST_COV_REPORT_CMD}${_END}"; \
		${PYTEST_RUN_CMD} && ${PYTEST_COV_REPORT_CMD}; \
	fi

# Convenient short hand for the two linters.
lint:: ruff pylint

format:: format-prerequisite format-default format-postrequisite
format-prerequisite format-postrequisite::
format-default:
	@echo "${INFO_LABEL} $@: Running ${CODE}black${_END} on the code in ${CODE}${SRC_DIR}${_END}."
	uv run black ${SRC_DIR}

ruff:: ruff-prerequisite ruff-default ruff-postrequisite
ruff-prerequisite ruff-postrequisite::
ruff-default:
	@echo "${INFO_LABEL} $@: Running ${CODE}ruff${_END} to lint the code in ${CODE}${SRC_DIR}${_END}."
	uv run ruff check --fix ${SRC_DIR}

pylint:: pylint-prerequisite pylint-default pylint-postrequisite
pylint-prerequisite pylint-postrequisite::
pylint-default:
	@echo "${INFO_LABEL} $@: Running ${CODE}pylint${_END} on the code in ${CODE}${SRC_DIR}${_END} (configuration in ${CODE}pylintrc.toml${_END})"
	uv run pylint ${PYLINT_IGNORE_ARGS} ${SRC_DIR}

type-check:: type-check-prerequisite type-check-default type-check-postrequisite
type-check-prerequisite type-check-postrequisite::
type-check-default:
	@echo "${INFO_LABEL} $@: Running ${CODE}ty${_END} to type check the code in ${CODE}${SRC_DIR}${_END}."
	uv run ty check ${SRC_DIR}

type-check-watch:: type-check-prerequisite type-check-watch-default type-check-postrequisite
type-check-watch-default:
	@echo "${INFO_LABEL} $@: Running ${CODE}ty${_END} to type check the code in ${CODE}${SRC_DIR}${_END} using 'watch' mode."
	uv run ty check --watch ${SRC_DIR}

.PHONY: one-time-setup clean-setup uninstall-uv 
.PHONY: command-check-uv install-uv uv-venv install-dev-dependencies install-requirements-txt-dependencies

setup one-time-setup:: install-uv uv-venv install-dev-dependencies

clean-setup:: uninstall-uv

install-%::
	@cmd=${@:install-%=%} && command -v $$cmd > /dev/null && \
		echo "${INFO_LABEL}command ${CODE}$$cmd${_END} is already installed." || ${MAKE} help-command-$$cmd

uv-venv:: command-check-uv
	@test -d .venv && echo "${INFO}Directory ${CODE}.venv${_END} already exists; not running ${CODE}uv venv${_END}." || uv venv
	@echo "${TIP_LABEL}run ${CODE}source .venv/bin/activate${_END} if subsequent commands fail!"

install-dev-dependencies::
	uv pip install -e ".[dev]"

uninstall-uv:: 
	$(info ${help_message_${@:uninstall-%=%}})
	@echo "${WARNING}You have to uninstall ${@:uninstall-%=%} manually.${_END}"

# This target exists to support contributions that have a custom requirements.txt file
# that needs to be used for local setup. Otherwise, it isn't used by the main uv process.
install-requirements-txt-dependencies::
	uv pip install --requirements requirements.txt

command-check-uv::
	@command -v uv > /dev/null || ! ${MAKE} help-command-uv

install-jq:: help-command-jq

%-error:
	$(info ${ERROR}${@} - Error ${_END})
	$(error ${${@}-message})

define help-command-uv-message
${INFO_LABEL}The Python environment management tool ${CODE}uv${_END} is required.
${INFO_LABEL}See ${CODE}https://docs.astral.sh/uv/${_END} for installation instructions.
${INFO_LABEL}
${INFO_LABEL}If you want to uninstall uv and you used HomeBrew to install it,
${INFO_LABEL}use ${CODE}brew uninstall uv${_END}. Otherwise, if you executed one of the
${INFO_LABEL}installation commands on the website above, find the installation
${INFO_LABEL}location and delete uv.
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
