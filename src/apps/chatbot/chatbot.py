import cmd
import io
import logging
import os
import readline
import sys
from pathlib import Path
from typing import Any

from litellm import completion
from openai import OpenAIError
from common.utils import (
    ensure_dirs_exist,
    get_package_version,
    load_yaml,
)

from .response_handler import ResponseHandler, ChatBotResponseHandler

class ChatBot:

    default_confidence_threshold: float = 0.9
    default_template_file = "patient-chatbot.yaml"

    def __init__(self,
        model: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        confidence_level_threshold: float,
        response_handler: ResponseHandler,
        logger: logging.Logger,
        ):
        """
        Use a `ChatBotResponseHandler` for the response_handler.
        """
        self.model             = model
        self.service_url       = service_url
        self.template_dir      = template_dir
        self.data_dir          = data_dir
        self.logger            = logger
        if confidence_level_threshold < 0.0:
            confidence_level_threshold = 0.0
        if confidence_level_threshold > 1.0:
            confidence_level_threshold = 1.0 # would reject almost all!!
        self.confidence_level_threshold  = confidence_level_threshold
        self.version = get_package_version(self.logger)
        if not self.version:
            self.version = '0.1.0'  # An error occurred that was logged by get_package_version()

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
            error_msg = f"These values can't be None or empty: {', '.join(errors)}"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        ensure_dirs_exist(self.template_dir, self.data_dir)

        if response_handler:
            self.response_handler = response_handler
        else:
            self.response_handler = ChatBotResponseHandler(
                confidence_level_threshold = self.confidence_level_threshold, 
                logger=self.logger)

        self.template_file = Path(template_dir, self.default_template_file)
        if self.logger:
            self.logger.info(f"Using template file: {self.template_file}")
        self.template = load_yaml(self.template_file)
        self.system_prompt = self.template.get('system')
        if not self.system_prompt:
            error_msg = f"The template['system'] is empty: prompt template file {self.template_file}, template:\n{self.template}"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        if self.logger:
            self.logger.info("ChatBot Settings:")
            self.logger.info(f"  version:                    {self.version}")
            self.logger.info(f"  model:                      {self.model}")
            self.logger.info(f"  service_url:                {self.service_url}")
            self.logger.info(f"  template_dir:               {self.template_dir}")
            self.logger.info(f"  data_dir:                   {self.data_dir}")
            self.logger.info(f"  confidence_level_threshold: {self.confidence_level_threshold}")
            self.logger.info(f"  response_handler:           {self.response_handler}")

    def query(self, query: str) -> dict[str,Any] | str:
        """
        Runs a user query and returns either an error message or a dictionary of values
        in the the parsed response. See the `ResponseHandler` object that was passed to
        the constructor for details on the keys and values returned. This method is relatively
        agnostic to the details.

        Args:
            query (str): The user's query

        Returns:
            an error message or a dict with the parsed response.
        """    
        try:
            sysp = f"{self.system_prompt}\n{self.__session_prompt()}"
            messages = [
              {
                "role": "system",
                "content": sysp,
              },
              {
                "role": "user",
                "content": query,
              },
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
            handled = self.response_handler(response)
            if self.logger:
                self.logger.debug(f"response: {handled}")
            return handled

        except OpenAIError as e:
            error_msg = f"OpenAIError thrown: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg

    def __session_prompt(self) -> str:
        if not self.response_handler.responses:
            return ''
        strs = ["SESSION:"]
        count = 1
        for res in self.response_handler.responses:
            query = res.get('query')
            reply = res.get('reply_to_user', res.get('content'))
            strs.append(f"#{count}")
            strs.append(f"query: {query}")
            strs.append(f"reply: {reply}")
            strs.append('\n')
            count += 1
        return '\n'.join(strs)

class ChatBotShell(cmd.Cmd):
    intro = 'Welcome to the patient ChatBot. Type help or ? to list commands.\n'
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
                print(answer+'\n', file=self.stdout)
                if self.verbose:
                    print(f"Full response: {response}\n", file=self.stdout)

    def do_bye(self, arg):
        'Stop the session.'
        print('\nThank you for using the patient ChatBot', file=self.stdout)
        self.close()
        return True

    def close(self):
        pass
