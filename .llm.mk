# .llm.mk
# Some convenience targets for working with the "llm" CLI tool.
# It is NOT required to install and use this tool.
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
