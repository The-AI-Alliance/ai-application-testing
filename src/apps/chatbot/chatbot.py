import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from common.utils import (
    ensure_dirs_exist,
    get_package_version,
    load_yaml,
)

from .response_handler import ResponseHandler, ChatBotResponseHandler

class ChatBot(ABC):
    """
    Base class for ChatBot implementations.
    Provides common initialization and abstract methods for query processing.
    """

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
        template_file: str = '',
        ):
        """
        Initialize the ChatBot base class.
        
        Args:
            model: The model identifier
            service_url: The inference service URL
            template_dir: Directory containing prompt templates
            data_dir: Directory for data storage
            confidence_level_threshold: Minimum confidence threshold (0.0-1.0)
            response_handler: Handler for processing responses
            logger: Logger instance
            template_file: Optional template file name (defaults to default_template_file)
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

        template_filename = template_file if template_file else self.default_template_file
        self.template_file = Path(template_dir, template_filename)
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
            self.logger.info(f"{self.__class__.__name__} Settings:")
            self.logger.info(f"  version:                    {self.version}")
            self.logger.info(f"  model:                      {self.model}")
            self.logger.info(f"  service_url:                {self.service_url}")
            self.logger.info(f"  template_dir:               {self.template_dir}")
            self.logger.info(f"  data_dir:                   {self.data_dir}")
            self.logger.info(f"  confidence_level_threshold: {self.confidence_level_threshold}")
            self.logger.info(f"  response_handler:           {self.response_handler}")

    def query(self, query: str) -> dict[str,Any]:
        """
        Runs a user query and returns a dictionary of values in the parsed
        response or an error message. 

        Args:
            query (str): The user's query

        Returns:
            If successful, a dict with the parsed response is returned:
            ```
            {
              "query":    query,
              "content":  parsed_text_response,
              "response": whole_response_dict
            }
            ```
            If unsuccessful, `{ "error": "error_message" }` is returned.
        """

        response = self._do_query(query)
        handled = self.response_handler(response)
        if self.logger:
            self.logger.debug(f"handled response: {handled}")
        return handled

    @abstractmethod
    def _do_query(self, query: str) -> dict[str,Any]:
        pass

    def _session_prompt(self) -> str:
        """
        Build a session prompt from previous responses.
        Protected method that can be used by subclasses.
        """
        # TODO: Eliminate this and use session tools instead.
        # if not self.response_handler.responses:
        #     return ''
        # strs = ["SESSION:"]
        # count = 1
        # for res in self.response_handler.responses:
        #     query = res.get('query')
        #     reply = res.get('reply_to_user', res.get('content'))
        #     strs.append(f"#{count}")
        #     strs.append(f"query: {query}")
        #     strs.append(f"reply: {reply}")
        #     strs.append('\n')
        #     count += 1
        # return '\n'.join(strs)
        return ''

# Made with Bob
