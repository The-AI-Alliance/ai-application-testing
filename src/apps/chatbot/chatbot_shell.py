import cmd
import sys
import logging

from .chatbot import ChatBot

class ChatBotShell(cmd.Cmd):
    """Interactive shell for the ChatBot."""
    
    intro = '\nWelcome to the patient ChatBot. Type help or ? to list commands. Use "bye" to quit.\n'
    prompt = 'input> '

    def __init__(self, chatbot: ChatBot, logger: logging.Logger | None = None, verbose: bool = False, stdin = sys.stdin, stdout = sys.stdout):
        super().__init__(stdin=stdin, stdout=stdout)
        self.chatbot = chatbot
        self.verbose = verbose
        self.logger  = logger 

    def default(self, line):
        'Process the user prompt'
        if line == 'EOF':
            return self.do_bye(line)
        elif line:
            print("One moment...", file=self.stdout)
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
                    print(f"ERROR! {error}\n", file=self.stdout)
                if self.verbose:
                    print(f"Full response: {response}\n", file=self.stdout)

    def do_bye(self, arg):
        'Stop the session.'
        print('\nThank you for using the patient ChatBot', file=self.stdout)
        self.close()
        return True

    def close(self):
        pass

# Made with Bob
