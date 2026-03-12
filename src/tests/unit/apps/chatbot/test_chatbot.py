# Tests for the "ChatBot" module.

# Normally, we use hypothesis for tests, but in this case, we just have a
# few variables to iterate over and it's better not to have Hypothesis go
# through its iterations to find minimal failing example inputs, given the
# expense of inference.
# from hypothesis import given, strategies as st
import json, os, re, sys, unittest
from json.decoder import JSONDecodeError
from pathlib import Path
from io import StringIO

from apps.chatbot import ChatBot, ChatBotShell
from tests.utils.apps.chatbot.testbase import TestBase

class TestChatBot(TestBase):
    """
    Test the interactive ChatBot.
    """

    benchmark_data_dir = Path("tests/data")

    def run_test(self, data_file: str):
        for prescription in TestBase.place_holders['prescriptions']:
            for body_part in TestBase.place_holders['body_parts']:
                self.try_queries(
                    self.benchmark_data_dir / data_file,
                    {'prescriptions': prescription, 'body_parts': body_part})

    def test_chatbot_prescription_requests(self):
        self.run_test("prescriptions.jsonl")

    def test_chatbot_emergency_requests(self):
        self.run_test("emergencies.jsonl")

    def test_chatbot_appointment_requests(self):
        self.run_test("appointments.jsonl")

    def test_chatbot_other_requests(self):
        self.run_test("others.jsonl")

