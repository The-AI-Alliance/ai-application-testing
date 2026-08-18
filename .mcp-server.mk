# Definitions for the MCP server support.

define help-mcp-server-message
${HIGHLIGHT} Quick help for the make targets for the MCP server support for some of the tools. ${_END}

${CODE}make mcp-server${_END}         # Run the ChatBot's MCP server.
${CODE}make run-mcp-server${_END}     # Synonym for ${CODE}mcp-server${_END}.
${CODE}make help-mcp-server-cli${_END}
${CODE}${_END}                        # Run the MCP server with the --help flag to show its CLI options.
endef


.PHONY: mcp-server run-mcp-server check-mcp-server inspect-mcp-server help-mcp-server-cli

# See inspect-mcp-server for information about ${INSPECTOR}, which is otherwise
# blank.
run-mcp-server:: mcp-server
mcp-server:: before-chatbot
	@echo "${INFO_LABEL}Running the ChatBot MCP Server..."
	export LITELLM_LOG=ERROR; \
	${NOOP} ${INSPECTOR} uv run python ${SRC_DIR}/apps/chatbot/mcp_server/server.py \
		--model ${MODEL} \
		--service-url ${INFERENCE_URL} \
		--template-dir ${CHATBOT_TEMPLATES_DIR} \
		--data-dir ${CHATBOT_DATA_DIR} \
		--output-dir ${CHATBOT_OUTPUT_DIR} \
		--confidence-threshold ${CONFIDENCE_THRESHOLD} \
		--which-chatbot ${WHICH_CHATBOT} \
		--log-file ${OUTPUT_LOGS_DIR}/$@.log \
		${APP_ARGS}
	@echo "${INFO_LABEL}Log output: ${CODE}${OUTPUT_LOGS_DIR}/$@.log${_END}"

inspect-mcp-server:: command-check-node
	@echo "${INFO_LABEL}Running the ${CODE}@modelcontextprotocol/inspector${_END} with the ChatBot MCP Server..."
	${MAKE} INSPECTOR="npx @modelcontextprotocol/inspector" mcp-server

help-mcp-server-cli::
	${NOOP} uv run python ${SRC_DIR}/apps/chatbot/mcp_server/server.py --help
