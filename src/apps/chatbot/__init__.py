import cmd
import io
import json
import glob
import logging
import os
import readline
import sys
from pathlib import Path
from pprint import pprint

from litellm import completion
from openai import OpenAIError
from common.utils import (
    setup, 
    load_yaml,
    ensure_dirs_exist,
    make_full_prompt,
    extract_content,
    logging_level_to_string,
)

class ChatBot:

    def_template_file = "patient-chatbot.yaml"
    replies = {
        "refill":
            "Okay, I have your request for a refill for {prescriptions}. I will check your records and get back to you within the next business day.",
        "emergency":
            "It appears you are having an urgent or emergency situation. Please call 911 immediately!",
        "appointment":
            "Okay, I have your request about an appointment. I will check your records and get back to you within the next business day.",
        "appointment-schedule":
            "Okay, I have your request to schedule an appointment. Here are some available dates and times...",
        "appointment-reschedule":
            "Okay, I have your request to reschedule an appointment. Here are some available dates and times...",
        "appointment-information":
            "Okay, I have your request for information about your scheduled appointments. Here they are...",
    }

    def __init__(self, 
        model: str, 
        service_url: str, 
        template_dir: str, 
        data_dir: str, 
        logger: logging.Logger = None):
        self.model        = model
        self.service_url  = service_url
        self.template_dir = template_dir
        self.data_dir     = data_dir
        self.logger       = logger
        self.queries_responses = []

        errors = []
        if not self.model:
            errors.append('model')
        if not self.service_url:
            errors.append('service_url')
        if not self.template_dir:
            errors.append('template_dir')
        if not self.data_dir:
            errors.append('data_dir')
        if errors:
            err_msg = f"These values can't be None or empty: {', '.join(errors)}"
            if self.logger:
                self.logger.error(err_msg)
            raise ValueError(err_msg)

        ensure_dirs_exist(self.template_dir, self.data_dir)

        self.template_file = Path(template_dir, self.def_template_file)
        if self.logger:
            self.logger.info(f"Using template file: {self.template_file}")
        self.template = load_yaml(self.template_file)
        self.system_prompt = self.template.get('system')
        if not self.system_prompt:
            err_msg = f"The template['system'] is empty: prompt template file {self.template_file}, template:\n{template}"
            if self.logger:
                self.logger.error(err_msg)
            raise ValueError(err_msg)

    def query(self, query: str) -> dict[str,str]:
        """Validate a single generated datum; does the question match the label?"""    
        try:
            messages = [
              {
                "role": "system",
                "content": self.system_prompt,
              },
              {
                "role": "user",
                "content": query,
                }
            ]
            if self.logger:
                self.logger.debug(str(messages))
            stream = False #True if self.model.find('_chat') > 0 else False
            response = completion(
                model = self.model, 
                messages = messages, 
                api_base = self.service_url, 
                stream = stream,
                verbose = False,
                format = "json",
            )
            json = response.json()
            actual = extract_content(response)
            full = {"query": query, "response": actual, "json": json}
            self.queries_responses.append(full)
            if self.logger:
                self.logger.info(full)
            return full

        except OpenAIError as e:
            if self.logger:
                self.logger.error(f"OpenAIError thrown: {e}")
            raise e

class ChatBotShell(cmd.Cmd):
    intro = 'Welcome to the patient ChatBot. Type help or ? to list commands.\n'
    prompt = 'input> '

    def __init__(self, chatbot: ChatBot, verbose: bool = False, stdin = sys.stdin, stdout = sys.stdout):
        super().__init__(stdin=stdin, stdout=stdout)
        self.chatbot = chatbot
        self.verbose = verbose
        if self.verbose:
            pprint(vars(self))

    def default(self, line):
        'Process the user prompt'
        if line == 'EOF':
            return self.do_bye(line)
        elif line:
            print("One moment...", file=self.stdout)
            answer = self.chatbot.query(line)
            if self.verbose:
                print(answer, file=self.stdout)
            else:
                print(answer.get('response'), file=self.stdout)

    def do_bye(self, arg):
        'Stop the session.'
        print('\nThank you for using the patient ChatBot', file=self.stdout)
        self.close()
        return True

    def close(self):
        pass
