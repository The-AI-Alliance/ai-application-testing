import logging
from typing import Any

from litellm import completion
from openai import OpenAIError

from .chatbot import ChatBot
from .response_handler import ResponseHandler

class ChatBotSimple(ChatBot):
    """
    Simple ChatBot implementation using direct LiteLLM completion calls.
    """

    default_template_file = "patient-chatbot-simple.yaml"

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
        Initialize the simple ChatBot implementation.
        Use a `ChatBotResponseHandler` for the response_handler.
        """
        super().__init__(
            model=model,
            service_url=service_url,
            template_dir=template_dir,
            data_dir=data_dir,
            confidence_level_threshold=confidence_level_threshold,
            response_handler=response_handler,
            logger=logger,
            template_file=self.default_template_file
        )

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
            sysp = f"{self.system_prompt}\n{self._session_prompt()}"
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
