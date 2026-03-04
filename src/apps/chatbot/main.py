import os
import sys
import io
import json
import glob
import logging
from pathlib import Path

from common.utils import setup
from apps.chatbot import ChatBot, ChatBotShell

def main():

    script = os.path.basename(__file__)
    description = "Demonstration Patient ChatBot."
    args, logger = setup(script, description)

    chatbot = ChatBot(
        model = args.model,
        service_url = args.service_url,
        template_dir = args.template_dir,
        data_dir = args.data_dir,
        logger = logger)
    shell = ChatBotShell(chatbot)
    shell.cmdloop()

if __name__ == "__main__":
    main()
