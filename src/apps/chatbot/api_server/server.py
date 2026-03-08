"""
OpenAI-compatible API server for the Patient ChatBot.

This module creates a FastAPI server that exposes the chatbot functionality
through OpenAI-compatible endpoints, allowing integration with any client
that supports the OpenAI API format.
"""
import logging
import os
import sys
import time
import uuid
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from apps.chatbot import ChatBot
from common.utils import setup, get_package_version


# Pydantic models for OpenAI-compatible API

class Message(BaseModel):
    """A chat message."""
    role: str = Field(..., description="The role of the message author (system, user, or assistant)")
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(BaseModel):
    """Request body for chat completions endpoint."""
    model: str = Field(..., description="ID of the model to use")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(default=False, description="Whether to stream responses")
    n: Optional[int] = Field(default=1, description="Number of completions to generate")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences")


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionChoice(BaseModel):
    """A single completion choice."""
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    """Response from chat completions endpoint."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class ChatCompletionChunk(BaseModel):
    """A chunk in a streaming response."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


class Model(BaseModel):
    """Model information."""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """List of available models."""
    object: str = "list"
    data: List[Model]


class APIServer:
    """OpenAI-compatible API server for the ChatBot."""
    
    def __init__(
        self,
        model: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        confidence_level_threshold: float = 0.9,
        host: str = "0.0.0.0",
        port: int = 8000,
        logger: logging.Logger | None = None
    ):
        """
        Initialize the API server.
        
        Args:
            model: The LLM model to use
            service_url: The URL of the inference service
            template_dir: Directory containing prompt templates
            data_dir: Directory containing data files
            confidence_level_threshold: Minimum confidence level for responses
            host: Host to bind the server to
            port: Port to bind the server to
            logger: Optional logger for debugging
        """
        self.model = model
        self.service_url = service_url
        self.template_dir = template_dir
        self.data_dir = data_dir
        self.confidence_level_threshold = confidence_level_threshold
        self.host = host
        self.port = port
        self.logger = logger
        self.version = get_package_version(self.logger)
        if not self.version:
            self.version = '0.1.0'  # An error occurred that was logged by get_package_version()
        
        # Create the chatbot instance
        self.chatbot = ChatBot(
            model=self.model,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            confidence_level_threshold=self.confidence_level_threshold,
            logger=self.logger
        )
        

        # Create FastAPI app
        self.app = FastAPI(
            title="Patient ChatBot API",
            description="OpenAI-compatible API for the Patient ChatBot",
            version=self.version
        )
        
        # Register routes
        self._register_routes()
        
        if self.logger:
            self.logger.info(f"API server initialized with model: {model}")
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "message": "Patient ChatBot API",
                "version": self.version,
                "endpoints": {
                    "chat_completions": "/v1/chat/completions",
                    "models": "/v1/models",
                    "health": "/health"
                }
            }
        
        @self.app.get("/v1/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy"}
        
        @self.app.get("/v1/models", response_model=ModelList)
        async def list_models():
            """List available models (OpenAI-compatible)."""
            if self.logger:
                self.logger.info("GET /v1/models called")
            
            return ModelList(
                object="list",
                data=[
                    Model(
                        id=self.model,
                        object="model",
                        created=int(time.time()),
                        owned_by="patient-chatbot"
                    )
                ]
            )
        
        @self.app.post("/v1/chat/completions")
        async def create_chat_completion(request: ChatCompletionRequest):
            """
            Create a chat completion (OpenAI-compatible).
            
            This endpoint accepts OpenAI-formatted chat completion requests
            and returns responses in the same format.
            """
            if self.logger:
                self.logger.info(f"POST /v1/chat/completions called with model: {request.model}")
            
            try:
                # Extract the user message (last message with role 'user')
                user_messages = [msg for msg in request.messages if msg.role == "user"]
                if not user_messages:
                    raise HTTPException(status_code=400, detail="No user message found in request")
                
                user_query = user_messages[-1].content
                
                if self.logger:
                    self.logger.debug(f"User query: {user_query}")
                
                # Handle streaming vs non-streaming
                if request.stream:
                    return StreamingResponse(
                        self._stream_completion(request, user_query),
                        media_type="text/event-stream"
                    )
                else:
                    return await self._create_completion(request, user_query)
                    
            except HTTPException:
                raise
            except Exception as e:
                error_msg = f"Error processing chat completion: {str(e)}"
                if self.logger:
                    self.logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
    
    async def _create_completion(
        self,
        request: ChatCompletionRequest,
        user_query: str
    ) -> ChatCompletionResponse:
        """Create a non-streaming chat completion."""
        
        # Query the chatbot
        response = self.chatbot.query(user_query)
        
        if isinstance(response, str):
            # Error occurred
            raise HTTPException(status_code=500, detail=f"Chatbot error: {response}")
        
        # Extract the reply
        reply_to_user = response.get('reply_to_user', 'No reply generated')
        
        # Create OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created_time = int(time.time())
        
        # Estimate token counts (rough approximation)
        prompt_tokens = len(user_query.split())
        completion_tokens = len(reply_to_user.split())
        
        return ChatCompletionResponse(
            id=completion_id,
            object="chat.completion",
            created=created_time,
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=reply_to_user
                    ),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )
    
    async def _stream_completion(
        self,
        request: ChatCompletionRequest,
        user_query: str
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion response."""
        
        # Query the chatbot
        response = self.chatbot.query(user_query)
        
        if isinstance(response, str):
            # Error occurred - send error chunk
            error_chunk = {
                "error": {
                    "message": f"Chatbot error: {response}",
                    "type": "chatbot_error",
                    "code": "internal_error"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # Extract the reply
        reply_to_user = response.get('reply_to_user', 'No reply generated')
        
        # Create streaming response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created_time = int(time.time())
        
        # Split response into words for streaming effect
        words = reply_to_user.split()
        
        for i, word in enumerate(words):
            chunk = ChatCompletionChunk(
                id=completion_id,
                object="chat.completion.chunk",
                created=created_time,
                model=request.model,
                choices=[{
                    "index": 0,
                    "delta": {
                        "content": word + (" " if i < len(words) - 1 else "")
                    },
                    "finish_reason": None
                }]
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
        
        # Send final chunk with finish_reason
        final_chunk = ChatCompletionChunk(
            id=completion_id,
            object="chat.completion.chunk",
            created=created_time,
            model=request.model,
            choices=[{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    
    def run(self):
        """Run the API server."""
        if self.logger:
            self.logger.info(f"Starting API server on {self.host}:{self.port}")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )


def main():
    """
    Main entry point for running the API server standalone.
    """
    script = os.path.basename(__file__)
    description = "OpenAI-compatible API Server for Patient ChatBot"
    
    def add_args(parser):
        parser.add_argument(
            "-c", "--confidence-threshold",
            type=float,
            default=0.9,
            help="Confidence threshold level (0.0-1.0). Default: 0.9"
        )
        parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Host to bind the server to. Default: 0.0.0.0"
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to bind the server to. Default: 8000"
        )
    
    args, logger = setup(
        script,
        description,
        epilog="Run the chatbot as an OpenAI-compatible API server.",
        add_arguments=add_args
    )
    
    if args.verbose:
        print(f"{description}")
        for key, value in vars(args).items():
            k = key + ":"
            print(f"  {k:20s} {value}")
    
    try:
        server = APIServer(
            model=args.model,
            service_url=args.service_url,
            template_dir=args.template_dir,
            data_dir=args.data_dir,
            confidence_level_threshold=args.confidence_threshold,
            host=args.host,
            port=args.port,
            logger=logger
        )
        
        server.run()
        
    except KeyboardInterrupt:
        if logger:
            logger.info("API server stopped by user")
        print("\nAPI server stopped")
    except Exception as e:
        error_msg = f"Error running API server: {e}"
        if logger:
            logger.error(error_msg)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
