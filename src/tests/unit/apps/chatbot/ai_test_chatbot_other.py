# Tests for the "ChatBot" module with "Other" Q&A pairs.

from .testchatbot import AITestChatBot

class AITestChatBotOthers(AITestChatBot):
    def test_chatbot_other_requests(self):
        self.run_test("others.jsonl")
