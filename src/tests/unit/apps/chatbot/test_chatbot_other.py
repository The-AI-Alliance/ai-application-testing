# Tests for the "ChatBot" module with "Other" Q&A pairs.

import os
import pytest
from pathlib import Path
from tests.utils.apps.chatbot.chatbot_test_base import ChatBotTestWithInference

@pytest.mark.ai
def test_chatbot_other_requests():
    """
    The annotation `@pytest.mark.ai` indicates this test uses AI inference and
    therefore it takes a long time to run. We use the annotation to separate
    invocations of the tests into `*-tests-non-ai` and `*-tests-ai` test targets
    in the `Makefile`, so you can run the conventional, fast tests separately.
    In fact, the non-AI tests are what gets executed by default for the `unit-tests`
    target and also PR checks.
    """
    data_dir = os.environ.get("TEST_DATA_DIR", "src/tests/data")
    cbtb = ChatBotTestWithInference(data_dir = Path(data_dir))
    cbtb.try_qna_queries("others")
