"""
Example client demonstrating how to use the OpenAI-compatible API server.

This script shows various ways to interact with the Patient ChatBot API server
using the OpenAI Python client library.
"""
import os
import sys
from openai import OpenAI

example_content  = "I need a refill for my blood pressure medication"
example_messages = [
    {"role": "user", "content": example_content}
]

def make_client() -> OpenAI:
    return OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="not-needed"  # API key not required for local server
    )

def example_basic_query():
    """Example: Basic non-streaming query."""
    print("\n" + "="*60)
    print("Example 1: Basic Non-Streaming Query")
    print("="*60)
    
    client = make_client()
    
    response = client.chat.completions.create(
        model="ollama_chat/gpt-oss:20b",
        messages=example_messages)  # ty: ignore[invalid-argument-type]
    
    print(f"\nUser: {example_content}")
    print(f"Assistant: {response.choices[0].message.content}")
    print(f"\nMetadata:")
    print(f"  - Model: {response.model}")
    print(f"  - Tokens: {response.usage.total_tokens}")
    print(f"  - Finish Reason: {response.choices[0].finish_reason}")


def example_streaming_query():
    """Example: Streaming query."""
    print("\n" + "="*60)
    print("Example 2: Streaming Query")
    print("="*60)
    
    client = make_client()
    
    print(f"\nUser: {example_content}")
    print(f"Assistant: ", end="", flush=True)
    
    stream = client.chat.completions.create( # ty: ignore[no-matching-overload]
        model="ollama_chat/gpt-oss:20b",
        messages=example_messages,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print()  # New line after streaming


def example_conversation():
    """Example: Multi-turn conversation."""
    print("\n" + "="*60)
    print("Example 3: Multi-Turn Conversation")
    print("="*60)
    
    client = make_client()
    
    # First turn
    print(f"\nUser: {example_messages[0]['content']}")
    response = client.chat.completions.create(
        model="ollama_chat/gpt-oss:20b",
        messages=example_messages   # ty: ignore[invalid-argument-type]
    )
    assistant_reply = response.choices[0].message.content
    print(f"Assistant: {assistant_reply}")
    
    messages = example_messages.copy()

    # Add assistant response to conversation
    messages.append({"role": "assistant", "content": assistant_reply})
    
    # Second turn
    messages = example_messages.copy()
    messages.append({"role": "user", "content": "I need to refill my lisinopril prescription"})
    print(f"\nUser: {messages[-1]['content']}")
    response = client.chat.completions.create(
        model="ollama_chat/gpt-oss:20b",
        messages=messages   # ty: ignore[invalid-argument-type]
    )
    print(f"Assistant: {response.choices[0].message.content}")


def example_emergency_query():
    """Example: Emergency situation query."""
    print("\n" + "="*60)
    print("Example 4: Emergency Query")
    print("="*60)
    
    client = make_client()

    content = "I'm having severe chest pain and difficulty breathing"
    response = client.chat.completions.create(
        model="ollama_chat/gpt-oss:20b",
        messages=[
            {"role": "user", "content": content}
        ]
    )
    
    print(f"\nUser: {content}")
    print(f"Assistant: {response.choices[0].message.content}")


def example_list_models():
    """Example: List available models."""
    print("\n" + "="*60)
    print("Example 5: List Available Models")
    print("="*60)
    
    client = make_client()    
    models = client.models.list()
    
    print(f"\nAvailable models:")
    for model in models.data:
        print(f"  - {model.id} (owned by: {model.owned_by})")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Patient ChatBot API - Example Client")
    print("="*60)
    print("\nMake sure the API server is running:")
    print("  python -m apps.chatbot.api_server.server")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    try:
        # Run examples
        example_list_models()
        example_basic_query()
        example_streaming_query()
        example_conversation()
        example_emergency_query()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure the API server is running:")
        print("  python -m apps.chatbot.api_server.server")
        sys.exit(1)


if __name__ == "__main__":
    main()

