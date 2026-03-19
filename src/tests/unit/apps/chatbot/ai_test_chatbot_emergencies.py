# Tests for the "ChatBot" module with "Emergency" Q&A pairs.

from tests.utils.apps.chatbot.testbase import TestBaseRunner

class AITestChatBotEmergencies(TestBaseRunner):
    """
    The prefix `AITest` and the file name prefix `ai_test_` rather than the 
    conventional `test_`. Because this test suite takes a long time to run, 
    we separate invocations of the tests into `non-ai-*` and `ai-*` test 
    targets in the `Makefile`, so you can run the conventional, fast tests 
    separately. 
    """
    def test_chatbot_emergency_requests(self):
        self.try_queries(TestBaseRunner.benchmark_data_dir / "emergencies.jsonl")

