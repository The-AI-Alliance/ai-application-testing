"""
MCP Server implementation for the Patient ChatBot using FastMCP.

This module creates and configures the MCP server that exposes
chatbot functionality through the Model Context Protocol.
"""
import logging
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

from apps.chatbot import ChatBot
from common.utils import setup


def create_mcp_server(
    model: str,
    service_url: str,
    template_dir: str,
    data_dir: str,
    confidence_level_threshold: float = 0.9,
    logger: logging.Logger | None = None
) -> tuple[FastMCP, ChatBot] | None:
    """
    Create and configure an MCP server for the chatbot using FastMCP.
    
    Args:
        model: The LLM model to use
        service_url: The URL of the inference service
        template_dir: Directory containing prompt templates
        data_dir: Directory containing data files
        confidence_level_threshold: Minimum confidence level for responses
        logger: Optional logger for debugging
        
    Returns:
        A tuple of (mcp, chatbot)
    """
    
    # Create the chatbot instance
    chatbot = ChatBot(
        model=model,
        service_url=service_url,
        template_dir=template_dir,
        data_dir=data_dir,
        confidence_level_threshold=confidence_level_threshold,
        logger=logger
    )
    
    # Create the FastMCP server
    mcp = FastMCP("patient-chatbot")
    
    # Register tools using the chatbot instance
    @mcp.tool()
    async def query_chatbot(query: str) -> str:
        """
        Query the patient chatbot with a user message.
        
        This tool allows you to interact with a healthcare chatbot that can handle:
        - Prescription refill requests
        - Emergency situations
        - Appointment scheduling
        - General healthcare inquiries
        
        Args:
            query: The user's question or request to the chatbot
            
        Returns:
            A response containing the chatbot's reply and metadata about the interaction
        """
        if not query:
            return "Error: No query provided"
        
        if logger:
            logger.info(f"MCP tool query_chatbot called with: {query}")
        
        try:
            response = chatbot.query(query)
            
            if isinstance(response, str):
                # Error occurred
                return f"Error: {response}"
            
            # Extract the reply to user
            reply_to_user = response.get('reply_to_user', 'No reply generated')
            content = response.get('content', {})
            reply_info = content.get('reply', {})
            label = reply_info.get('label', 'unknown')
            confidence = reply_info.get('confidence', 0.0)
            
            # Format the response
            result = f"Reply: {reply_to_user}\n\nMetadata:\n- Label: {label}\n- Confidence: {confidence:.2f}"
            
            if logger:
                logger.info(f"MCP tool query_chatbot response: {result}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing chatbot query: {str(e)}"
            if logger:
                logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    async def get_chatbot_session_history() -> str:
        """
        Get the current session history from the chatbot.
        
        This tool retrieves the conversation history for the current chatbot session,
        showing all previous queries and responses.
        
        Returns:
            A formatted list of all queries and responses in the current session
        """
        if logger:
            logger.info("MCP tool get_chatbot_session_history called")
        
        try:
            responses = chatbot.response_handler.responses
            
            if not responses:
                return "No session history available. The chatbot has not processed any queries yet."
            
            history_lines = ["Session History:", "=" * 50]
            
            for idx, response in enumerate(responses, 1):
                query = response.get('query', 'N/A')
                reply = response.get('reply_to_user', 'N/A')
                content = response.get('content', {})
                reply_info = content.get('reply', {})
                label = reply_info.get('label', 'unknown')
                confidence = reply_info.get('confidence', 0.0)
                
                history_lines.extend([
                    f"\n#{idx}",
                    f"Query: {query}",
                    f"Reply: {reply}",
                    f"Label: {label}",
                    f"Confidence: {confidence:.2f}",
                    "-" * 50
                ])
            
            return "\n".join(history_lines)
            
        except Exception as e:
            error_msg = f"Error retrieving session history: {str(e)}"
            if logger:
                logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    async def get_chatbot_info() -> str:
        """
        Get information about the chatbot configuration.
        
        This tool returns details about the chatbot's current configuration,
        including the model being used, service URL, and confidence threshold.
        
        Returns:
            Configuration details of the chatbot
        """
        if logger:
            logger.info("MCP tool get_chatbot_info called")
        
        try:
            info = {
                "model": chatbot.model,
                "service_url": chatbot.service_url,
                "template_dir": chatbot.template_dir,
                "confidence_threshold": chatbot.confidence_level_threshold,
                "template_file": str(chatbot.template_file),
                "session_length": len(chatbot.response_handler.responses)
            }
            
            info_lines = [
                "Chatbot Configuration:",
                "=" * 50,
                f"Model: {info['model']}",
                f"Service URL: {info['service_url']}",
                f"Template Directory: {info['template_dir']}",
                f"Template File: {info['template_file']}",
                f"Confidence Threshold: {info['confidence_threshold']:.2f}",
                f"Current Session Length: {info['session_length']} queries"
            ]
            
            return "\n".join(info_lines)
            
        except Exception as e:
            error_msg = f"Error retrieving chatbot info: {str(e)}"
            if logger:
                logger.error(error_msg)
            return error_msg
    
    if logger:
        logger.info(f"FastMCP server created with model: {model}")
    
    return mcp, chatbot


def main():
    """
    Main entry point for running the MCP server standalone.
    """
    tool = os.path.basename(__file__)
    description = "FastMCP Server for Patient ChatBot"
    
    def add_args(parser):
        parser.add_argument(
            "-c", "--confidence-threshold",
            type=float,
            default=0.9,
            help="Confidence threshold level threshold (0.0-1.0). Default: 0.9"
        )
    
    args, logger = setup(
        tool,
        description,
        epilog="Run the chatbot as an MCP server for integration with MCP clients.",
        add_arguments=add_args
    )
    
    if args.verbose:
        print(f"{description}")
        for key, value in vars(args).items():
            k = key + ":"
            print(f"  {k:20s} {value}")
    
    try:
        result = create_mcp_server(
            model=args.model,
            service_url=args.service_url,
            template_dir=args.template_dir,
            data_dir=args.data_dir,
            confidence_level_threshold=args.confidence_threshold,
            logger=logger
        )
        
        if result is None:
            sys.exit(1)
        
        mcp, chatbot = result
        
        if logger:
            logger.info("Starting FastMCP server...")
        
        # Run the FastMCP server
        mcp.run()
        
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
