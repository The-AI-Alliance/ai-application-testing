# Makefile for the ai-application-testing repo code.

SRC_DIR            ?= .
SRC_TEMPLATES_DIR  ?= ${SRC_DIR/llm/templates}
TEMP_DIR           ?= temp
OUTPUT             ?= ${TEMP_DIR}/output
OUTPUT_DATA        ?= ${OUTPUT}/data
DOCS_DIR           ?= ../docs
TIMESTAMP          ?= $(shell date +"%Y%m%d-%H%M%S")

# One way to prevent execution of scripts is to invoke make this way:
# NOOP=echo make foobar
NOOP        ?=

MODEL             ?= gpt-oss:20b
INFERENCE_SERVICE ?= ollama

LLM_TEMPLATE_DIR ?= $(shell llm templates path)
ifeq ($(LLM_TEMPLATE_DIR),)
LLM_TEMPLATE_DIR := $$HOME/Library/Application Support/io.datasette.llm/templates (on MacOS)
endif

define help_message
Quick help for this make process for the tools described in this website.
For the tools used to manage the website, see the parent directory Makefile.

make all                # Clean and run the tools.
make clean              # Remove build artifacts, etc., such as outputs in ${OUTPUT}

make one-time-setup     # Synonym for the setup target...
make setup              # One-time setup tasks; builds target install-llm, which
                        # builds install-templates.
make install-llm        # pip install "llm" and dependencies. Also makes install-templates.
                        # Run "make help-llm" for more information.
make install-templates  # Install our llm "templates" into llm. See also the "run-*" targets.

make install-jq         # Attempt to install "jq" and if not feasible, provide instructions
                        # for doing this. Run "make help-jq" for more information.

make clean-setup        # Undoes everything done by the setup target. Builds clean-llm,
                        # which builds clean-templates.
make clean-llm          # pip uninstall "llm" and dependencies. Also makes clean-templates.
make clean-templates    # Remove our llm "templates" from llm.
make clean-jq           # Attempt to uninstall jq or provide instructions for this purpose.

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
make run-unit-benchmark-data-validation
                        # Run the code for validating the synthetic data for the "unit benchmark".
                        # See the Unit Benchmark chapter in the website for details.

Miscellaneous tasks for help, debugging, setup, etc.

make help               # Prints this output.

The "llm" CLI is used by many of the tools here:

make help-llm           # Prints specific information about llm, including installation.
make help-jq            # Prints specific information about jq, including installation.
endef

define help_llm_message
The "llm" CLI is used by many of the tools here. For more details, see:
  https://github.com/simonw/llm

You can install llm using make:
  make install-llm

If you want to serve models locally using "ollama", see the installation instructions:
  https://ollama.com 

Also install the llm plugin using the llm CLI:
  llm install llm-ollama

The tools also use several llm "templates". These need to be installed into:
  ${LLM_TEMPLATE_DIR}

Use the following make command to do this:
  make install-templates 

WARNING: If you edit the templates in ${SRC_TEMPLATES_DIR}, rerun  
  make install-templates 
endef

define help_jq_message
The "jq" CLI is used by some scripts for parsing JSON. For more details, see:
  https://jqlang.org
  https://jqlang.org/download/  (downloading and installation instructions)

You can attempt to install jq using make, although it may have to tell you to do this manually:
  make install-jq
endef

.PHONY: all help help-llm help-llm-preamble help-jq clean 
.PHONY: run-terc run-tdd-example-refill-chatbot 
.PHONY: run-ubds run-unit-benchmark-data-synthesis 
.PHONY: run-ubdv run-unit-benchmark-data-validation 
.PHONY: before-run

all:: clean run-tdd-example-refill-chatbot run-unit-benchmark-data-synthesis run-unit-benchmark-data-validation run-unit-benchmark-data-validation 

help::
	$(info ${help_message})
	@echo

help-llm:: help-llm-preamble
	$(info ${help_llm_message})
	@echo
help-llm-preamble::
	@echo 'One moment, determining where llm wants "templates"...'

help-jq::
	$(info ${help_jq_message})
	@echo

clean:: 
	rm -rf ${TEMP_DIR}
	
run-terc:: run-tdd-example-refill-chatbot
run-tdd-example-refill-chatbot:: before-run
	@echo "*** Running the TDD example."
	${NOOP} ${SRC_DIR}/scripts/${@:run-%=%}.sh --model ${MODEL} \
		--output ${OUTPUT}/${@:run-%=%}.out

# If you decide to write the output to a file, add --output ${OUTPUT}/${@:run-%=%}.out
# We don't do that by default, because this output is either empty or small for normal 
# execution runs.
run-ubds:: run-unit-benchmark-data-synthesis
run-unit-benchmark-data-synthesis:: before-run 
	@echo "*** Running the unit benchmark data synthesis example."
	${NOOP} ${SRC_DIR}/scripts/${@:run-%=%}.sh --model ${MODEL} \
		--data ${OUTPUT_DATA} 

# If you decide to write the output to a file, add --output ${OUTPUT}/${@:run-%=%}.out
# We don't do that by default, because this output is either empty or small for normal 
# execution runs.
run-ubdv:: run-unit-benchmark-data-validation
run-unit-benchmark-data-validation:: before-run
	@echo "*** Running the unit benchmark synthetic data validation example."
	${NOOP} ${SRC_DIR}/scripts/${@:run-%=%}.sh --model ${MODEL} \
		--data ${OUTPUT_DATA} 

${TEMP_DIR} ${OUTPUT} ${OUTPUT_DATA}::
	mkdir -p $@

# See help above for why we have install-templates as a dependency.
before-run:: ${OUTPUT} ${OUTPUT_DATA} install-templates
	$(info NOTE: If errors occur, try 'make setup' or 'make clean-setup setup', then try again.)

.PHONY: one-time-setup setup clean-setup 
.PHONY: clean-llm clean-templates install-llm install-templates
.PHONY: clean-jq clean-jq-preamble install-jq install-jq-preamble

setup one-time-setup:: install-llm

clean-setup:: clean-llm clean-jq

clean-llm:: clean-templates
	@printf "Pip uninstalling llm and support libraries. Proceed? [Y/n] " && \
		read answer; \
		[[ $$answer = 'n' ]] && exit 0 || echo pip uninstall llm bs4

clean-templates::
	@cd ${SRC_DIR}/llm/templates/ && \
		for t in *.yaml; do echo "removing: ${LLM_TEMPLATE_DIR}/$$t"; rm -f "${LLM_TEMPLATE_DIR}/$$t"; done
	ls -l "${LLM_TEMPLATE_DIR}"

clean-jq:: clean-jq-preamble help-jq
clean-jq-preamble::
	@echo "TODO: Automated uninstallation of jq is not yet supported. See the installation instructions:"

install-llm:: install-templates
	pip install -U llm bs4
	llm install llm-ollama

install-templates::
	cp ${SRC_DIR}/llm/templates/*.yaml "${LLM_TEMPLATE_DIR}"
	ls -l "${LLM_TEMPLATE_DIR}"

install-jq:: 
	@command -v jq > /dev/null && echo "jq is already installed" || ${MAKE} install-jq-preamble help-jq
install-jq-preamble::
	@echo "TODO: Automated installation of jq is not yet supported. See the installation instructions:"
