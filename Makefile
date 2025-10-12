# Makefile for the ai-application-testing website and repo example code.

# Definitions for the example code.
INFERENCE_SERVICE     ?= ollama
INFERENCE_URL         ?= http://localhost:11434
MODEL                 ?= ollama/gpt-oss:20b
MODEL_FILE_NAME       ?= $(subst :,_,${MODEL}) # Covert any ':' to '_'.
SRC_DIR               ?= src
PROMPTS_TEMPLATES_DIR ?= ${SRC_DIR}/prompts/templates
TEMP_DIR              ?= temp
OUTPUT_DIR            ?= ${TEMP_DIR}/output/${MODEL_FILE_NAME}
OUTPUT_LOGS_DIR       ?= ${OUTPUT_DIR}/logs
OUTPUT_DATA_DIR       ?= ${OUTPUT_DIR}/data
EXAMPLE_DATA          ?= ${SRC_DIR}/data/examples/${MODEL_FILE_NAME}
CLEAN_CODE_DIRS       ?= ${OUTPUT_DIR}
TIME                  ?= time  # time execution of long processes

## One way to prevent execution of scripts is to invoke make this way:
## NOOP=echo make foobar
## Another way is `make -n targets`.
NOOP                  ?=

# Definitions for the website.
PAGES_URL             ?= https://the-ai-alliance.github.io/ai-application-testing/
DOCS_DIR              ?= docs
SITE_DIR              ?= ${DOCS_DIR}/_site
CLEAN_DOCS_DIRS       ?= ${SITE_DIR} ${DOCS_DIR}/.sass-cache

## Override when running `make view-local` using e.g., `JEKYLL_PORT=8000 make view-local`
JEKYLL_PORT           ?= 4000

# Other Environment variables
MAKEFLAGS              = -w  # --warn-undefined-variables
MAKEFLAGS_RECURSIVE   ?= # --print-directory (only useful for recursive makes...)
UNAME                 ?= $(shell uname)
ARCHITECTURE          ?= $(shell uname -m)
TIMESTAMP             ?= $(shell date +"%Y%m%d-%H%M%S")
## Used for version tagging release artifacts.
GIT_HASH              ?= $(shell git show --pretty="%H" --abbrev-commit |head -1)

define help_message

Quick help for this make process. 

Try these more specific help targets:

make help-docs          # Help on the website targets.
make help-code          # Help on the example code targets.

make print-info         # Print the current values of some make and env. variables.

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

Quick help for this make process for the tools described in this website.
For the tools used to manage the website, see the parent directory Makefile.

make all-code           # Clean and run all the tools.
make run-code           # Run all the tools without cleaning first.

make setup              # One-time setup tasks; e.g., builds target install-uv.
make one-time-setup     # Synonym for "setup".
make install-uv         # Explain how to install "uv".
                        # Run "make help-uv" for more information.

make clean-code         # Remove build artifacts in ${OUTPUT_DIR}.
make clean-all-code     # Remove ALL build artifacts for all models in ${TEMP_DIR}.
make clean-temp         # Synonym for "clean-all-code".
make clean-setup        # Undoes everything done by the setup target or provides
                        # instructions for what you must do manually in some cases.
make clean-uv           # Explain how to uninstall "uv".

For scripts run by the following targets, which invoke inference, ${MODEL} 
served by ollama is used by default. The make variable MODEL specifies the
model, so if you want to use a different model, invoke make as in this example:

  MODEL=ollama/llama3.2:3B make run-tdd-example-refill-chatbot

All these "run-*" targets may run setup dependencies that are redundant most of the time,
but easy to forgot when important!

make terc run-terc      # Shorthands for the run-tdd-example-refill-chatbot target.
make run-tdd-example-refill-chatbot   
                        # Run the code for the TDD example "unit benchmark".
                        # See the TDD chapter in the website for details.

make ubds run-ubds      # Shorthands for the run-unit-benchmark-data-synthesis target.
make run-unit-benchmark-data-synthesis
                        # Run the code for "unit benchmark" data synthesis.
                        # See the Unit Benchmark chapter in the website for details.

make ubdv run-ubdv      # Shorthands for the run-unit-benchmark-data-validation target.
make run-unit-benchmark-data-validation
                        # Run the code for validating the synthetic data for the unit benchmarks.
                        # See the Unit Benchmark chapter in the website for details.

Miscellaneous tasks for help, debugging, setup, etc.

make help-code          # Prints this output.

