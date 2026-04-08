import os
import sys
import io
import json
import glob
import logging
from pathlib import Path

from common.utils import setup
from apps.chatbot import ChatBot, ChatBotSimple, ChatBotAgent, ChatBotShell, ChatBotResponseHandler

def main():
    """
    Main entry point for the interactive Patient ChatBot shell.
    
    For MCP server mode, use: python -m apps.chatbot.mcp_server.server
    See src/apps/chatbot/mcp_server/README.md for details.
    
    For OpenAI-compatible API server mode, use: python -m apps.chatbot.api_server.server
    See src/apps/chatbot/api_server/README.md for details.
    """

    def add_custom_arguments(p):
        p.add_argument(
            "-c", "--confidence-threshold",
            type=float,
            default=0.9,
            help="What confidence threshold level, reported as part of the inference result, do you consider acceptable for the reply? Default: 0.9 (between 0.0-1.0)")
        p.add_argument(
            "-w", "--which-chatbot",
            type=str,
            choices=['agent', 'simple'],
            default='agent',
            help="Which ChatBot implementation to use: 'agent' for ChatBotAgent (LangChain Deep Agents) or 'simple' for ChatBotSimple (direct LiteLLM). Default: agent")
    
    tool = os.path.basename(__file__)
    description = "Demonstration Patient ChatBot."
    args, logger = setup(
        tool,
        description,
        epilog="The data directory is used to store the ChatBot GUI session information.",
        omit_arguments={'use-cases'},
        add_arguments=add_custom_arguments)

    # Instantiate the appropriate ChatBot implementation
    chatbot_class = ChatBotAgent if args.which_chatbot == 'agent' else ChatBotSimple

    if args.verbose:
        print(f"\n{description}")
        for key, value in vars(args).items():
            k = key+":"
            print(f"  {k:25s} {value}")
        print(f"\nUsing the {chatbot_class.__name__} implementation.")
        
    chatbot = chatbot_class(
        model = args.model,
        service_url = args.service_url,
        template_dir = args.template_dir,
        data_dir = args.data_dir,
        confidence_level_threshold = args.confidence_threshold,
        response_handler = ChatBotResponseHandler(
            confidence_level_threshold = args.confidence_threshold,
            logger = logger),
        logger = logger)
    shell = ChatBotShell(chatbot, verbose = args.verbose)
    shell.cmdloop()

if __name__ == "__main__":
    main()
