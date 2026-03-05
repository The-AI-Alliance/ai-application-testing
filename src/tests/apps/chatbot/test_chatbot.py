# Unit tests for the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st
import json, os, re, sys, unittest
from json.decoder import JSONDecodeError
from pathlib import Path
from io import StringIO

from apps.chatbot import ChatBot, ChatBotShell
from tests.apps.chatbot.test_base import TestBase

class TestChatBot(TestBase):
    """
    Test the interactive ChatBot.
    """

    benchmark_data_dir = Path("tests/data")

    @given(
        st.sampled_from(TestBase.place_holders['prescriptions']), 
        st.sampled_from(TestBase.place_holders['body_parts']))
    def test_chatbot_prescription_requests(self, prescription: str, body_part: str):
        self.try_queries(
            self.benchmark_data_dir / "prescriptions.jsonl",
            {'prescriptions': prescription, 'body_parts': body_part}, 
            rating_threshold=4, 
            confidence_threshold=0.6)

    @given(
        st.sampled_from(TestBase.place_holders['prescriptions']), 
        st.sampled_from(TestBase.place_holders['body_parts']))
    def test_chatbot_emergency_requests(self, prescription: str, body_part: str):
        chatbot, shell = self.make_chatbot()
        self.try_queries(
            self.benchmark_data_dir / "emergencies.jsonl",
            {'prescriptions': prescription, 'body_parts': body_part}, 
            rating_threshold=4, 
            confidence_threshold=0.6)

    @given(
        st.sampled_from(TestBase.place_holders['prescriptions']), 
        st.sampled_from(TestBase.place_holders['body_parts']))
    def test_chatbot_appointment_requests(self, prescription: str, body_part: str):
        chatbot, shell = self.make_chatbot()
        self.try_queries(
            self.benchmark_data_dir / "appointments.jsonl",
            {'prescriptions': prescription, 'body_parts': body_part}, 
            rating_threshold=4, 
            confidence_threshold=0.6)

    @given(
        st.sampled_from(TestBase.place_holders['prescriptions']), 
        st.sampled_from(TestBase.place_holders['body_parts']))
    def test_chatbot_other_requests(self, prescription: str, body_part: str):
        chatbot, shell = self.make_chatbot()
        self.try_queries(
            self.benchmark_data_dir / "others.jsonl",
            {'prescriptions': prescription, 'body_parts': body_part}, 
            rating_threshold=4, 
            confidence_threshold=0.6)

