# OpenAI-Compatible API Server for Patient ChatBot

This module provides an OpenAI-compatible REST API server for the Patient ChatBot, allowing integration with any client that supports the OpenAI API format.

## Features

- **OpenAI-Compatible Endpoints**: Implements the standard OpenAI API endpoints
- **Streaming Support**: Supports both streaming and non-streaming responses
- **FastAPI Framework**: Built on FastAPI for high performance and automatic API documentation
- **Easy Integration**: Works with any OpenAI-compatible client library

## Installation

The API server dependencies are included in the main project. To install them:

```bash
uv sync
```

This will install:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client for testing
- `pytest` - Testing framework

## Running the Server

### Using Python Module

```bash
cd src && uv run python -m apps.chatbot.api_server.server \
  --model ollama_chat/gpt-oss:20b \
  --service-url http://localhost:11434 \
  --template-dir apps/chatbot/prompts/templates \
  --data-dir data \
  --confidence-threshold 0.9 \
  --host 0.0.0.0 \
  --port 8000
```

### Command Line Options

- `--model`: The LLM model to use (default: from environment or config)
- `--service-url`: URL of the inference service (default: http://localhost:11434)
- `--template-dir`: Directory containing ChatBot prompt templates
- `--data-dir`: Directory for data storage
- `--confidence-threshold`: Confidence threshold for responses (0.0-1.0, default: 0.9)
- `--host`: Host to bind the server to (default: 0.0.0.0)
- `--port`: Port to bind the server to (default: 8000)
- `--verbose`: Enable verbose logging

## API Endpoints

### Root Endpoint

```shell
curl localhost:8000
```

Returns API information and available endpoints.

An example response:

```json
{
  "message": "Patient ChatBot API",
  "version": "0.5.0",
  "endpoints": {
    "chat_completions": "/v1/chat/completions",
    "models": "/v1/models",
    "health": "/health"
  }
}
```

### Health Check

```shell
curl localhost:8000/v1/health
```

Returns the health status of the server.

It should return the following:

```json
{
  "status": "healthy"
}
```

### Model List


```shell
curl localhost:8000/v1/models
```

Lists available models (OpenAI-compatible).

An example response:

```json
{
  "object": "list",
  "data": [
    {
      "id": "ollama_chat/gpt-oss:20b",
      "object": "model",
      "created": 1234567890,
      "owned_by": "patient-chatbot"
    }
  ]
}
```

### Chat Completions


```shell
curl --request POST --header "Content-Type: application/json" --data '{
    "model": "ollama_chat/gpt-oss:20b",
    "messages": [
      {
        "role": "user",
        "content": "I need a refill for my blood pressure medication"
      }
    ],
    "stream": false,
    "temperature": 1.0,
    "max_tokens": null
  }' localhost:8000/v1/chat/completions 
```

Creates a chat completion (OpenAI-compatible).


A non-streaming response:

```json
{
  "id": "chatcmpl-4e73d300326e4f0b9ac3a451",
  "object": "chat.completion",
  "created": 1772988862,
  "model": "ollama_chat/gpt-oss:20b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Sure, I have requested a refill for your blood pressure medication. You should receive confirmation from your pharmacy shortly."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 18,
    "total_tokens": 27
  }
}
```

A streaming response, when `stream: true`, in which case the server returns _Server-Sent Events_ (SSE):

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"ollama_chat/gpt-oss:20b","choices":[{"index":0,"delta":{"content":"Sure, "},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"ollama_chat/gpt-oss:20b","choices":[{"index":0,"delta":{"content":"I "},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"ollama_chat/gpt-oss:20b","choices":[{"index":0,"delta":{"content":"have "},"finish_reason":null}]}

...

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"ollama_chat/gpt-oss:20b","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### Using the Python OpenAI Client

```python
from openai import OpenAI

# Point to your local API server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # API key not required for local server
)

# Non-streaming
response = client.chat.completions.create(
    model="ollama_chat/gpt-oss:20b",
    messages=[
        {"role": "user", "content": "I need a refill for my blood pressure medication"}
    ]
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="ollama_chat/gpt-oss:20b",
    messages=[
        {"role": "user", "content": "I need a refill for my blood pressure medication"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Using LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
    model="ollama_chat/gpt-oss:20b"
)

response = llm.invoke("I need a refill for my blood pressure medication")
print(response.content)
```

## Testing

Run the integration tests:

```bash
make integration-tests # run all the integration tests
# or
cd src && uv run python -m pytest tests/integration/apps/chatbot/api_server/test_api_server.py -v
```

## Interactive API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly in your browser.

> [!TIP]
> Run the `make` targets `view-api-server-docs` or `view-api-server-redoc` to open these links in a browser.

## Architecture

The API server is built on top of the existing ChatBot implementation:

```
┌─────────────────────────────────────┐
│   OpenAI-Compatible API Client      │
│   (Python, JavaScript, cURL, etc.)  │
└─────────────────┬───────────────────┘
                  │
                  │ HTTP/REST
                  │
┌─────────────────▼───────────────────┐
│      FastAPI API Server             │
│  - /v1/chat/completions             │
│  - /v1/models                       │
│  - /health                          │
└─────────────────┬───────────────────┘
                  │
                  │ Python API
                  │
┌─────────────────▼───────────────────┐
│         ChatBot Core                │
│  - Query processing                 │
│  - Response handling                │
│  - Confidence thresholds            │
└─────────────────┬───────────────────┘
                  │
                  │ LiteLLM
                  │
┌─────────────────▼───────────────────┐
│    Inference Service (Ollama)       │
└─────────────────────────────────────┘
```

## Differences from Standard OpenAI API

While this server implements the OpenAI API format, there are some differences:

1. **Model Names**: Uses LiteLLM model naming (e.g., `ollama_chat/gpt-oss:20b`)
2. **Response Content**: Responses are tailored for healthcare chatbot use cases
3. **Confidence Thresholds**: Applies confidence-based response filtering
4. **Session Management**: Maintains conversation history internally

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request (e.g., missing user message)
- `500 Internal Server Error`: Server or chatbot error

Error responses include a `detail` field with the error message:

```json
{
  "detail": "No user message found in request"
}
```

## Security Considerations

**Important**: This is a demonstration server for educational purposes. For production use:

1. Add authentication (API keys, OAuth, etc.)
2. Implement rate limiting
3. Add input validation and sanitization
4. Use HTTPS/TLS
5. Implement proper logging and monitoring
6. Add CORS configuration as needed
7. Consider adding request/response size limits

## Troubleshooting

### Server won't start

- Check that the port is not already in use
- Verify that all dependencies are installed (`uv sync`)
- Ensure the inference service (Ollama) is running

### Responses are slow

- Check the model size - larger models require more memory and time
- Verify the inference service is running locally
- Consider using a smaller model for testing

### Import errors

- Run `uv sync` to install all dependencies
- Verify you're in the correct virtual environment

## Related Documentation

- [ChatBot Main Documentation](../README.md)
- [MCP Server Documentation](../mcp_server/README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)