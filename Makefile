# Makefile for the ai-application-testing website and repo example code.

# Definitions for the example code.
INFERENCE_SERVICE     ?= ollama
INFERENCE_URL         ?= http://localhost:11434
MODEL                 ?= ollama/gpt-oss:20b
SRC_DIR               ?= src
PROMPT_TEMPLATES_DIR  ?= ${SRC_DIR}/llm/templates
TEMP_DIR              ?= temp
OUTPUT_DIR            ?= ${TEMP_DIR}/output
OUTPUT_DATA_DIR       ?= ${OUTPUT_DIR}/data
EXAMPLE_DATA          ?= ${SRC_DIR}/data/examples
CLEAN_CODE_DIRS       ?= ${TEMP_DIR}

## One way to prevent execution of scripts is to invoke make this way:
## NOOP=echo make foobar
## Another way is `make -n targets`.
NOOP                  ?=

LLM_TEMPLATES_LIB_DIR ?= $(shell llm templates path)
ifeq ($(LLM_TEMPLATES_LIB_DIR),)
LLM_TEMPLATES_LIB_DIR := $$HOME/Library/Application Support/io.datasette.llm/templates (on MacOS)
endif

# Definitions for the website.
PAGES_URL             ?= https://the-ai-alliance.github.io/ai-application-testing/
DOCS_DIR              ?= ../docs
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
make clean-code         # Remove build artifacts, etc., such as outputs in ${OUTPUT_DIR}

make one-time-setup     # Synonym for the setup target...
make setup              # One-time setup tasks; builds target install-llm, which
                        # builds install-templates.
make install-uv         # Explain how to install "uv".
                        # Run "make help-uv" for more information.
make install-llm        # pip install "llm" and dependencies. Also makes install-templates.
                        # Run "make help-llm" for more information.
make install-templates  # Install our llm "templates" into llm. See also the "run-*" targets.
make install-jq         # Explain how to install "jq".
                        # Run "make help-jq" for more information.

make clean-setup        # Undoes everything done by the setup target or provides
                        # instructions for what to do manually in some cases.
make clean-uv           # Explain how to uninstall "uv".
make clean-llm          # pip uninstall "llm" and dependencies. Also makes clean-templates.
make clean-templates    # Remove our llm "templates" from llm.
make clean-jq           # Explain how to uninstall "jq".

For scripts run by the following targets, which invoke inference, ${MODEL} served by
ollama is used, by default. To specify a different model, invoke make as in this example:

  MODEL=llama3.2:3B make run-tdd-example-refill-chatbot

"llm" will interpret the model name to invoke the correct service.

All these "run-*" targets have install-templates as a dependency, because it would be easy
to forgot to build this target if you edit a template and this step is trivial to run, so
we just do it every time...

make run-terc           # Shorthand for the run-tdd-example-refill-chatbot target.
make run-tdd-example-refill-chatbot   
                        # Run the code for the TDD example "unit benchmark".
                        # See the TDD chapter in the website for details.

make run-ubds           # Shorthand for the run-unit-benchmark-data-synthesis target.
make run-unit-benchmark-data-synthesis
                        # Run the code for "unit benchmark" data synthesis.
                        # See the Unit Benchmark chapter in the website for details.

make run-ubdv           # Shorthand for the run-unit-benchmark-data-validation target.
make run-unit-benchmark-data-validation
                        # Run the code for validating the synthetic data for the "unit benchmark".
                        # See the Unit Benchmark chapter in the website for details.

Miscellaneous tasks for help, debugging, setup, etc.

make help               # Prints this output.

The "uv", "llm", and "jq" CLI tools are required:

make help-uv            # Prints specific information about "uv", including installation.
make help-llm           # Prints specific information about "llm", including installation.
make help-jq            # Prints specific information about "jq", including installation.

endef

define help_message_uv
The Python environment management tool "uv" is required.
See https://docs.astral.sh/uv/ for installation instructions.

If you want to uninstall uv and used HomeBrew to install it,
use 'brew uninstall uv'. Otherwise, if you executed one of the
installation commands on the website above, find the installation
location and delete uv.

endef

define help_message_llm
The "llm" CLI is used by many of the tools here. For more details, see:
  https://github.com/simonw/llm

You can install llm using make:
  make install-llm

If you want to serve models locally using "ollama", see the installation instructions:
  https://ollama.com 

Also install the llm plugin using the llm CLI:
  llm install llm-ollama

The tools also use several llm "templates". These need to be installed into:
  ${LLM_TEMPLATES_LIB_DIR}

Use the following make command to do this:
  make install-templates 

WARNING: If you edit the templates in ${PROMPT_TEMPLATES_DIR}, rerun  
  make install-templates 

If you want to uninstall llm, use "make clean-llm".

endef

define help_message_jq
The "jq" CLI is used by some tools for parsing JSON. For more details, see:
  https://jqlang.org
  https://jqlang.org/download/  (downloading and installation instructions)

If you want to uninstall jq and used HomeBrew to install it,
use 'brew uninstall jq'. Otherwise, if you executed one of the
installation commands on the website above, find the installation
location and delete jq.
endef

ifndef DOCS_DIR
$(error ERROR: There is no ${DOCS_DIR} directory!)
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

.PHONY: help help-docs help-code help-uv help-llm help-llm-preamble help-jq

all help::
	$(info ${help_message})
	@echo

help-llm:: help-llm-preamble
help-docs help-code help-uv help-llm help-jq::
	$(info ${help_message_${@:help-%=%}})
	@echo

help-llm-preamble::
	@echo 'One moment, determining where llm wants "templates"...'
	@echo

.PHONY: print-info print-info-docs print-info-code print-info-env

