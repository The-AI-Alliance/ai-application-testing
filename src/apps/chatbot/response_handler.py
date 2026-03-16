import io
import logging
import os
import readline

from litellm.types.utils import ModelResponse
from common.utils import parse_json

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
                * "response": the full input ModelResponse converted to a dictionary so it is JSON-serializable. 
            `_handle()` might modify the values for these keys, add more keys, but not remove these key-values.
        """
        # This is what we care about, assuming nothing fails and we don't need the rest for debugging...
        content = self.__extract_content(response)
        try:
            parsed = parse_json(content)
            full = {
                "query": parsed.get('query'),
                "content": parsed,
                "response": response.to_dict(),
            }
            handled = self._handle(full)
            if isinstance(handled, str):
                return handled
            else:
                self.responses.append(handled)
                if self.logger:
                    self.logger.info(handled)
                return handled
        except ValueError as err:
            return f"""ValueError raised: "{err}" for content = "{content}"."""

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
                if self.logger:
                    self.logger.info(f"Reply's confidence {confidence} < {self.confidence_level_threshold}. Using default 'other' handling. (content = {content})")
                answer = other
            else:
                match label:
                    case 'prescription' | 'appointment':
                        answer = text
                    case 'emergency':
                        answer = self.replies['emergency']
                    case _:
                        answer = other
            
            answer2 = answer.format(prescriptions=prescriptions, body_parts=body_parts)
            processed_response['reply_to_user'] = answer2
            return processed_response
        except Exception as ex:
            return f"ChatBotResponseHandler._handle(): {ex}"
