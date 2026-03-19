"""
Simple test script to verify MCP server functionality.

This script tests that the MCP server can be imported and initialized
with FastMCP.
"""

import logging, os, sys
from pathlib import Path

# Add src to path for imports
#sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from apps.chatbot import ChatBot
from apps.chatbot.mcp_server.server import create_mcp_server
from tests.utils.apps.chatbot.testbase import TestBase

class TestMCPServer(TestBase):
    """
    Test the MCP Server for the ChatBot.
    """

    def test_chatbot_creation(self):
        """Test that ChatBot can be created. This is effectively done by the TestBase.setUp() method."""
        print("✓ Successfully created ChatBot instance")
        print(f"  - Model: {self.chatbot.model}")
        print(f"  - Service URL: {self.chatbot.service_url}")
        print(f"  - Template dir: {self.chatbot.template_dir}")
        print(f"  - Data dir: {self.chatbot.data_dir}")
        print(f"  - Confidence threshold: {self.chatbot.confidence_level_threshold}")

    def test_mcp_server_creation(self):
        """Test that MCP server can be created with FastMCP."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)
        
        result = create_mcp_server(
            model=self.chatbot.model,
            service_url=self.chatbot.service_url,
            template_dir=self.chatbot.template_dir,
            data_dir=self.chatbot.data_dir,
            confidence_level_threshold=self.chatbot.confidence_level_threshold,
            logger=logger
        )
        
        self.assertIsNotNone(result, """
            ⚠ FastMCP not available (this is expected if not installed)
            Install with: pip install fastmcp""")
        
        mcp, chatbot = result
        print("✓ Successfully created FastMCP server")
        print(f"  - Server type: {type(mcp).__name__}")
        print(f"  - ChatBot model: {chatbot.model}")

