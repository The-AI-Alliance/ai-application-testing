# Patient ChatBot MCP Server

This directory contains the MCP (Model Context Protocol) server implementation for the Patient ChatBot application. The MCP server exposes the ChatBot functionality as tools that can be used by MCP clients.

## Overview

The MCP server is built using **FastMCP**, which provides a simplified and more Pythonic way to create MCP servers. It provides three main tools:

1. **query_chatbot** - Send queries to the patient ChatBot
2. **get_chatbot_session_history** - Retrieve the conversation history
3. **get_chatbot_info** - Get information about the ChatBot configuration

### FastMCP Benefits

FastMCP simplifies MCP server development by:

- **Simplified API**: Use Python decorators (`@mcp.tool()`) to define tools
- **Type Safety**: Leverage Python type hints for automatic parameter validation
- **Less Boilerplate**: No need for separate tool registration functions
- **Better Integration**: Tools are defined inline with the server creation
- **Automatic Documentation**: Tool docstrings become tool descriptions

## Installation

### Prerequisites

1. Install FastMCP:
```bash
uv add fastmcp  # or use uv pip install fastmcp
```

## Running the MCP Server

### Standalone Mode

You can run the MCP server as a standalone process. For example:

```bash
cd src
uv run python -m apps.chatbot.mcp_server.server \
  --model "ollama_chat/gpt-oss:20b" \
  --service-url "http://localhost:11434" \
  --template-dir "prompts/templates" \
  --data-dir "data" \
  --confidence-threshold 0.9
```

> [!TIP]
> Use the `--help` flag to see all the options.

### As an MCP Server Configured for MCP Clients

To use this MCP server with MCP clients, add it to the appropriate MCP configuration file, e.g., `~/.bob/settings/mcp_settings.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "patient-chatbot": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "apps.chatbot.mcp_server.server",
        "--model", "ollama_chat/gpt-oss:20b",
        "--service-url", "http://localhost:11434",
        "--template-dir", "prompts/templates",
        "--data-dir", "data",
        "--confidence-threshold", "0.9"
      ],
      "cwd": "/path/to/ai-application-testing/src",
      "env": {
        "PYTHONPATH": "/path/to/ai-application-testing/src"
      }
    }
  }
}
```

## Architecture

The MCP server is organized into several components:

- **`__init__.py`** - Package initialization and exports
- **`server.py`** - Main server implementation with FastMCP and tool definitions

Here is the directory structure:

```
mcp_server/
├── __init__.py          # Package exports
├── server.py            # Server creation, tool definitions, and main entry point
└── README.md            # This file
```

## Tools

### query_chatbot

Send a query to the patient ChatBot and receive a response.

**Parameters:**
- `query` (string, required): The user's question or request

**Returns:**
- A formatted response containing the ChatBot's reply and metadata (label, confidence)

**Example:**
```python
await query_chatbot("I need a refill for my blood pressure medication")
```

### get_chatbot_session_history

Retrieve the conversation history for the current session.

**Parameters:** None

**Returns:**
- A formatted list of all queries and responses in the current session

### get_chatbot_info

Get information about the ChatBot's current configuration.

**Parameters:** None

**Returns:**
- Configuration details including model, service URL, confidence threshold, and session length

## Integration with the ChatBot Application

The MCP server uses the same `ChatBot` class from the main application (`apps.chatbot`), ensuring consistency between the interactive shell and MCP server modes.

## Configuration Options

All command-line options from the main ChatBot application are supported:

- `--model` / `-m`: LLM model to use (default: "ollama_chat/gpt-oss:20b")
- `--service-url` / `-s`: Inference service URL (default: "http://localhost:11434")
- `--template-dir` / `-t`: Prompt template directory (default: "src/apps/chatbot/prompts/templates")
- `--data-dir` / `-d`: Directory with some data (default: "src/data")
- `--confidence-threshold` / `-c`: Confidence threshold level (default: 0.9)
- `--log-file` / `-l`: Log file path
- `--log-level`: Logging level (default: INFO)
- `--verbose` / `-v`: Enable verbose output

## Error Handling

The MCP server includes comprehensive error handling:

- Invalid queries return error messages.
- Chatbot errors are caught and returned as tool responses.
- All errors are logged when a logger is configured.

## Development

To modify or extend the MCP server:

1. **Adding new tools**: Add tool definitions to `server.py` using the `@mcp.tool()` decorator within the `create_mcp_server()` function
2. **Modifying server behavior**: Update `server.py` to change initialization or runtime behavior
3. **Testing**: Run the server standalone and use MCP client tools to test functionality

### Example: Adding a New Tool

```python
@mcp.tool()
async def new_tool(param: str) -> str:
    """
    Description of what this tool does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of the return value
    """
    # Implementation here
    return "result"
```

## Testing

Run the integration tests:

```bash
make integration-tests # run all the integration tests
# or
cd src && uv run python -m pytest tests/integration/apps/chatbot/mcp_server/test_mcp_server.py -v
```


## Troubleshooting

### FastMCP Not Found

If you get an error that `fastmcp` can't be imported, install it:
```bash
uv add fastmcp  # or with uv pip install fastmcp
```

### Import Errors

Ensure the `PYTHONPATH` includes the `src` directory:
```bash
export PYTHONPATH=/path/to/ai-application-testing/src:$PYTHONPATH
```

### Connection Issues

Verify the inference service is running:
```bash
curl http://localhost:11434/api/tags
```

## License

See the Apache 2.0 license file in this repository's root directory.
