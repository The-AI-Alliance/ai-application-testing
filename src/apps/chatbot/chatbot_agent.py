import logging
from pathlib import Path
from typing import Any

from .chatbot import ChatBot
from .response_handler import ResponseHandler
from .response_parser import DeepAgentResponseParser
from .skills.appointments import APPOINTMENT_TOOLS, get_appointment_manager
from .skills.date_time import DATE_TIME_TOOLS

from deepagents import create_deep_agent

class ChatBotAgent(ChatBot):
    """
    ChatBot implementation using LangChain Deep Agents framework.
    
    This implementation uses the Deep Agents SDK for building agents with
    built-in capabilities for task planning, file systems for context management,
    subagent-spawning, and long-term memory.
    
    See: https://docs.langchain.com/oss/python/deepagents/overview
    """

    default_template_file = "patient-chatbot-agent.yaml"

    def __init__(self,
        model: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        output_dir: str,
        confidence_level_threshold: float,
        response_handler: ResponseHandler,
        logger: logging.Logger,
        ):
        """
        Initialize the Deep Agents-based ChatBot implementation.
        Use a `ChatBotResponseHandler` for the response_handler.
        """
        # LangChain Deep Agents uses "provider:model". Also, if
        # we use `ollama_chat` in the model argument, remove the "_chat".
        model2 = model.replace("/", ":").replace("_chat", "")

        super().__init__(
            model=model2,
            service_url=service_url,
            template_dir=template_dir,
            data_dir=data_dir,
            output_dir=output_dir,
            confidence_level_threshold=confidence_level_threshold,
            response_handler=response_handler,
            logger=logger,
            template_file=self.default_template_file
        )
        self.response_parser = DeepAgentResponseParser()
        if model2.find('gpt-oss') >= 0:
            err_msg = "The gpt-oss models served by ollama don't currently work with LangChain's Deep Agents!"
            logger.error(err_msg)
        
        # Set up appointment tools with the correct data directory
        appointments_file = Path(self.output_dir) / "appointments.jsonl"
        appointment_manager = get_appointment_manager(
            file_path = appointments_file,
            logger = self.logger)
        
        self.agent = create_deep_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=APPOINTMENT_TOOLS+DATE_TIME_TOOLS,
        )

        self.logger.info("ChatBotAgent initialized (Deep Agents integration pending)")

    def _do_query(self, query: str) -> dict[str,Any]:
        # Build context from session history
        session = self._session_prompt()
        messages = { 
            "messages": [
                {
                  "role": "user",
                  "content": query,
                },
            ],
        }

        # Invoke the agent
        response = self.agent.invoke(messages)
        parsed = self.response_parser.parse(query, response)
        self.logger.debug(f"response = <{response}>, parsed = <{parsed}>.")
        return parsed

# Made with Bob
