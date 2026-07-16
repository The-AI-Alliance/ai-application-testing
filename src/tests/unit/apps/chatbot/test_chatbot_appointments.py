# Tests for the "ChatBot" module with "Appointment" Q&A pairs.

import pytest
from tests.utils.apps.chatbot.testbase import TestBaseRunner

class AITestChatBotAppointments(TestBaseRunner):
    """
    The prefix `AITest` and the annotation `@pytest.mark.ai` indicates this
    test uses AI inference and therefore it takes a long time to run. We use
    the annotation to separate invocations of the tests into `*-tests-non-ai` and
    `*-tests-ai` test targets in the `Makefile`, so you can run the conventional,
    fast tests separately. In fact, the non-AI tests are what gets executed by
    default for the `unit-tests` target and also PR checks.
    """

    @pytest.mark.ai
    @pytest.mark.appointments
    def test_chatbot_appointment_requests(self):
        self.try_scenarios("appointments")
