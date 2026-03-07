"""
MCP Tools for the Patient ChatBot.

This module defines the tools that are exposed through the MCP server,
allowing external clients to interact with the chatbot functionality.
"""

import logging
from typing import Any, Dict

from apps.chatbot import ChatBot, ChatBotResponseHandler


def register_chatbot_tools(server: Any, chatbot: ChatBot, logger: logging.Logger | None = None) -> None:
    """
    Register chatbot tools with the MCP server.
    
    Args:
        server: The MCP server instance
        chatbot: The ChatBot instance to use for queries
        logger: Optional logger for debugging
    """
    
    @server.call_tool()
    async def query_chatbot(arguments: Dict[str, Any]) -> list[Dict[str, Any]]:
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
        query = arguments.get("query", "")
        
        if not query:
            return [{
                "type": "text",
                "text": "Error: No query provided"
            }]
        
        if logger:
            logger.info(f"MCP tool query_chatbot called with: {query}")
        
        try:
            response = chatbot.query(query)
            
            if isinstance(response, str):
                # Error occurred
                return [{
                    "type": "text",
                    "text": f"Error: {response}"
                }]
            
            # Extract the reply to user
            reply_to_user = response.get('reply_to_user', 'No reply generated')
            content = response.get('content', {})
            
            # Format the response
            result = {
                "reply": reply_to_user,
                "query": content.get('query', query),
                "label": content.get('reply', {}).get('label', 'unknown'),
                "confidence": content.get('reply', {}).get('confidence', 0.0),
            }
            
            if logger:
                logger.info(f"MCP tool query_chatbot response: {result}")
            
            return [{
                "type": "text",
                "text": f"Reply: {reply_to_user}\n\nMetadata:\n- Label: {result['label']}\n- Confidence: {result['confidence']:.2f}"
            }]
            
        except Exception as e:
            error_msg = f"Error processing chatbot query: {str(e)}"
            if logger:
                logger.error(error_msg)
            return [{
                "type": "text",
                "text": error_msg
            }]
    
    @server.call_tool()
    async def get_chatbot_session_history(arguments: Dict[str, Any]) -> list[Dict[str, Any]]:
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
                return [{
                    "type": "text",
                    "text": "No session history available. The chatbot has not processed any queries yet."
                }]
            
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
            
            return [{
                "type": "text",
                "text": "\n".join(history_lines)
            }]
            
        except Exception as e:
            error_msg = f"Error retrieving session history: {str(e)}"
            if logger:
                logger.error(error_msg)
            return [{
                "type": "text",
                "text": error_msg
            }]
    
    @server.call_tool()
    async def get_chatbot_info(arguments: Dict[str, Any]) -> list[Dict[str, Any]]:
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
            
            return [{
                "type": "text",
                "text": "\n".join(info_lines)
            }]
            
        except Exception as e:
            error_msg = f"Error retrieving chatbot info: {str(e)}"
            if logger:
                logger.error(error_msg)
            return [{
                "type": "text",
                "text": error_msg
            }]

# Made with Bob
