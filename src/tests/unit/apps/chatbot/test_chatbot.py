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

    place_holders = {
        'prescriptions': ['prilosec', 'xanax', 'prozac'],
        'body_parts':    ['stomach', 'head', 'chest'],
        'vaccines':      ['flu', 'COVID'],
    }

    # Encode allowed alternative labels for the ChatBot to return,
    # which are more _conservative_ choices. For example, if we expected 
    # "prescription", it's okay if "emergency" or "other" is returned, as
    # they are handled more _conservatively_. In contrast, if we think
    # the test prompt should be labeled as an emergency, no alternative is
    # acceptable.

    allowed_alt_labels = {
        "emergency": [],
        "prescription": ["emergency", "other"],
        "appointment": ["prescription", "other"],
        "other": [],
    }

    def run_test(self, data_file: str):
        self.try_queries(
            self.benchmark_data_dir / data_file,
            place_holders = TestChatBot.place_holders,
            allowed_alt_labels = TestChatBot.allowed_alt_labels,
            accumulate_errors = True)

    def test_chatbot_prescription_requests(self):
        self.run_test("prescriptions.jsonl")

    def test_chatbot_emergency_requests(self):
        self.run_test("emergencies.jsonl")

    def test_chatbot_appointment_requests(self):
        self.run_test("appointments.jsonl")

    def test_chatbot_other_requests(self):
        self.run_test("others.jsonl")

