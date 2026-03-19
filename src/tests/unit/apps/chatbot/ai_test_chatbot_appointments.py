# Tests for the "ChatBot" module with "Appointment" Q&A pairs.

from .testchatbot import AITestChatBot

class AITestChatBotAppointments(AITestChatBot):
    def test_chatbot_appointment_requests(self):
        self.run_test("appointments.jsonl")
