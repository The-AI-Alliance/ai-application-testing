# Tests for the "ChatBot" module with "Emergency" Q&A pairs.

from .testchatbot import AITestChatBot

class AITestChatBotEmergencies(AITestChatBot):
    def test_chatbot_emergency_requests(self):
        self.run_test("emergencies.jsonl")