The "uv" CLI tool is required:

make help-uv            # Prints specific information about "uv", including installation.

make save-examples      # Copy run output and data files for MODEL=${MODEL} 
                        # to ${EXAMPLE_DATA}.

endef

define help_message_uv

The Python environment management tool "uv" is required.
See https://docs.astral.sh/uv/ for installation instructions.

If you want to uninstall uv and you used HomeBrew to install it,
use 'brew uninstall uv'. Otherwise, if you executed one of the
installation commands on the website above, find the installation
location and delete uv.

endef

ifndef DOCS_DIR
$(error ERROR: There is no ${DOCS_DIR} directory!)
endif
ifndef SRC_DIR
$(error ERROR: There is no ${SRC_DIR} directory!)
endif

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

.PHONY: help help-docs help-code help-uv

all:: help

help::
	$(info ${help_message})
	@echo

help-docs help-code help-uv::
	$(info ${help_message_${@:help-%=%}})
	@echo

.PHONY: print-info print-info-docs print-info-code print-info-env

print-info:: print-info-docs print-info-code print-info-env 
print-info-docs::
	@echo "For the GitHub Pages website:"
	@echo "  GitHub Pages URL:      ${PAGES_URL}"
	@echo "  current dir:           ${PWD}"
	@echo "  docs dir:              ${DOCS_DIR}"
	@echo "  site dir:              ${SITE_DIR}"
	@echo "  JEKYLL_PORT:           ${JEKYLL_PORT}"
	@echo

print-info-code::
	@echo "For the code examples:"
	@echo "  model:                 ${MODEL}"
	@echo "  inference service:     ${INFERENCE_SERVICE}"
	@echo "  prompt templates dir:  ${PROMPTS_TEMPLATES_DIR}"
	@echo "  output dir:            ${OUTPUT_DIR}"
	@echo "  output data dir:       ${OUTPUT_DATA_DIR}"
	@echo "  example data dir:      ${EXAMPLE_DATA}"
	@echo "  src dir:               ${SRC_DIR}"
	@echo

print-info-env::
	@echo "The environment:"
	@echo "  GIT_HASH:              ${GIT_HASH}"
	@echo "  TIMESTAMP:             ${TIMESTAMP}"
	@echo "  MAKEFLAGS:             ${MAKEFLAGS}"
	@echo "  MAKEFLAGS_RECURSIVE:   ${MAKEFLAGS_RECURSIVE}"
	@echo "  UNAME:                 ${UNAME}"
	@echo "  ARCHITECTURE:          ${ARCHITECTURE}"
	@echo "  GIT_HASH:              ${GIT_HASH}"

# Docs Targets

.PHONY: all-docs clean-docs
.PHONY: view-pages view-local setup-jekyll run-jekyll

all-docs:: clean-docs view-local

clean-docs::
	rm -rf ${CLEAN_DOCS_DIRS}   

view-pages::
	@python -m webbrowser "${PAGES_URL}" || \
		(echo "ERROR: I could not open the GitHub Pages URL, ${PAGES_URL}. Try ⌘-click or ^-click on this URL instead:" && \
		 exit 1 ): 
view-local:: setup-jekyll run-jekyll

# Passing --baseurl '' allows us to use `localhost:4000` rather than require
# `localhost:4000/The-AI-Alliance/ai-application-testing` when running locally.
run-jekyll: clean-docs
	@echo
	@echo "Once you see the http://127.0.0.1:${JEKYLL_PORT}/ URL printed, open it with command+click..."
	@echo
	cd ${DOCS_DIR} && bundle exec jekyll serve --port ${JEKYLL_PORT} --baseurl '' --incremental || ( echo "ERROR: Failed to run Jekyll. Try running 'make setup-jekyll'." && exit 1 )

setup-jekyll:: ruby-installed-check bundle-ruby-command-check
	@echo "Updating Ruby gems required for local viewing of the docs, including jekyll."
	gem install jekyll bundler jemoji || ${MAKE} gem-error
	bundle install || ${MAKE} bundle-error
	bundle update html-pipeline || ${MAKE} bundle-error

# Code Targets

.PHONY: all-code run-code clean-code clean-all-code clean-temp
.PHONY: run-terc run-tdd-example-refill-chatbot 
.PHONY: run-ubds run-unit-benchmark-data-synthesis 
.PHONY: run-ubdv run-unit-benchmark-data-validation 
.PHONY: before-run save-examples

