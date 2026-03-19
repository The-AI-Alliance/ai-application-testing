# Tests for the "ChatBot" module with Prescription Q&A pairs.

from .testchatbot import AITestChatBot

class AITestChatBotPrescriptions(AITestChatBot):
    def test_chatbot_prescription_requests(self):
        self.run_test("prescriptions.jsonl")
