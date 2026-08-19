# Definitions for the API server support.

OPEN_WEBUI_DIR        ?= ${SRC_DIR}/apps/chatbot/open-webui
foo:
	$(info ${help-api-server-message})
define help-api-server-message
${HIGHLIGHT} Quick help for the make targets for the API server support for some of the tools. ${_END}

${CODE}make api-server${_END}         # Run the ChatBot's OpenAI-compatible API server.
${CODE}make run-api-server${_END}     # Synonym for ${CODE}api-server${_END}.

${CODE}make view-api-server-docs${_END}
${CODE}${_END}                        # Open a browser showing the API server ${CODE}docs${_END}.
${CODE}make view-api-server-redoc${_END}
${CODE}${_END}                        # Open a browser showing the API server ${CODE}redoc${_END}.
${CODE}make help-api-server-cli${_END}
${CODE}${_END}                        # Run the API server with the --help flag to show its CLI options.
endef


.PHONY: api-server run-api-server check-api-server help-api-server-cli
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

help-api-server-cli::
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/api_server/server.py --help

check-api-server::
	@echo "${INFO_LABEL}'Sanity check' that the OpenAI-compatible API server works:"
	@echo "${INFO_LABEL}Running the server in the background..."
	${NOOP} ${MAKE} api-server &
	@echo
	@echo "  ${HIGHLIGHT} Hit the 'return' key! ${_END}"
	@echo
	@echo "${INFO_LABEL}Running ${CODE}apps/chatbot//api_server/example_client.py${_END} ..."
	@echo
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/api_server/example_client.py
	@echo
	@echo " ${HIGHLIGHT} Using a hack: Find the process id for the server and kill it... ${_END}"
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
