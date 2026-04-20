import json, re
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from typing import Any, Generic, TypeVar

from litellm.types.utils import ModelResponse

RESPONSE = TypeVar("RESPONSE")

class ResponseParser(ABC, Generic[RESPONSE]):
    """
    Abstraction for the different types of responses returned by
    agent and inference libraries we use use, e.g., LiteLLM, LangChain, etc.
    """
    @abstractmethod
    def parse(self, query: str, response: RESPONSE) -> dict[str,Any]:
        pass

    def __parse_content(self, content: str) -> dict[str,Any]:
        try:
            # hack: Gemma responses sometimes start with "google:" or "json" 
            # and sometimes it wraps in Markdown: "```json ...```".
            content1 = re.sub('^google:', '', content)
            content2 = re.sub('^json', '', content1)
            content3 = re.sub('^```json *', '', content2)
            content4 = re.sub('```$', '', content3)
            return json.loads(content4)
        except JSONDecodeError as err:
            return {"text": content4}
    
    def _make_full_response(self, query: str, content: str, response_dict: dict[str,Any]) -> dict[str,Any]:
        """
        Tries to parse the response content to extract the content
        we expect to find. 

        On success, returns this dictionary:
        ```python
        {
            "query":    query, 
            "text":  parsed_content_field, # Text to optionally show to the user.
            ... other key-value pairs in the response
            "response": response_dict,
        }
        ```
        On failure, returns this dictionary:
        ```python
        {
            "error":          error_message, 
            "query":          query, 
            "content_string": content_field,
            "response":       response_dict,
        }
        ```
        """

        parsed = self.__parse_content(content)
        assert isinstance(parsed, dict)
        if "error" in parsed:
            parsed["content_string"] = content

        parsed.update({
            "query":    query, 
            "response": response_dict,
        })
        return parsed

class ModelResponseParser(ResponseParser[ModelResponse]):
    def parse(self, query: str, response: ModelResponse) -> dict[str,Any]:
        """
        Takes a LiteLLM `ModelResponse` and extracts the 
        JSON-formatted string content we care about, returning
        it in a dictionary with other content from the response.
        ```json
        {
          "id": "chatcmpl-09f35520-2558-4a3f-8379-a717109a178c",
          "created": 1775669892,
          "model": "ollama/gemma4:e4b",
          "object": "chat.completion",
          "system_fingerprint": null,
          "choices": [
            {
              "finish_reason": "stop",
              "index": 0,
              "message": {
                "content": {
                  "understanding": "prescription_refill",
                  "suggestions": [
                    "Do you have your insurance card and the prescription bottle handy?",
                    "Which pharmacy do you usually use?",
                    "Do you have the name of the medication and the dosage strength?",
                    "Are you calling from your doctor's office or from home?"
                  ],
                  "response": "To help you with your prescription refill, could you please provide me with a few more details? Do you have the name of the medication, the dosage, and which pharmacy you plan to use?"
                },
                "role": "assistant",
                "tool_calls": null,
                "function_call": null,
                "provider_specific_fields": null
              }
            }
          ],
          "usage": {
            "completion_tokens": 126,
            "prompt_tokens": 25,
            "total_tokens": 151,
            "completion_tokens_details": null,
            "prompt_tokens_details": null
          }
        }
        ```
        """
        response_dict = response.to_dict()
        # A hacky way way to get the "content"!!!
        content = response_dict['choices'][0]['message']['content']  # ty: ignore[not-subscriptable]
        return self._make_full_response(query, content, response_dict)

class DeepAgentResponseParser(ResponseParser[dict[str,Any]]):
    def parse(self, query: str, response: dict[str,Any]) -> dict[str,Any]:
        """
        Takes a LangChain Deep Agents dict response and extracts the 
        JSON-formatted string content we care about, returning
        it in a dictionary with other content from the response.

        Here is an example response:

        ```python
        {'messages': [HumanMessage(...), AIMessage(...)]}
        ```

        Here is a full example converted to JSON, where `obj.model_dump_json()`
        was called on each element in the array. (The corresponding `obj.model_dump()`
        method returns a dictionary.)

        ```json
        {
          "messages": [
            {
              "content": "... user's query ...",
              "additional_kwargs": {},
              "response_metadata": {},
              "type": "human",
              "name": null,
              "id": "93621a38-2dbf-4419-92c0-738ebceb4c0c"
            },
            {
              "content": "... reply ...",
              "additional_kwargs": {},
              "response_metadata": {
                "model": "gemma4:e4b",
                "created_at": "2026-04-08T14:01:02.475545Z",
                "done": true,
                "done_reason": "stop",
                "total_duration": 33242340375,
                "load_duration": 21962041333,
                "prompt_eval_count": 5611,
                "prompt_eval_duration": 10370078583,
                "eval_count": 21,
                "eval_duration": 578368915,
                "logprobs": null,
                "model_name": "gemma4:e4b",
                "model_provider": "ollama"
              },
              "type": "ai",
              "name": null,
              "id": "lc_run--019d6d65-0122-7450-acd2-74a251d45ca5-0",
              "tool_calls": [],
              "invalid_tool_calls": [],
              "usage_metadata": {
                "input_tokens": 5611,
                "output_tokens": 21,
                "total_tokens": 5632
              }
            }
          ]
        }
        ```
        """
        messages = response.get("messages")
        if not messages:
            return {"error": f"response doesn't have 'messages': {response}"}
        content = messages[-1].content
        response_dict = {"messages": [m.model_dump() for m in messages]}
        return self._make_full_response(query, content, response_dict)
