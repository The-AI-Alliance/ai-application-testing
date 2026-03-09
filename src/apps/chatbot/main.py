import os
import sys
import io
import json
import glob
import logging
from pathlib import Path

from common.utils import setup
from apps.chatbot import ChatBot, ChatBotShell, ResponseHandler

def main():
    """
    Main entry point for the interactive Patient ChatBot shell.
    
    For MCP server mode, use: python -m apps.chatbot.mcp_server.server
    See src/apps/chatbot/mcp_server/README.md for details.
    
    For OpenAI-compatible API server mode, use: python -m apps.chatbot.api_server.server
    See src/apps/chatbot/api_server/README.md for details.
    """

    tool = os.path.basename(__file__)
    description = "Demonstration Patient ChatBot."
    args, logger = setup(
        tool,
        description,
        epilog="The data directory is used to store the ChatBot GUI session information.",
        add_arguments=lambda p: p.add_argument(
            "-c", "--confidence-threshold",
            type=float,
            default=0.9,
            help="What confidence threshold level, reported as part of the inference result, do you consider acceptable for the reply? Default: 0.9 (between 0.0-1.0)"))

    if args.verbose:
        print(f"{description}")
        for key, value in vars(args).items():
            k = key+":"
            print(f"  {k:20s} {value}")
        
    chatbot = ChatBot(
        model = args.model,
        service_url = args.service_url,
        template_dir = args.template_dir,
        data_dir = args.data_dir,
        confidence_level_threshold = args.confidence_threshold,
        logger = logger)
    shell = ChatBotShell(chatbot, verbose = args.verbose)
    shell.cmdloop()

if __name__ == "__main__":
    main()
