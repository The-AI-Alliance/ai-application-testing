# Makefile for the ai-application-testing repo code.

SRC_ROOT    ?= .
DOCS_ROOT   ?= ../docs
TEMP_DIR    ?= ${SRC_ROOT}/temp
TOOLS_SRC   ?= ${DOCS_ROOT}/files
TOOLS_DEST  ?= ${TEMP_DIR}/src
OUTPUT      ?= ${TEMP_DIR}/output

LLM_TEMPLATE_DIR ?= $(shell llm templates path)

define help_message
Quick help for this make process for the tools described in this website.
For the tools used to manage the website, see the parent directory Makefile.

make all                # Clean and run the tools.
make clean              # Remove build artifacts, etc., including the contents of
                        # ${TOOLS_DEST}. (See the help for the stage-files target.)

make setup              # One-time setup tasks; builds target install-llm, which
                        # builds install-templates.
make install-llm        # pip install "llm" and dependencies. Also makes install-templates.
make install-templates  # Install llm "templates" into ${LLM_TEMPLATE_DIR}.

make clean-setup        # Undoes everything done by the setup target.
make clean-llm          # pip uninstall "llm" and dependencies. Also makes clean-templates.
make clean-templates    # Remove the llm "templates" from ${LLM_TEMPLATE_DIR}.

make stage-files        # The tools files are actually kept in ${TOOLS_SRC}, so 
                        # they are accessible in the website. This target copies
                        # them to ${TOOLS_DEST} for local testing, etc. Unlike the
                        # one-time setup target, this target is built first by all
                        # targets that run the example code. So, you don't need to
                        # make this target yourself.
                        # WARNING: Never edit files in ${TOOLS_DEST}! Instead, make
                        # edits in ${TOOLS_SRC} and let targets rerun "make stage-files".

make run-tdd-example    # Run the code for the TDD example "unit benchmark".

make setup              # One-time commands that setup tools:
                        # * Copy "llm" template files to $HOME/Library/

Miscellaneous tasks for help, debugging, setup, etc.

make help               # Prints this output.
endef

.PHONY: all help clean clean-tools-dest stage-files run-tdd-example

all:: clean stage-files run-tdd-example

help::
	$(info ${help_message})
	@echo

clean:: 
	rm -rf ${TEMP_DIR}
clean-tools-dest::
	rm -rf ${TOOLS_DEST}
	
stage-files:: clean-tools-dest ${TEMP_DIR} install-templates
	cp -r ${TOOLS_SRC} ${TOOLS_DEST}

run-tdd-example:: stage-files ${OUTPUT}
	@echo "Running the TDD example. If errors occur, run 'make setup' or 'make clean-setup setup', then try again."
	@echo TODO

${TEMP_DIR} ${OUTPUT}::
	mkdir -p $@

.PHONY: setup clean-setup clean-llm clean-templates install-llm install-templates

setup:: install-llm

clean-setup:: clean-llm

clean-llm:: clean-templates
	@printf "Pip uninstalling llm and support libraries. Proceed? [Y/n] " && \
		read answer; \
		[[ $$answer = 'n' ]] && exit 0 || echo pip uninstall llm bs4

clean-templates::
	@cd ${TOOLS_SRC}/llm/templates/ && \
		for t in *.yaml; do echo "removing: ${LLM_TEMPLATE_DIR}/$$t"; rm -f "${LLM_TEMPLATE_DIR}/$$t"; done && \
		ls -l "${LLM_TEMPLATE_DIR}"

install-llm:: install-templates
	pip install -U llm bs4
	llm install llm-ollama

install-templates::
	@cp ${TOOLS_SRC}/llm/templates/*.yaml "${LLM_TEMPLATE_DIR}" && \
		ls -l "${LLM_TEMPLATE_DIR}"
