# Base class for the "ChatBot" module tests.

import json, os, re, sys, unittest
from json.decoder import JSONDecodeError
from pathlib import Path
from io import StringIO

from apps.chatbot import ChatBot, ChatBotShell
from tests.utils.apps.chatbot.testbase import TestBase

class AITestChatBot(TestBase):
    """
    Parent class for tests of the interactive ChatBot. Note the prefix 
    `AITest` and the file name prefix `ai_test_` rather than the conventional 
    `test_`. Because this test suite takes a long time to run, we separate 
    invocations of the tests into `non-ai-*` and `ai-*` test targets in the 
    `Makefile`, so you can run the conventional, fast tests separately. 
    """
    benchmark_data_dir = Path("tests/data")

    # Encode allowed alternative labels for the ChatBot to return,
    # which are more _conservative_ choices. For example, if we expected 
    # "prescription", it's okay if "emergency" or "other" is returned, as
    # they are handled more _conservatively_. In contrast, if we think
    # the test prompt should be labeled as an emergency, no alternative is
    # acceptable.

    allowed_alt_labels = {
        'emergency': [],
        'prescription': ['emergency', 'other'],
        'appointment': ['prescription', 'other'],
        'other': ['emergency'],
    }

    def run_test(self, data_file: str):
        self.try_queries(
            self.benchmark_data_dir / data_file,
            allowed_alt_labels = AITestChatBot.allowed_alt_labels)
