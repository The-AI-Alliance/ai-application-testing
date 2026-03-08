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
from litellm.types.utils import ModelResponse
from openai import OpenAIError
from common.utils import (
    ensure_dirs_exist,
    extract_content,
    get_package_version,
    load_yaml,
    parse_json,
)

class ResponseHandler():
    """
    Understands the specific format of responses and 
    does appropriate deconstruction and handling.
    """
    def __init__(self, confidence_level_threshold: float, logger: logging.Logger | None = None):
        self.logger = logger
        self.responses = []
        self.confidence_level_threshold = confidence_level_threshold

    def __call__(self, response: ModelResponse) -> dict[str,any] | str:
        """
        This method deconstructs the response and then calls _handle() with it, 
        which should be overridden by derived classes to perform the desired handling.

        Args:
            response (ModelResponse): The LiteLLM response

        Returns:
            A `Union` that is either a `str` for an error message or a `dict[str,any]`
            parsed from the response, with the following entries:
                * "query": the user query
                * "content": the "core" content we care about, as JSON. Can be `None` on error.
                * "response": the full input ModelResponse. 
            `_handle()` might modify the values for these keys, add more keys, but not remove these key-values.
        """
        # This is what we care about, assuming nothing fails and we don't need the rest for debugging...
        content = self.__extract_content(response)
        parsed = parse_json(content)
        if isinstance(parsed, str):
            return parsed
        else:
            full = {
                "query": parsed.get('query'),
                "content": parsed,
                "response": response,
            }
            handled = self._handle(full)
            if isinstance(handled, str):
                return handled
            else:
                self.responses.append(handled)
                if self.logger:
                    self.logger.info(handled)
                return handled

    def __extract_content(self, litellm_reponse: ModelResponse) -> str:
        """Returns the JSON-formatted string content we care about."""
        response_dict = litellm_reponse.to_dict()
        # TODO: There must be an easier way to get the "content"!!!
        content = response_dict['choices'][0]['message']['content']
        return content

    def _handle(self, processed_response: dict[str,any]) -> dict[str,any] | str:
        """
        Override this method for additional handling. It is not necessary to call this parent implementation.
        It is okay to modify the values for these keys, but not remove any of them. It is also okay to 
        add more key-value pairs. Derived classes will want to drill into the `content` key-value, 
        which should reflect the instructions provided in the prompt template used by the application.
        If an error occurs, return an error message instead.
        """
        return processed_response

    def __repr__(self):
        # Return the name of the actual class.
        return f"{type(self).__name__}(confidence_level_threshold = {self.confidence_level_threshold}, #responses = {len(self.responses)})"

class ChatBotResponseHandler(ResponseHandler):
    """
    Handle responses for the ChatBot, reflecting the details for the expected responses,
    as defined in the prompt file. We follow a policy of actually using the model's response text if the
    confidence is > 90%. Otherwise, we use these "canned" responses.
    """
    team_member_reply = """
I will ask a member of the healthcare team to get back to you as soon as possible. 
This could be the next business day. If you are having an emergency, please call 911 immediately!"""

    # If a value is a dictionary, it corresponds to the expected `actions` value, with `default` used if the actions
    # is empty or not found here.
    replies = {
        "prescription": {
            "refill":  f"I have your request for a refill for {{prescriptions}}. {team_member_reply}",
            "inquiry": f"I have your request for information concerning {{prescriptions}}. {team_member_reply}",
            "other":   f"I have your query concerning {{prescriptions}}. {team_member_reply}",
        },
        "emergency":
            f"It sounds like you may be having an emergency or urgent situation. If so, please call 911 or visit an urgent care center immediately!",
        "appointment": {
            "schedule":   f"I have your request to schedule an appointment. Here are some available dates and times...",
            "reschedule": f"I have your request to reschedule an appointment. Here are some available dates and times...",
            "inquiry":    f"I have your request for appointment information. Here is a list of your scheduled appointments...",
            "other":      f"I have your appointment query. I will get back to you within the next business day.",
        },
        "other": team_member_reply,
    }
    
    def __init__(self, confidence_level_threshold: float, logger: logging.Logger | None = None):
        super().__init__(confidence_level_threshold=confidence_level_threshold, logger=logger)

    def _handle(self, processed_response: dict[str,any]) -> dict[str,any] | str:
        """
        _Usually_, we return one of our "canned" replies to the user. Exceptions are
        when we think the generated text is likely (high confidence value...) to be a good response.
        """
        try:
            content       = processed_response.get('content')
            query         = content.get('query')
            reply         = content.get('reply')
            label         = reply.get('label')
            prescriptions = reply.get('prescriptions', '')
            body_parts    = reply.get('body_parts', '')
            actions       = reply.get('actions', '')
            confidence    = reply.get('confidence', 0.0)
            text          = reply.get('text', '')
            
            other  = self.replies.get('other')
            answer = None
            if confidence < self.confidence_level_threshold:
                self.logger.info(f"Reply's confidence {confidence} < {self.confidence_level_threshold}. Using default 'other' handling. (content = {content})")
                answer = other
            else:
                match label:
                    case 'prescription' | 'appointment':
                        answer = text
                    case 'emergency':
                        answer = self.replies.get('emergency')
                    case _:
                        answer = other
            
            answer2 = answer.format(prescriptions=prescriptions, body_parts=body_parts)
            processed_response['reply_to_user'] = answer2
            return processed_response
        except Exception as ex:
            return f"ChatBotResponseHandler._handle(): {ex}"

class ChatBot:

    default_confidence_threshold: float = 0.9
    default_template_file = "patient-chatbot.yaml"

    def __init__(self,
        model: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        confidence_level_threshold: float = default_confidence_threshold,
        response_handler: ResponseHandler | None = None,
        logger: logging.Logger | None = None):
        """
        If the `response_handler` is `None`, a `ChatBotResponseHandler` will be used.
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
            error_msg = f"The template['system'] is empty: prompt template file {self.template_file}, template:\n{template}"
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

    def query(self, query: str) -> dict[str,any] | str:
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
                answer = response.get('reply_to_user')
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
