"""
A simple script to verify MCP server functionality.

This script tests that the MCP server can be imported and initialized
without requiring the actual MCP SDK to be installed.

See also the src/tests/integration/.../test_mcp_server.py test version of this script.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.chatbot import ChatBot, ChatBotResponseHandler
from apps.chatbot.mcp_server.server import create_mcp_server

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from apps.chatbot.mcp_server.server import create_mcp_server
        print("✓ Successfully imported MCP server modules")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_chatbot_creation():
    """Test that ChatBot can be created."""
    print("\nTesting ChatBot creation...")
    try:
        # Create a simple logger
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)
        
        chatbot = ChatBot(
            model="ollama_chat/gpt-oss:20b",
            service_url="http://localhost:11434",
            template_dir="src/apps/chatbot/prompts/templates",
            data_dir="src/data",
            confidence_level_threshold=0.9,
            response_handler = ChatBotResponseHandler(
                confidence_level_threshold=0.9, 
                logger=logger),
            logger=logger
        )
        print("✓ Successfully created ChatBot instance")
        print(f"  - Model: {chatbot.model}")
        print(f"  - Service URL: {chatbot.service_url}")
        print(f"  - Template dir: {chatbot.template_dir}")
        print(f"  - Data dir: {chatbot.data_dir}")
        print(f"  - Confidence threshold: {chatbot.confidence_level_threshold}")
        return True
    except Exception as e:
        print(f"✗ Error creating ChatBot: {e}")
        return False


def test_mcp_server_creation():
    """Test that MCP server can be created (if MCP SDK is available)."""
    print("\nTesting MCP server creation...")
    try:
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)
        
        result = create_mcp_server(
            model="ollama_chat/gpt-oss:20b",
            service_url="http://localhost:11434",
            template_dir="src/apps/chatbot/prompts/templates",
            data_dir="src/data",
            confidence_level_threshold=0.9,
            logger=logger
        )
        
        if result is None:
            print("⚠ MCP SDK not available (this is expected if not installed)")
            print("  Install with: pip install mcp")
            return True  # Not a failure, just not installed
        
        server, chatbot = result
        print("✓ Successfully created MCP server")
        print(f"  - Server type: {type(server).__name__}")
        print(f"  - ChatBot model: {chatbot.model}")
        return True
    except Exception as e:
        print(f"✗ Error creating MCP server: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("ChatBot Creation", test_chatbot_creation()))
    results.append(("MCP Server Creation", test_mcp_server_creation()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

