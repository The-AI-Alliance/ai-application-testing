"""
MCP Server implementation for the Patient ChatBot.

This module creates and configures the MCP server that exposes
chatbot functionality through the Model Context Protocol.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None
    stdio_server = None

from apps.chatbot import ChatBot
from common.utils import setup
from .tools import register_chatbot_tools


def create_mcp_server(
    model: str,
    service_url: str,
    template_dir: str,
    data_dir: str,
    confidence_level_threshold: float = 0.9,
    logger: logging.Logger | None = None
) -> tuple[Any, ChatBot] | None:
    """
    Create and configure an MCP server for the chatbot.
    
    Args:
        model: The LLM model to use
        service_url: The URL of the inference service
        template_dir: Directory containing prompt templates
        data_dir: Directory containing data files
        confidence_level_threshold: Minimum confidence level for responses
        logger: Optional logger for debugging
        
    Returns:
        A tuple of (server, chatbot) if MCP is available, None otherwise
    """
    if not MCP_AVAILABLE:
        error_msg = "MCP SDK not available. Install with: pip install mcp"
        if logger:
            logger.error(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        return None
    
    # Create the chatbot instance
    chatbot = ChatBot(
        model=model,
        service_url=service_url,
        template_dir=template_dir,
        data_dir=data_dir,
        confidence_level_threshold=confidence_level_threshold,
        logger=logger
    )
    
    # Create the MCP server
    server = Server("patient-chatbot")
    
    # Register the chatbot tools
    register_chatbot_tools(server, chatbot, logger)
    
    if logger:
        logger.info(f"MCP server created with model: {model}")
    
    return server, chatbot


async def run_mcp_server(
    model: str,
    service_url: str,
    template_dir: str,
    data_dir: str,
    confidence_level_threshold: float = 0.9,
    logger: logging.Logger | None = None
) -> None:
    """
    Run the MCP server using stdio transport.
    
    Args:
        model: The LLM model to use
        service_url: The URL of the inference service
        template_dir: Directory containing prompt templates
        data_dir: Directory containing data files
        confidence_level_threshold: Minimum confidence level for responses
        logger: Optional logger for debugging
    """
    result = create_mcp_server(
        model=model,
        service_url=service_url,
        template_dir=template_dir,
        data_dir=data_dir,
        confidence_level_threshold=confidence_level_threshold,
        logger=logger
    )
    
    if result is None:
        return
    
    server, chatbot = result
    
    if logger:
        logger.info("Starting MCP server on stdio...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

def main():
    """
    Main entry point for running the MCP server standalone.
    """
    script = os.path.basename(__file__)
    description = "MCP Server for Patient ChatBot"
    
    args, logger = setup(
        script,
        description,
        epilog="Run the chatbot as an MCP server for integration with MCP clients.",
        add_arguments=lambda p: p.add_argument(
            "-c", "--confidence-threshold",
            type=float,
            default=0.9,
            help="Confidence threshold level threshold (0.0-1.0). Default: 0.9"
        )
    )
    
    if args.verbose:
        print(f"{description}")
        for key, value in vars(args).items():
            k = key + ":"
            print(f"  {k:20s} {value}")
    
    try:
        asyncio.run(run_mcp_server(
            model=args.model,
            service_url=args.service_url,
            template_dir=args.template_dir,
            data_dir=args.data_dir,
            confidence_level_threshold=args.confidence_threshold,
            logger=logger
        ))
    except KeyboardInterrupt:
        if logger:
            logger.info("MCP server stopped by user")
        print("\nMCP server stopped")
    except Exception as e:
        error_msg = f"Error running MCP server: {e}"
        if logger:
            logger.error(error_msg)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
