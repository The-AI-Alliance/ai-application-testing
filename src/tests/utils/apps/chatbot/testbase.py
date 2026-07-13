"""
Common code for tests of the "ChatBot" module using Hypothesis
for property-based testing. https://hypothesis.readthedocs.io/en/latest/
"""

import json
import logging
import os
import random
import re
import time
import unittest
from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO, TextIOWrapper
from pathlib import Path
from typing import Any, Sequence, TypeVar

from apps.chatbot import (
    ChatBot,
    ChatBotSimple,
    ChatBotAgent,
    ChatBotResponseHandler,
    ChatBotShell,
)
from common.collections import dict_pop
from common.json_yaml import decode_json

from .data_ai_tests import BaseAITest, QnATest, ScenarioTest


class LowConfidenceResult:
    """
    Hold a _low confidence result_, i.e., when the prompt has been rated below `rating_threshold`, or the returned
    answer has confidence below `confidence_threshold`, or both, in which case we can't trust that the returned answer
    should be exactly as expected.
    """

    def __init__(
        self,
        query: str,
        reasons: str,
        reply: dict[str, Any],
        test_prompt: BaseAITest,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        self.query = query
        self.reasons = reasons
        self.reply = reply
        self.test_prompt = test_prompt
        self.rating_threshold = rating_threshold
        self.confidence_threshold = confidence_threshold

    def __repr__(self) -> str:
        return f"""LowConfidenceResult(query='{self.query}',reasons='{self.reasons}',reply='{self.reply}',test_prompt='{self.test_prompt}',rating_threshold='{self.rating_threshold}',confidence_threshold={self.confidence_threshold})"""

    def dict(self) -> dict[str, Any]:
        # We don't use __dict__ here because we need to turn the QnATest instance into a dictionary.
        # TODO: Is there a more standard way to make any class recursively convertible to a dictionary?
        return {
            "name": "LowConfidenceResult",
            "query": self.query,
            "reasons": self.reasons,
            "reply": self.reply,
            "test_prompt": self.test_prompt.to_dict(),
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
        }

    def json(self) -> str:
        return json.dumps(self.dict())


TESTDATUM = TypeVar("TESTDATUM")


class TestDataLoader[TESTDATUM](ABC):
    @abstractmethod
    def load_data(self, path: Path) -> list[TESTDATUM]:
        pass


class QnADataLoader(TestDataLoader[QnATest]):
    def load_data(self, path: Path) -> list[QnATest]:
        if not path.exists():
            raise FileNotFoundError(path)

        tests = []
        with path.open("r") as file:
            for line in file:
                ls = line.strip()
                if ls:
                    try:
                        obj = decode_json(ls)
                        query = dict_pop(obj, "query")
                        labels = dict_pop(obj, "labels")
                        actions = dict_pop(obj, "actions")
                        rating = dict_pop(obj, "rating")
                        reason = dict_pop(
                            obj, "reason"
                        )  # Not all records have this, so None will be returned.
                        # What's left in obj at this point are "substitution" keywords, if any,
                        # that we expect to find in the inference results.
                        qnat = QnATest(
                            query, labels, actions, rating, reason, keywords=obj
                        )
                        tests.append(qnat)
                    except ValueError as err:
                        raise ValueError(
                            f"From file {path}, error parsing line: <{line}>"
                        ) from err
        if not len(tests):
            raise ValueError(f"No Q&A pairs were loaded from {path}!")
        return tests


class ScenarioDataLoader(TestDataLoader[ScenarioTest]):
    def load_data(self, path: Path) -> list[ScenarioTest]:
        if not path.exists():
            raise FileNotFoundError(path)

        # The file has to be for a scenario kind we understand...
        kind = None
        known_kinds = ScenarioTest.get_known_scenario_kinds()
        for name, k in known_kinds.items():
            if path.name.find(name) >= 0:
                kind = k
                break
        if not kind:
            raise ValueError(
                f"Input data file {path} doesn't correspond to one of the known scenario types: {known_kinds}"
            )

        with path.open("r") as file:
            lines = file.readlines()
            try:
                objs = decode_json("".join(lines))
                tests = kind.from_dict(objs)
                if isinstance(tests, list):
                    return tests
                else:
                    return [tests]
            except ValueError as err:
                raise ValueError(f"Error parsing JSON in file {path}") from err
        if not len(tests):
            raise ValueError(f"No scenario tests were loaded from {path}!")


class QueryRunner[TESTDATUM](ABC):
    def __init__(
        self,
        chatbot: ChatBot,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        self.chatbot = chatbot
        self.rating_threshold = rating_threshold
        self.confidence_threshold = confidence_threshold

    @abstractmethod
    def run_query(
        self,
        test_prompt: TESTDATUM,
    ):
        pass

    def _check_label(self, expected: Sequence[str], actual: str) -> str:
        return (
            ""
            if actual in expected
            else f"""label '{actual}' not in expected: {expected}."""
        )


class QnAQueryRunner(QueryRunner[QnATest]):
    def __init__(
        self,
        chatbot: ChatBot,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        super().__init__(chatbot, rating_threshold, confidence_threshold)

    def run_query(
        self,
        test_prompt: QnATest,
    ) -> tuple[
        dict[str, Any], dict[str, Any], dict[str, Any], list[LowConfidenceResult]
    ]:
        """
        See src/apps/chatbot/prompts/templates/patient-chatbot.yaml for "requirements".
        Rather than follow the usual approach for failing fast on the first wrong datum,
        we run all the examples and accumulate error messages, then report the results.
        """
        exp_query = test_prompt.query
        exp_labels = test_prompt.labels
        exp_actions = test_prompt.actions
        exp_rating = test_prompt.rating
        exp_keywords = test_prompt.keywords
        prompt = exp_query  # no longer used: if not exp_keywords else exp_query.format_map(exp_keywords)

        metadata = {
            "prompt": prompt,
            "test_prompt": test_prompt.to_dict(),
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
        }
        # On success this will be returned as empty.
        errors = {}
        warnings = {}
        lowConfidenceResults = []

        answer = self.chatbot.query(prompt)
        metadata["answer"] = answer
        try:
            if isinstance(answer, str) or answer.get("error"):
                errors["query_failure"] = (
                    f"unexpected message returned: {answer}, error: {answer.get("error", "")}"
                )
                return metadata, errors, warnings, lowConfidenceResults

            actual_query = str(answer.get("query"))
            actual_rtu = answer.get("reply_to_user")
            actual_content = answer.get("content", {})

            # Sigh, sometimes what we want is in 'reply', other times at the top level.
            actual_reply = actual_content.get("reply", answer)

            actual_label = actual_reply.get("label")
            actual_actions = actual_reply.get("actions", "")

            if isinstance(actual_actions, str):
                actual_actions = re.split(r"\s*,\s*", actual_reply.get("actions", ""))
            actual_keywords = dict(
                [(key, actual_reply.get(key, "")) for key in exp_keywords]
            )
            # We have seen the occasional confidence scores at the content level, rather than inside the reply.
            actual_confidence = actual_reply.get(
                "confidence", actual_content.get("confidence", 1.0)
            )
            # actual_text = actual_reply.get('text', '')

            # We have seen subtle punctuation changes in prompts...
            p2 = re.sub(r"\W", " ", prompt)
            aq = re.sub(r"\W", " ", actual_query)
            if p2 != aq:
                errors["unexpected answer.query"] = f"{prompt} != {actual_query}"

            low_confidence_reasons = []
            if actual_confidence < self.confidence_threshold:
                low_confidence_reasons.append(
                    f"Actual confidence ({actual_confidence}) < confidence threshold ({self.confidence_threshold})."
                )
            if exp_rating < self.rating_threshold:
                low_confidence_reasons.append(
                    f"Expected rating ({exp_rating}) < rating threshold ({self.rating_threshold})."
                )

            if low_confidence_reasons:
                reasons = " ".join(low_confidence_reasons)
                lowConfidenceResults.append(
                    LowConfidenceResult(
                        prompt,
                        reasons,
                        actual_reply,
                        test_prompt,
                        self.rating_threshold,
                        self.confidence_threshold,
                    )
                )
            else:
                err_msg = self._check_label(exp_labels, actual_label)
                if len(err_msg) > 0:
                    errors["unexpected label"] = err_msg
                elif actual_label == "emergency" or actual_label == "other":
                    # Ignore the action if we detect an emergency or other prompt, but check
                    # the returned user response, since we always return with the same reply for
                    # these labels!
                    exp_rtu = ChatBotResponseHandler.fixed_replies[actual_label]
                    if exp_rtu != actual_rtu:
                        errors["unexpected reply_to_user"] = (
                            f"<{exp_rtu}> != <{actual_rtu}>"
                        )
                else:
                    # For the other label cases, IF there are expected actions, do the actual actions contain
                    # at least one item in the expected actions? This is not a rigorous requirement, but should
                    # be adequate. The ChatBot can return more than one actions in a comma-separated list, so
                    # we check at least one of the actual actions is in the set of the expected actions. This
                    # is done by computing the intersection of the sets and expecting it to be non-empty.
                    # Right now, we treat these as warnings, not errors.
                    if exp_actions:
                        exp_set = set(exp_actions)
                        actual_set = set(actual_actions)
                        if not len(actual_set.intersection(exp_set)):
                            warnings["unexpected actions"] = (
                                f"""At least one actual action {actual_actions} not found in the allowed (expected) actions = {exp_actions}."""
                            )

                # For the "keywords", ignore case, since sometimes proper names,
                # can occur with different cases. Also, we check that _expected_
                # values, if any, are present, but also allow for additional actual
                # values. This is because some of the test queries hard-code potential
                # keywords, but we don't "care" if they appear.
                # Right now, we treat these as warnings, not errors.
                missing_kvs = {}
                for key, value in exp_keywords.items():
                    if len(value) == 0:
                        warnings["unexpected keywords"] = (
                            f"BUG: keyword {key} has zero-length value array!"
                        )
                        continue
                    if len(value) > 1:
                        warnings["unexpected keywords"] = (
                            f"TODO: We currently only handle one value in keywords: {key} -> {value}. Ignoring all but the first value!"
                        )
                    expected = value[0].lower()
                    actual = actual_keywords.get(key, "").lower()
                    if not actual.find(expected) >= 0:
                        missing_kvs[key] = f"{expected} vs. {actual}"
                if missing_kvs:
                    warnings["missing keywords"] = missing_kvs
        except TypeError as te:
            print(f"TypeError while parsing answer: {answer}")
            raise te

        return metadata, errors, warnings, lowConfidenceResults


class ScenarioQueryRunner(QueryRunner[ScenarioTest]):
    def __init__(
        self,
        chatbot: ChatBot,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        super().__init__(chatbot, rating_threshold, confidence_threshold)

    def run_query(
        self,
        test_prompt: ScenarioTest,
    ) -> tuple[
        dict[str, Any], dict[str, Any], dict[str, Any], list[LowConfidenceResult]
    ]:
        """
        run a scenario session.
        """
        # test_prompt.scenario
        # test_prompt.inputs
        # test_prompt.successes
        # test_prompt.failures
        # test_prompt.initial_queries
        # test_prompt.start_data
        # test_prompt.end_data
        # test_prompt.errors = {
        #     "required-information": [],
        #     "pre-conditions": [],
        #     "post-conditions": [],
        # }

        metadata = {
            "test_prompt": test_prompt.to_dict(),
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
        }
        # On success these will be returned as empty.
        errors = {}
        warnings = {}
        lowConfidenceResults = []
        raise ValueError("Not yet implemented")

        return metadata, errors, warnings, lowConfidenceResults


class TestBase(unittest.TestCase):
    """
    Base class for tests that need to instantiate a ChatBot, but not necessarily run inference with it.
    Use `TestBaseRunner`, a derived class of this class, for those tests.
    """

    default_confidence_threshold: float = ChatBot.default_confidence_threshold
    default_rating_threshold: int = 4
    log_file_name: str = ""
    log_file: TextIOWrapper | None = None
    which_chatbot_choice: str = ""
    which_chatbot_name: str = ""

    def make_chatbot(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        chatbot_class = (
            ChatBotAgent if TestBase.which_chatbot_choice == "agent" else ChatBotSimple
        )
        self.chatbot = chatbot_class(
            model=self.model,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            output_dir=self.output_dir,
            confidence_level_threshold=self.confidence_threshold,
            response_handler=ChatBotResponseHandler(
                confidence_level_threshold=self.confidence_threshold, logger=logger
            ),
            logger=logger,
        )
        self.shell = ChatBotShell(self.chatbot, stdout=StringIO())

    def setUp(self):
        """
        Initialize the ChatBot and ChatBotShell. Track the number of confident and "low-confidence" results.
        By default, all test data prompts are executed, which can be too slow and expensive for frequent
        unit tests. Override the environment variable `DATA_SAMPLE_RATE` when invoking tests with a value
        between 0.0 (none) and 1.0 (all) to control the amount of test data prompts sampled. (A minimum
        threshold of 5 samples, if available, will be used in all cases.)
        """
        self.model = os.environ.get("MODEL", "ollama_chat/gemma4:e4b")
        self.service_url = os.environ.get("INFERENCE_URL", "http://localhost:11434")
        self.template_dir = os.environ.get(
            "CHATBOT_TEMPLATES_DIR", "apps/chatbot/prompts/templates"
        )
        self.data_dir = os.environ.get("DATA_DIR", "data")
        self.output_dir = os.environ.get("OUTPUT_DIR", "../output/tests")
        self.accumulate_test_results: bool = bool(
            os.environ.get("ACCUMULATE_TEST_ERRORS", False)
        )
        self.sample_rate: float = float(os.environ.get("DATA_SAMPLE_RATE", 1.0))
        self.rating_threshold: int = int(
            os.environ.get("RATING_THRESHOLD", TestBase.default_rating_threshold)
        )
        self.confidence_threshold: float = float(
            os.environ.get(
                "CONFIDENCE_THRESHOLD", TestBase.default_confidence_threshold
            )
        )
        self.verbose: bool = bool(os.environ.get("VERBOSE", False))

        self.samples_count: int = 0
        self.key_results = {"low_confidence_results": [], "errors": [], "warnings": []}

        self.make_chatbot()


class TestBaseRunner(TestBase):
    """
    Base class for ChatBot tests. This class implements a number of extensions to normal
    TestCase behavior, which we added to address some of the challenges of testing stochastic
    AI behaviors. The features include the following:

    * A _confidence threshold_:
        * Minimal testing is done on a response if the confidence score included in the
        response is below a threshold.
    * A _rating threshold_:
        * Similarly, if the generated Q&A pair was validated below a threshold, we don't
        require testing with it to "pass".
    * A flag for _testing all examples_ or not and a _sampling rate_:
        * Running with all the test Q&A pairs and some variable substitutions supported
        takes a very long time, so we support sampling a subset for faster unit test runs.
    * Accumulating all errors and warnings vs. failing fast:
        We have found it useful to accumulate and report all found errors and warnings
        vs. the normal approach of failing fast on the first error.
    """

    total_samples_count = 0
    total_lcr_count = 0
    total_error_count = 0
    total_warning_count = 0
    benchmark_data_dir = Path("tests/data")

    def setUp(self):
        super().setUp()

        d = {
            "step": "setUp",
            "model": self.model,
            "service_url": self.service_url,
            "template_dir": self.template_dir,
            "data_dir": self.data_dir,
            "accumulate_test_results": self.accumulate_test_results,
            "default sample_rate": self.sample_rate,
            "default rating_threshold": self.rating_threshold,
            "default confidence_threshold": self.confidence_threshold,
        }
        print(json.dumps(d), file=TestBaseRunner.log_file)

    def tearDown(self):
        lcr_count = len(self.key_results["low_confidence_results"])
        warning_count = len(self.key_results["warnings"])
        error_count = len(self.key_results["errors"])

        TestBaseRunner.total_samples_count += self.samples_count
        TestBaseRunner.total_lcr_count += lcr_count
        TestBaseRunner.total_warning_count += warning_count
        TestBaseRunner.total_error_count += error_count
        self._dump_key_results(lcr_count, warning_count, error_count)

    def _get_data_file(self, use_case_name: str, kind_label: str) -> Path:
        """
        Look for a "{use_case_name}-{kind_label}.jsonl" or "...json" file.
        If not found, then look for a "{use_case_name}.jsonl" file.
        However, only look for the second
        """
        files = [
            TestBaseRunner.benchmark_data_dir / f"{use_case_name}-{kind_label}.jsonl",
            TestBaseRunner.benchmark_data_dir / f"{use_case_name}-{kind_label}.json",
        ]
        for file in files:
            if file.exists():
                return file
        self.fail(
            f"Data files {files} don't exist for use case {use_case_name} and {kind_label} tests!"
        )

    def _dump_key_results(self, lcr_count: int, warning_count: int, error_count: int):
        lcrs = [lcr.dict() for lcr in self.key_results["low_confidence_results"]]
        d = {
            "step": "tearDown",
            "samples_count": self.samples_count,
            "low_confidence_results": {
                "count": lcr_count,
                "results": lcrs,
            },
            "warnings": {
                "count": warning_count,
                "warnings": self.key_results["warnings"],
            },
            "errors": {
                "count": error_count,
                "errors": self.key_results["errors"],
            },
        }
        js1 = json.dumps(d)
        js = re.sub(r"\n", r"\\n", js1)  # Try to print true JSONL records
        print(js, file=TestBaseRunner.log_file)
        if not self.samples_count:
            raise ValueError("No samples were loaded!")

    @classmethod
    def setUpClass(cls):
        # Determine which ChatBot implementation to use based on environment variable
        TestBase.which_chatbot_choice = os.environ.get("WHICH_CHATBOT", "agent").lower()
        TestBase.which_chatbot_name = (
            "ChatBotAgent"
            if TestBase.which_chatbot_choice == "agent"
            else "ChatBotSimple"
        )
        def_log_dir = "tests/logs"
        log_file_template = os.environ.get("OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE")
        if not log_file_template:
            print(
                "WARNING: OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE undefined. Using default value."
            )
            log_file_template = f"{def_log_dir}/{{TestBase.which_chatbot_name}}-{{class_name}}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        log_file_path = Path(
            log_file_template.format(
                class_name=cls.__name__, which_chatbot=TestBase.which_chatbot_name
            )
        )
        print(f"\n  ** Logging to {log_file_path} ** \n")
        os.makedirs(log_file_path.parent, exist_ok=True)
        TestBaseRunner.log_file = log_file_path.open(
            "a", buffering=1
        )  # append mode, because we _may_ share it across tests.

    @classmethod
    def tearDownClass(cls):
        print("\nTotals:")
        print(f"Which ChatBot:          {TestBase.which_chatbot_choice}")
        print(f"Samples count:          {TestBaseRunner.total_samples_count}")
        print(f"Low-confidence results: {TestBaseRunner.total_lcr_count}")
        print(f"Warning count:          {TestBaseRunner.total_warning_count}")
        print(f"Error count:            {TestBaseRunner.total_error_count}")
        print()
        if TestBaseRunner.log_file:
            TestBaseRunner.log_file.close()
        if TestBaseRunner.total_error_count:
            raise AssertionError(f"{TestBaseRunner.total_error_count} errors reported!")

    def __try_all(
        self,
        method: str,
        use_case_name: str,
        test_data_path: Path,
        test_data: Sequence[BaseAITest],
        query_runner: QueryRunner,
        sample_rate: float,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        """Template method supporting `try_qna_queries` and `try_scenarios`."""
        if not sample_rate > 0.0:
            sample_rate = self.sample_rate

        d = {
            "step": method,
            "which_chatbot": TestBase.which_chatbot_choice,
            "use_case": use_case_name,
            "file_name": str(test_data_path),
            "sample_rate": sample_rate,
            "rating_threshold": rating_threshold,
            "confidence_threshold": confidence_threshold,
            "accumulate_test_results": self.accumulate_test_results,
        }
        print(json.dumps(d), file=TestBaseRunner.log_file)

        samples = (
            self._sample(test_data, sample_rate) if sample_rate < 1.0 else test_data
        )

        last_time = time.time()
        allowed_time_delta = 120  # seconds (NOTE: litellm appears to have an internal timeout of 5-6 minutes.)

        for test_prompt in samples:
            self.samples_count += 1
            metadata, errors, warnings, lowConfidenceResults = query_runner.run_query(
                test_prompt,
            )
            if errors:
                me = errors | metadata  # print the error data first.
                self.key_results["errors"].append(me)
                if self.verbose:
                    print(me)
            if warnings:
                mw = warnings | metadata  # print the warning data first.
                self.key_results["warnings"].append(mw)
                if self.verbose:
                    print(mw)

            if lowConfidenceResults:
                self.key_results["low_confidence_results"].extend(lowConfidenceResults)
                if self.verbose:
                    print(lowConfidenceResults)

            lcr_count = len(self.key_results["low_confidence_results"])
            warning_count = len(self.key_results["warnings"])
            error_count = len(self.key_results["errors"])
            if not self.accumulate_test_results:
                self.assertEqual(
                    0,
                    error_count,
                    f"{error_count} errors for test prompt: {test_prompt}",
                )

            # Logic to detect when it appears the system has deadlocked in some way.
            # If so, then error out.
            now = time.time()
            difference = int(last_time - now)
            self.assertLess(
                difference,
                allowed_time_delta,
                f"Time difference between inference calls, {difference} exceeds allowed time delta {allowed_time_delta}",
            )
            last_time = now

            # Show we aren't dead by printing counts...
            print(
                f"({self.samples_count},{lcr_count},{warning_count},{error_count}) ",
                end="",
            )

    def try_qna_queries(
        self,
        use_case_name: str,
        sample_rate: float = 0.0,
        rating_threshold: int = TestBase.default_rating_threshold,
        confidence_threshold: float = TestBase.default_confidence_threshold,
    ):
        """
        Loop through the sampled test Q&A pairs and try them, i.e., the _simple_
        test data set, as described in `src/tests/data/README.md`.
        If the environment variable `ACCUMULATE_TEST_ERRORS` is true (any value non-empty),
        then accumulate errors and report them at the end. Otherwise, fail on the first prompt
        where we detect errors in the result.
        """
        file_path = self._get_data_file(use_case_name, "qna")
        data_loader = QnADataLoader()
        data = data_loader.load_data(file_path)
        runner = QnAQueryRunner(self.chatbot, rating_threshold, confidence_threshold)

        self.__try_all(
            method="try_qna_queries",
            use_case_name=use_case_name,
            test_data_path=file_path,
            test_data=data,
            query_runner=runner,
            sample_rate=sample_rate,
            rating_threshold=rating_threshold,
            confidence_threshold=confidence_threshold,
        )

    def try_scenarios(
        self,
        use_case_name: str,
        sample_rate: float = 0.0,
        rating_threshold: int = TestBase.default_rating_threshold,
        confidence_threshold: float = TestBase.default_confidence_threshold,
    ):
        """
        Loop through the "session" test data for testing _agent skills_.
        The test data set is described in `src/tests/data/README.md`.
        If the environment variable `ACCUMULATE_TEST_ERRORS` is true (any value non-empty),
        then accumulate errors and report them at the end. Otherwise, fail on the first prompt
        where we detect errors in the result.
        """
        file_path = self._get_data_file(use_case_name, "scenario")
        data_loader = ScenarioDataLoader()
        data = data_loader.load_data(file_path)
        runner = ScenarioQueryRunner(
            self.chatbot, rating_threshold, confidence_threshold
        )

        self.__try_all(
            method="try_scenarios",
            use_case_name=use_case_name,
            test_data_path=file_path,
            test_data=data,
            query_runner=runner,
            sample_rate=sample_rate,
            rating_threshold=rating_threshold,
            confidence_threshold=confidence_threshold,
        )

    def _sample(self, collection: Sequence[Any], sample_rate: float) -> Sequence[Any]:
        """
        The sample_rate (between 0.0 and 1.0) is a pragmatic compromise due to relatively slow local inference
        and expensive inference services. Use a low value for unit tests that are run frequently and need to be fast.
        Use a high value for integration and acceptance tests, usually 1.0, to run most or all of the available test
        prompts, for more exhaustive coverage. However, if the sampled number of test prompts will be less than 5
        (arbitrary), we run the first five available (if the collection has that many...).
        """
        minimum_n = 5
        n = len(collection)
        self.assertTrue(n > 0, f"Collection has no elements! {collection}")
        samples = collection
        if n > minimum_n and sample_rate < 1.0:
            # The samples will be unsorted, but that's okay, as we would like to catch subtle differences
            # in behavior that might be triggered by different ordering.
            k = round(sample_rate * n)
            if k < minimum_n:
                k = minimum_n
            samples = random.sample(collection, k=k)
        return samples
