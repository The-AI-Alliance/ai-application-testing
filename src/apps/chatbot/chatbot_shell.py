import cmd
import sys
import logging
from rich.status import Status

from .chatbot import ChatBot

# Source for history management adapted from - https://stackoverflow.com/a/39495060
# Posted by Martijn Pieters, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-10, License - CC BY-SA 3.0

import os.path
try:
    import readline
except ImportError:
    readline = None # ty: ignore

class ChatBotShell(cmd.Cmd):
    """Interactive shell for the ChatBot."""

    histfile = os.path.expanduser('~/.chatbotshell_history')
    histfile_size = 1000

    def preloop(self):
        if readline and os.path.exists(ChatBotShell.histfile):
            readline.read_history_file(ChatBotShell.histfile)

    def postloop(self):
        if readline:
            readline.set_history_length(ChatBotShell.histfile_size)
            readline.write_history_file(ChatBotShell.histfile)

    intro = '\nWelcome to the patient ChatBot. Type help or ? to list commands. Use "bye" to quit.\n'
    prompt = 'input> '

    def __init__(self, chatbot: ChatBot, verbose: bool = False, stdin = sys.stdin, stdout = sys.stdout):
        super().__init__(stdin=stdin, stdout=stdout)
        self.chatbot = chatbot
        self.verbose = verbose
        self.logger  = chatbot.logger 

    def default(self, line):
        'Process the user prompt'
        if line == 'EOF':
            return self.do_bye(line)
        elif line:
            # print("One moment...", file=self.stdout)
            with Status("One moment...") as status:
                response = self.chatbot.query(line)
            if isinstance(response, str):
                print(f"Something went wrong: {response}")
                print("Try your query again or report an issue to the development team:")
                print("  https://github.com/The-AI-Alliance/ai-application-testing")
            else:
                answer = response.get('reply_to_user', '')
                if answer:
                    print(answer+'\n', file=self.stdout)
                error = response.get('error', '')
                if error:
                    self.logger.error(error)
                    print(f"ERROR! {error}\n", file=self.stdout)
                if self.verbose:
                    self.logger.info(f"answer = {answer}, full response = {response}")
                    print(f"Full response: {response}\n", file=self.stdout)

    def emptyline(self):
        """Don't repeat the last command, just show the prompt again."""
        pass

    def do_bye(self, arg):
        """Stop the session."""
        print('\nThank you for using the patient ChatBot', file=self.stdout)
        self.close()
        return True

    def close(self):
        pass

# Made with Bob