print-info:: print-info-docs print-info-code print-info-env 
print-info-docs::
	@echo "For the GitHub Pages website:"
	@echo "  GitHub Pages URL:    ${PAGES_URL}"
	@echo "  current dir:         ${PWD}"
	@echo "  docs dir:            ${DOCS_DIR}"
	@echo "  site dir:            ${SITE_DIR}"
	@echo "  JEKYLL_PORT:         ${JEKYLL_PORT}"
	@echo

print-info-code::
	@echo "For the code examples:"
	@echo "  model:               ${MODEL}"
	@echo "  inference service:   ${INFERENCE_SERVICE}"
	@echo "  llm templates dir:   ${SRC_DIR}"
	@echo "  output dir:          ${OUTPUT_DIR}"
	@echo "  output data dir:     ${OUTPUT_DATA_DIR}"
	@echo "  example data dir:    ${EXAMPLE_DATA}"
	@echo "  src dir:             ${SRC_DIR}"
	@echo

print-info-env::
	@echo "The environment:"
	@echo "  GIT_HASH:            ${GIT_HASH}"
	@echo "  TIMESTAMP:           ${TIMESTAMP}"
	@echo "  MAKEFLAGS:           ${MAKEFLAGS}"
	@echo "  MAKEFLAGS_RECURSIVE: ${MAKEFLAGS_RECURSIVE}"
	@echo "  UNAME:               ${UNAME}"
	@echo "  ARCHITECTURE:        ${ARCHITECTURE}"
	@echo "  GIT_HASH:            ${GIT_HASH}"

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
run-jekyll: clean
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

.PHONY: all-code clean-code
.PHONY: run-terc run-tdd-example-refill-chatbot 
.PHONY: run-ubds run-unit-benchmark-data-synthesis 
.PHONY: run-ubdv run-unit-benchmark-data-validation 
.PHONY: before-run uv-venv 

all-code:: clean-code run-tdd-example-refill-chatbot run-unit-benchmark-data-synthesis run-unit-benchmark-data-validation run-unit-benchmark-data-validation 

clean-code::
	rm -rf ${CLEAN_CODE_DIRS}   
	
run-terc:: run-tdd-example-refill-chatbot
run-tdd-example-refill-chatbot:: before-run
	@echo "*** Running the TDD example."
	${NOOP} uv run ${SRC_DIR}/scripts/${@:run-%=%}.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${PROMPT_TEMPLATES_DIR} \
		--output ${OUTPUT_DIR}/${@:run-%=%}.out

# If you decide to write the output to a file, add --output ${OUTPUT_DIR}/${@:run-%=%}.out
# We don't do that by default, because this output is either empty or small for normal 
# execution runs.
run-ubds:: run-unit-benchmark-data-synthesis
run-unit-benchmark-data-synthesis:: before-run 
	@echo "*** Running the unit benchmark data synthesis example."
	${NOOP} ${SRC_DIR}/scripts/${@:run-%=%}.sh --model ${MODEL} \
		--data ${OUTPUT_DATA_DIR} 

# If you decide to write the output to a file, add --output ${OUTPUT_DIR}/${@:run-%=%}.out
# We don't do that by default, because this output is either empty or small for normal 
# execution runs.
run-ubdv:: run-unit-benchmark-data-validation
run-unit-benchmark-data-validation:: before-run
	@echo "*** Running the unit benchmark synthetic data validation example."
	${NOOP} ${SRC_DIR}/scripts/${@:run-%=%}.sh --model ${MODEL} \
		--data ${OUTPUT_DATA_DIR} 

${TEMP_DIR} ${OUTPUT_DIR} ${OUTPUT_DATA_DIR}::
	mkdir -p $@

# See help above for why we have install-templates as a dependency.
before-run:: uv-venv jq-command-check llm-command-check ${OUTPUT_DIR} ${OUTPUT_DATA_DIR} install-templates 
	$(info NOTE: If errors occur, try 'make setup' or 'make clean-setup setup', then try again.)

uv-venv:: uv-command-check 
	uv venv

.PHONY: one-time-setup setup clean-setup 
.PHONY: clean-uv clean-jq clean-llm clean-templates 
.PHONY: install-uv install-jq install-jq-preamble install-llm install-templates

setup one-time-setup:: install-uv install-llm install-jq

clean-setup:: clean-uv clean-llm clean-jq

clean-uv clean-jq:: 
	@echo "You have to uninstall ${@:clean-%=%} manually:"
	@echo
	$(info ${help_message_${@:clean-%=%}})

clean-llm:: uv-command-check clean-templates
	@printf "uv pip uninstalling llm and support libraries. Proceed? [Y/n] " && \
		read answer; \
		[[ $$answer = 'n' ]] && exit 0 || echo uv pip uninstall llm bs4

clean-templates::
	@cd ${SRC_DIR}/llm/templates/ && \
		for t in *.yaml; do echo "removing: ${LLM_TEMPLATES_LIB_DIR}/$$t"; rm -f "${LLM_TEMPLATES_LIB_DIR}/$$t"; done
	ls -l "${LLM_TEMPLATES_LIB_DIR}"

install-llm:: install-templates
	pip install -U llm bs4
	llm install llm-ollama
	echo "If you plan to use ollama for local inference, follow the installation instructions at https://ollama.com"

install-templates::
	cp ${SRC_DIR}/llm/templates/*.yaml "${LLM_TEMPLATES_LIB_DIR}"
	ls -l "${LLM_TEMPLATES_LIB_DIR}"

install-uv install-jq:: 
	@cmd=${@:install-%=%} && command -v $$cmd > /dev/null && \
		echo "$$cmd is already installed" || ${MAKE} help-$$cmd

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
