"""
Simple test script to verify MCP server functionality.

This script tests that the MCP server can be imported and initialized
with FastMCP.
"""

import os
import logging
from pathlib import Path

# Add src to path for imports
# sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from apps.chatbot.mcp_server.server import create_mcp_server
from tests.utils.apps.chatbot.chatbot_test_base import ChatBotTestBase

def test_chatbot_creation():
    data_dir = os.environ.get("TEST_DATA_DIR", "src/tests/data")
    cbtb = ChatBotTestBase(data_dir = Path(data_dir))
    """Test that a ChatBot can be created. This is effectively done by the ChatBotTestBase.setUp() method."""
    assert cbtb.chatbot
    print("✓ Successfully created ChatBot instance")
    print(f"  - Model: {cbtb.chatbot.model}")
    print(f"  - Service URL: {cbtb.chatbot.service_url}")
    print(f"  - Template dir: {cbtb.chatbot.template_dir}")
    print(f"  - Data dir: {cbtb.chatbot.data_dir}")
    print(f"  - Output dir: {cbtb.chatbot.output_dir}")
    print(f"  - Confidence threshold: {cbtb.chatbot.confidence_level_threshold}")

def test_mcp_server_creation():
    data_dir = os.environ.get("TEST_DATA_DIR", "src/tests/data")
    cbtb = ChatBotTestBase(data_dir = data_dir)
    """Test that MCP server can be created with FastMCP."""
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)

    result = create_mcp_server(
        model=cbtb.chatbot.model,
        service_url=cbtb.chatbot.service_url,
        template_dir=cbtb.chatbot.template_dir,
        data_dir=cbtb.chatbot.data_dir,
        output_dir=cbtb.chatbot.output_dir,
        confidence_level_threshold=cbtb.chatbot.confidence_level_threshold,
        logger=logger,
    )

    assert result, "FastMCP not available (this is expected if not installed). Install with: pip install fastmcp"""

    mcp, chatbot = result
    print("✓ Successfully created FastMCP server")
    print(f"  - Server type: {type(mcp).__name__}")
    print(f"  - ChatBot model: {chatbot.model}")
