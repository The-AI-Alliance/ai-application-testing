"""
Integration tests for the ChatBot API server.

These tests verify that the OpenAI-compatible API server works correctly
with the ChatBot implementation.
"""
import json, logging, pytest
from fastapi.testclient import TestClient
from pathlib import Path

from apps.chatbot.api_server.server import APIServer

@pytest.fixture
def api_server():
    """Create an API server instance for testing."""
    # Use test configuration
    model = "ollama_chat/gpt-oss:20b"
    service_url = "http://localhost:11434"
    # Ugly hack!!
    src_dir_path = Path(__file__).parent.parent.parent.parent.parent.parent
    template_dir = str(src_dir_path / "apps/chatbot/prompts/templates")
    data_dir = str(src_dir_path / "data")
    logger = logging.getLogger('test_api_server')
    logger.setLevel(logging.INFO)

    server = APIServer(
        model=model,
        service_url=service_url,
        template_dir=template_dir,
        data_dir=data_dir,
        confidence_level_threshold=0.9,
        host="127.0.0.1",
        port=8000,
        logger=logger
    )
    
    return server


@pytest.fixture
def client(api_server):
    """Create a test client for the API server."""
    return TestClient(api_server.app)

class TestAPIServerEndpoints:
    """Test the API server endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["endpoints"]["chat_completions"] == "/v1/chat/completions"
        assert data["endpoints"]["models"] == "/v1/models"
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_list_models_endpoint(self, client):
        """Test the /v1/models endpoint."""
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert "data" in data
        assert len(data["data"]) > 0
        
        # Check model structure
        model = data["data"][0]
        assert "id" in model
        assert "object" in model
        assert model["object"] == "model"
        assert "created" in model
        assert "owned_by" in model


class TestChatCompletions:
    """Test the chat completions endpoint."""
    
    def test_chat_completion_basic(self, client):
        """Test basic chat completion request."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "I need a refill for my blood pressure medication"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["object"] == "chat.completion"
        assert "created" in data
        assert "model" in data
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        # Check choice structure
        choice = data["choices"][0]
        assert "index" in choice
        assert choice["index"] == 0
        assert "message" in choice
        assert choice["message"]["role"] == "assistant"
        assert "content" in choice["message"]
        assert len(choice["message"]["content"]) > 0
        assert "finish_reason" in choice
        
        # Check usage
        assert "usage" in data
        assert "prompt_tokens" in data["usage"]
        assert "completion_tokens" in data["usage"]
        assert "total_tokens" in data["usage"]
    
    def test_chat_completion_no_user_message(self, client):
        """Test chat completion with no user message returns error."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 400
        assert "No user message found" in response.json()["detail"]
    
    def test_chat_completion_streaming(self, client):
        """Test streaming chat completion."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "I need a refill for my blood pressure medication"}
            ],
            "stream": True
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse streaming response
        chunks = []
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        chunks.append(chunk)
                    except json.JSONDecodeError:
                        pass
        
        # Verify we got chunks
        assert len(chunks) > 0
        
        # Check first chunk structure
        first_chunk = chunks[0]
        assert "id" in first_chunk
        assert first_chunk["object"] == "chat.completion.chunk"
        assert "created" in first_chunk
        assert "model" in first_chunk
        assert "choices" in first_chunk
        
        # Check that we have content in at least one chunk
        has_content = any(
            chunk["choices"][0].get("delta", {}).get("content")
            for chunk in chunks
        )
        assert has_content
        
        # Check last chunk has finish_reason
        last_chunk = chunks[-1]
        assert last_chunk["choices"][0].get("finish_reason") == "stop"
    
    def test_chat_completion_multiple_messages(self, client):
        """Test chat completion with conversation history."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hello! How can I help you today?"},
                {"role": "user", "content": "I need a refill for my medication"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "content" in data["choices"][0]["message"]


class TestAPIServerIntegration:
    """Integration tests for the full API server."""
    
    def test_prescription_refill_query(self, client):
        """Test a prescription refill query through the API."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "I need to refill my lisinopril prescription"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        
        # The reply should mention refill or prescription
        assert any(word in reply.lower() for word in ["refill", "prescription", "medication"])
    
    def test_emergency_query(self, client):
        """Test an emergency query through the API."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "I'm having severe chest pain"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        
        # The reply should mention emergency or 911
        assert any(word in reply.lower() for word in ["emergency", "911", "urgent"])
    
    def test_appointment_query(self, client):
        """Test an appointment query through the API."""
        request_data = {
            "model": "ollama_chat/gpt-oss:20b",
            "messages": [
                {"role": "user", "content": "I'd like to schedule an appointment"}
            ],
            "stream": False
        }
        
        response = client.post("/v1/chat/completions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        
        # The reply should mention appointment
        assert "appointment" in reply.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

