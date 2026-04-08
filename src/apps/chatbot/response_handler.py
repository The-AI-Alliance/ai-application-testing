import logging
from typing import Any

class ResponseHandler():
    """
    Understands the specific format of responses and 
    does appropriate deconstruction and handling.
    """
    def __init__(self, confidence_level_threshold: float, logger: logging.Logger):
        self.logger = logger
        self.responses = []
        self.confidence_level_threshold = confidence_level_threshold

    def __call__(self, response: dict[str,Any]) -> dict[str,Any]:
        """
        This method deconstructs the response and then calls _handle() with it, 
        which should be overridden by derived classes to perform the desired handling.

        Args:
            response (ModelResponse): The LiteLLM response

        Returns:
            If successful a `dict[str,Any]`
            parsed from the response, with the following entries:
                * "query": the user query
                * "content": the "core" content we care about, as JSON. Can be `None` on error.
                * "response": the full input ModelResponse converted to a dictionary so it is JSON-serializable. 
            `_handle()` might modify the values for these keys, add more keys, but not remove these key-values.
        """
        # This is what we care about, assuming nothing fails and we don't need the rest for debugging...
        try:
            handled = self._handle(response)
            self.responses.append(handled)
            if "error" in handled:
                self.logger.error(handled)
            else:
                self.logger.info(handled)
            return handled
        except ValueError as err:
            return {"error": f"""ValueError raised: "{err}" for response = "{response}"."""}

    def _handle(self, processed_response: dict[str,Any]) -> dict[str,Any]:
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
    fixed_replies = {
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
    
    def __init__(self, confidence_level_threshold: float, logger: logging.Logger):
        super().__init__(confidence_level_threshold=confidence_level_threshold, logger=logger)

    def _handle(self, processed_response: dict[str,Any]) -> dict[str,Any]:
        """
        _Usually_, we return one of our "fixed" replies to the user. Exceptions are
        when we think the generated text is likely (high confidence value...) to be a good response.
        This method has to do a lot of careful processing of the `processed_response` dictionary,
        because the content is unpredictable.
        """
        if processed_response.get("error"):
            return processed_response

        other    = str(self.fixed_replies.get('other', ''))  # str() for type checking!
        query    = processed_response.get('query', "?")
        content  = processed_response.get('content')
        if content == None:
            processed_response["error"] = "No 'content' in processed response.",
            processed_response['reply_to_user'] = other
        elif isinstance(content, str):
            processed_response['reply_to_user'] = other
        elif isinstance(content, dict):
            reply = content.get('reply')
            if reply and isinstance(reply, dict):
                answer        = ''
                label         = reply.get('label')
                prescriptions = reply.get('prescriptions', '')
                body_parts    = reply.get('body_parts', '')
                actions       = reply.get('actions', '')
                confidence    = reply.get('confidence', 0.0)
                text          = str(reply.get('text', ''))   # str() for type checking!
                if confidence < self.confidence_level_threshold:
                    self.logger.info(f"Reply's confidence {confidence} < {self.confidence_level_threshold}. Using default 'other' handling. (content = {content})")
                    answer = other
                else:
                    match label:
                        case 'prescription' | 'appointment':
                            answer = text
                        case 'emergency':
                            answer = str(self.fixed_replies.get('emergency', ''))   # str() for type checking!
                        case _:
                            answer = other
        
                answer2 = answer.format(prescriptions=prescriptions, body_parts=body_parts)
                processed_response['reply_to_user'] = answer2
            else:
                processed_response['reply_to_user'] = other
        
        return processed_response
        