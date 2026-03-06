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

    script = os.path.basename(__file__)
    description = "Demonstration Patient ChatBot."
    args, logger = setup(script, description, omit={'data-dir'},
        add_arguments = lambda p: p.add_argument("-c", "--confidence-level", 
            type=float, 
            default=0.9, 
            help="What confidence level, reported as part of the inference result, do you consider acceptable for the reply? Default: 0.8 (between 0.0-1.0)"))

    if args.verbose:
        print(f"{description}")
        for key, value in vars(args).items():
            k = key+":"
            print(f"  {k:20s} {value}")
        
    chatbot = ChatBot(
        model = args.model,
        service_url = args.service_url,
        template_dir = args.template_dir,
        confidence_level_threshold = args.confidence_level,
        logger = logger)
    shell = ChatBotShell(chatbot, verbose = args.verbose)
    shell.cmdloop()

if __name__ == "__main__":
    main()
