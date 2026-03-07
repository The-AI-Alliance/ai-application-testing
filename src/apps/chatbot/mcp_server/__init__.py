"""
MCP Server for the Patient ChatBot application.

This module provides an MCP (Model Context Protocol) server that exposes
the chatbot functionality as tools that can be used by MCP clients.
"""

from .server import create_mcp_server
from .tools import register_chatbot_tools

__all__ = ['create_mcp_server', 'register_chatbot_tools']

# Made with Bob