all-code:: clean-code run-code
run-code:: run-tdd-example-refill-chatbot run-unit-benchmark-data-synthesis run-unit-benchmark-data-validation run-unit-benchmark-data-validation 

clean-code::
	rm -rf ${CLEAN_CODE_DIRS}   

clean-all-code clean-temp::
	rm -rf ${TEMP_DIR}

define run-tdd-example-refill-chatbot-message
*** Running the TDD example.
endef
define run-unit-benchmark-data-synthesis-message
*** Running the unit benchmark data synthesis example.
endef
define run-unit-benchmark-data-validation-message
*** Running the unit benchmark synthetic data validation example.
endef
	
terc run-terc:: run-tdd-example-refill-chatbot
ubds run-ubds:: run-unit-benchmark-data-synthesis
ubdv run-ubdv:: run-unit-benchmark-data-validation

run-tdd-example-refill-chatbot run-unit-benchmark-data-synthesis run-unit-benchmark-data-validation:: before-run
	$(info ${$@-message})
	${NOOP} ${TIME} uv run ${SRC_DIR}/scripts/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${PROMPTS_TEMPLATES_DIR} \
		--output ${OUTPUT_DIR}/${@:run-%=%}.out \
		--data ${OUTPUT_DATA_DIR}

before-run:: uv-command-check ${OUTPUT_DIR} ${OUTPUT_DATA_DIR}  
	$(info NOTE: If errors occur, try 'make setup' or 'make clean-setup setup', then try again.)

${TEMP_DIR} ${OUTPUT_DIR} ${OUTPUT_DATA_DIR}::
	mkdir -p $@

save-examples::
	@echo "Saving example output and data files for model ${MODEL}:"
	rm -rf ${EXAMPLE_DATA}
	mkdir -p $$(dirname ${EXAMPLE_DATA})
	cp -r ${OUTPUT_DIR} ${EXAMPLE_DATA}

.PHONY: one-time-setup setup clean-setup 
.PHONY: clean-uv clean-llm-templates 
.PHONY: install-uv uv-venv

setup one-time-setup:: install-uv uv-venv

clean-setup:: clean-uv

clean-uv:: 
	@echo "You have to uninstall ${@:clean-%=%} manually:"
	@echo
	$(info ${help_message_${@:clean-%=%}})

install-uv:: 
	@cmd=${@:install-%=%} && command -v $$cmd > /dev/null && \
		echo "$$cmd is already installed" || ${MAKE} help-$$cmd

uv-venv:: uv-command-check 
	uv venv

%-error:
	$(error ${${@}-message})

ruby-installed-check:
	@command -v ruby > /dev/null || \
		( echo "ERROR: ${ruby_and_gem_required_message}" && exit 1 )
	@command -v gem  > /dev/null || \
		( echo "ERROR: ${gem_required_message}" && exit 1 )

%-ruby-command-check:
	@command -v ${@:%-ruby-command-check=%} > /dev/null || \
		( echo "ERROR: Ruby command/gem ${@:%-ruby-command-check=%} ${missing_ruby_gem_or_command_error_message}" && \
			exit 1 )

%-command-check:
	@cmd=${@:%-command-check=%} && command -v $$cmd > /dev/null || \
		( echo "ERROR: shell command \"$$cmd\" is required. Try \"make one-time-setup\", which may be able to install it." && \
		  echo "       or run \"make help\", \"make help-$$cmd\", and see the project's README.md for more information." && \
			exit 1 )

# The rest of this Makefile includes some convenience targets for working 
# with the "llm" CLI tool. See the Appendix in the README.md for details.

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
	@echo "** NOTE: ** clean-llm-templates was already executed to uninstall our templates."
	@echo

clean-llm-templates::
	@cd ${PROMPTS_TEMPLATES_DIR} && \
		llmdir="$$(llm templates path)" && \
		for t in *.yaml; do echo "removing: $$llmdir/$$t"; rm -f "$$llmdir/$$t"; done && \
		ls -l "$$llmdir"

install-llm:: help-llm install-llm-templates
	@echo
	@echo "** NOTE: ** install-llm-templates was already executed to install our templates."
	@echo

install-llm-templates:: llm-command-check
	@llmdir="$$(llm templates path)" && \
	echo "Installing the llm templates from ${PROMPTS_TEMPLATES_DIR} into $$llmdir" && \
	cp ${PROMPTS_TEMPLATES_DIR}/*.yaml "$$llmdir" && \
	ls -l "$$llmdir"

