"""
Common code for tests of the "ChatBot" module using Hypothesis
for property-based testing. https://hypothesis.readthedocs.io/en/latest/
"""

import json
import logging
import os
import random
import re
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum, auto
from io import StringIO
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
from common.json_yaml import decode_json_dict, decode_json_list

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

        # TODO: Use extract_jsonl_list isntead of looping through the lines
        # and calling decode_json_dict??
        tests = []
        with path.open("r") as file:
            for line in file:
                ls = line.strip()
                if ls:
                    try:
                        obj = decode_json_dict(ls)
                        query = dict_pop(obj, "query")
                        labels = dict_pop(obj, "labels")
                        actions = dict_pop(obj, "actions")
                        rating = dict_pop(obj, "rating")
                        reason = dict_pop(obj, "reason")  # Not all records have this, so None will be returned.
                        # What's left in obj at this point are "substitution" keywords, if any,
                        # that we expect to find in the inference results.
                        qnat = QnATest(query, labels, actions, rating, reason, keywords=obj)
                        tests.append(qnat)
                    except ValueError as err:
                        raise ValueError(f"From file {path}, error parsing line: <{line}>") from err
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
                objs = decode_json_list("".join(lines))
                if not len(objs):
                    raise ValueError(f"No scenario tests were loaded from {path}!")
                return [kind.from_dict(obj) for obj in objs]
            except ValueError as err:
                raise ValueError(f"Error parsing JSON in file {path}") from err


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
        return "" if actual in expected else f"""label '{actual}' not in expected: {expected}."""


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
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[LowConfidenceResult]]:
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
                errors["query_failure"] = f"unexpected message returned: {answer}, error: {answer.get("error", "")}"
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
            actual_keywords = dict([(key, actual_reply.get(key, "")) for key in exp_keywords])
            # We have seen the occasional confidence scores at the content level, rather than inside the reply.
            actual_confidence = actual_reply.get("confidence", actual_content.get("confidence", 1.0))
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
                        errors["unexpected reply_to_user"] = f"<{exp_rtu}> != <{actual_rtu}>"
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
                        warnings["unexpected keywords"] = f"BUG: keyword {key} has zero-length value array!"
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
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[LowConfidenceResult]]:
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


# class syntax
class WhichChatBot(StrEnum):
    SIMPLE = auto()
    AGENT = auto()

    def chatbot_name(self):
        return f"ChatBot{self.capitalize()}"


class ChatBotTestBase:
    """
    Base class for tests that need to instantiate a ChatBot, but not to run
    inference with it, which is expensive. Use the derived class,
    `ChatBotTestWithInference`, for tests that make inference calls.
    """

    default_which_chatbot_str = "agent"
    default_service_url = "http://localhost:11434"

    default_chatbot_dir = "src/apps/chatbot"
    default_chatbot_template_dir = f"{default_chatbot_dir}/prompts/templates"
    default_chatbot_data_dir = f"{default_chatbot_dir}/data"
    default_output_dir = "output/tests"
    default_log_file_template = (
        f"src/tests/logs/{{which_chatbot}}-{{class_name}}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    )

    default_data_sample_rate = 1.0
    default_accumulate_test_results = False
    default_rating_threshold = 4
    default_confidence_threshold = ChatBot.default_confidence_threshold

    def __init__(
        self,
        which_chatbot: WhichChatBot | None = None,
        model: str = "",
        service_url: str = "",
        template_dir: Path | None = None,
        data_dir: Path | None = None,
        output_dir: Path | None = None,
        log_file_path: Path | None = None,
        data_sample_rate: float | None = None,
        accumulate_test_results: bool | None = None,
        rating_threshold: int = 0,
        confidence_threshold: float = 0.0,
        verbose: bool | None = None,
    ):
        """
        Initialize the ChatBot and ChatBotShell. The default values for the arguments shown
        used to indicate that corresponding environment variables should be read to determine
        the values.

        Some of the values here, like `rating_threshold` and `data_sample_rate`
        will only be needed by derived classes that invoke inference. However, these values are
        initialized by this class, rather than the derived classes, because they are needed to
        construct ChatBot instances. See `ChatBotTestWithInference` for a description of these
        parameters.

        When the default values for input arguments are used, corresponding environment variable
        definitions are used instead to initialize the values.

        Here is the mapping of the arguments to environment variables and the default values
        the will be used if a valid input isn't provided _and_ the environment variable isn't
        set. Note that all paths shown are _relative_ to `src`.

        | Argument | Environment Variable | Default Value |
        | :------- | :------------------- | :------------ |
        | `which_chatbot` | `WHICH_CHATBOT` | `WhichChatBot.AGENT` |
        | `model` | `MODEL` | None - will raise an exception if not provided! |
        | `service_url` | `INFERENCE_URL` | http://localhost:11434 |
        | `template_dir` | `CHATBOT_TEMPLATES_DIR` | `apps/chatbot/prompts/templates` |
        | `data_dir` | `DATA_DIR` | `apps/chatbot/data` |
        | `output_dir` | `OUTPUT_DIR` | `../output/tests` |
        | `data_sample_rate` | `DATA_SAMPLE_RATE` | 1.0 |
        | `accumulate_test_results` | `ACCUMULATE_TEST_ERRORS` | `False` |
        | `rating_threshold` | `RATING_THRESHOLD` | 4 (out of 5) |
        | `confidence_threshold` | `CONFIDENCE_THRESHOLD` | 0.9 |
        | `verbose` | `VERBOSE` | `False` |

        Finally, if the `log_file_path` isn't specified, a _template_ is used, either
        the value of the environment variable `OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE` or
        `tests/logs/{{which_chatbot}}-{{class_name}}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl`.

        This is a special-purpose, custom "log" file. We also use the Python `logging` framework
        for "general" logging.
        """
        self.which_chatbot: WhichChatBot = (
            which_chatbot
            if which_chatbot
            else WhichChatBot(os.environ.get("WHICH_CHATBOT", ChatBotTestBase.default_which_chatbot_str).lower())
        )
        self.model: str = model if model else os.environ["MODEL"]  # no default!
        self.service_url: str = (
            service_url if service_url else os.environ.get("INFERENCE_URL", ChatBotTestBase.default_service_url)
        )
        self.template_dir: Path = (
            template_dir
            if template_dir
            else Path(os.environ.get("CHATBOT_TEMPLATES_DIR", ChatBotTestBase.default_chatbot_template_dir))
        )
        self.data_dir: Path = (
            data_dir if data_dir else Path(os.environ.get("DATA_DIR", ChatBotTestBase.default_chatbot_data_dir))
        )
        self.output_dir: Path = (
            output_dir if output_dir else Path(os.environ.get("OUTPUT_DIR", ChatBotTestBase.default_output_dir))
        )
        self.data_sample_rate: float = (
            data_sample_rate
            if data_sample_rate is not None
            else float(os.environ.get("DATA_SAMPLE_RATE", ChatBotTestBase.default_data_sample_rate))
        )
        self.accumulate_test_results: bool = (
            accumulate_test_results
            if accumulate_test_results is not None
            else bool(os.environ.get("ACCUMULATE_TEST_ERRORS", ChatBotTestBase.default_accumulate_test_results))
        )
        self.rating_threshold: int = (
            rating_threshold
            if rating_threshold > 0
            else int(os.environ.get("RATING_THRESHOLD", ChatBotTestBase.default_rating_threshold))
        )
        self.confidence_threshold: float = (
            confidence_threshold
            if confidence_threshold > 0.0
            else float(os.environ.get("CONFIDENCE_THRESHOLD", ChatBotTestBase.default_confidence_threshold))
        )
        self.verbose: bool = verbose if verbose is not None else bool(os.environ.get("VERBOSE", False))

        if log_file_path:
            self.log_file_path = Path(log_file_path)
        else:
            log_file_template = os.environ.get("OUTPUT_LOGS_TESTS_DIRFILE_TEMPLATE")
            if not log_file_template:
                log_file_template = ChatBotTestBase.default_log_file_template
            self.log_file_path = Path(
                log_file_template.format(
                    class_name=self.__class__.__name__, which_chatbot=self.which_chatbot.chatbot_name()
                )
            )
        print(f"\n  ** Logging to {self.log_file_path} ** \n")
        os.makedirs(self.log_file_path.parent, exist_ok=True)
        self.log_file = self.log_file_path.open(
            "a", buffering=1
        )  # append mode, because we _may_ share it across tests.

        self.make_chatbot()

    def make_chatbot(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        chatbot_class = ChatBotAgent if self.which_chatbot == WhichChatBot.AGENT else ChatBotSimple
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


class ChatBotTestWithInference(ChatBotTestBase):
    """
    A support class for ChatBot tests that invoke inference. This class implements a number
    of extensions to normal test behavior, which we added to address some of the challenges
    of testing stochastic AI behaviors. The features include the following:

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

    NOTE: We use the prefix convention `AITest` and the annotation `@pytest.mark.ai` in
    concrete derived classes of `ChatBotTestWithInference` to indicate that the test uses AI inference
    and it therefore takes a long time to run. Specifically, the annotation is used to
    separate invocations of the tests into `*-tests-non-ai` and `*-tests-ai` test targets
    in the `Makefile`, so you can run the conventional, fast tests separately. In fact,
    the non-AI tests are what gets executed by default for the `unit-tests` target and
    also PR checks.
    """

    def __init__(
        self,
        which_chatbot: WhichChatBot | None = None,
        model: str = "",
        service_url: str = "",
        template_dir: Path | None = None,
        data_dir: Path | None = None,
        output_dir: Path | None = None,
        log_file_path: Path | None = None,
        data_sample_rate: float | None = None,
        accumulate_test_results: bool | None = None,
        rating_threshold: int = 0,
        confidence_threshold: float = 0.0,
        verbose: bool | None = None,
    ):
        super().__init__(
            which_chatbot=which_chatbot,
            model=model,
            service_url=service_url,
            template_dir=template_dir,
            data_dir=data_dir,
            output_dir=output_dir,
            log_file_path=log_file_path,
            data_sample_rate=data_sample_rate,
            accumulate_test_results=accumulate_test_results,
            rating_threshold=rating_threshold,
            confidence_threshold=confidence_threshold,
            verbose=verbose,
        )

        self.samples_count = 0
        self.low_confidence_results = []
        self.errors = []
        self.warnings = []

        d = {
            "step": "initialize",
            "model": self.model,
            "service_url": self.service_url,
            "template_dir": str(self.template_dir),
            "data_dir": str(self.data_dir),
            "output_dir": str(self.output_dir),
            "log_file_path": str(self.log_file_path),
            "accumulate_test_results": self.accumulate_test_results,
            "data_sample_rate": self.data_sample_rate,
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
        }
        print(json.dumps(d), file=self.log_file)

    def finish(self):
        """Call after all the test samples have been executed."""
        lcr_count = len(self.low_confidence_results)
        warnings_count = len(self.warnings)
        errors_count = len(self.errors)
        print("\nTotals:")
        print(f"Which ChatBot:                {self.which_chatbot.chatbot_name()}")
        print(f"Samples count:                {self.samples_count}")
        print(f"Low-confidence results count: {lcr_count}")
        print(f"Warning count:                {warnings_count}")
        print(f"Error count:                  {errors_count}")
        print()
        lcrs = [lcr.dict() for lcr in self.low_confidence_results]
        d = {
            "step": "finish",
            "samples_count": self.samples_count,
            "low_confidence_results": {
                "count": lcr_count,
                "results": lcrs,
            },
            "warnings": {
                "count": warnings_count,
                "warnings": self.warnings,
            },
            "errors": {
                "count": errors_count,
                "errors": self.errors,
            },
        }
        js1 = json.dumps(d)
        js = re.sub(r"\n", r"\\n", js1)  # Try to print true JSONL records
        print(js, file=self.log_file)

        if self.log_file:
            self.log_file.close()
        assert len(self.errors) == 0, f"{len(self.errors)} errors reported!"

    def _get_data_file(self, use_case_name: str, kind_label: str) -> Path:
        """
        Look for a "{use_case_name}-{kind_label}.jsonl" or "...json" file.
        If not found, then look for a "{use_case_name}.jsonl" file.
        However, only look for the second
        """
        files = [
            self.data_dir / f"{use_case_name}-{kind_label}.jsonl",
            self.data_dir / f"{use_case_name}-{kind_label}.json",
        ]
        for file in files:
            if file.exists():
                return file
        assert False, f"Data files {files} don't exist for use case {use_case_name} and {kind_label} tests!"

    def __try_all_samples(
        self,
        method: str,
        use_case_name: str,
        test_data_path: Path,
        test_data: Sequence[BaseAITest],
        query_runner: QueryRunner,
    ):
        """Template method supporting `try_qna_queries` and `try_scenarios`."""
        d = {
            "step": method,
            "which_chatbot": self.which_chatbot.chatbot_name(),
            "use_case": use_case_name,
            "file_name": str(test_data_path),
            "data_sample_rate": self.data_sample_rate,
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
            "accumulate_test_results": self.accumulate_test_results,
        }
        print(json.dumps(d), file=self.log_file)

        samples = self._sample(test_data, self.data_sample_rate) if self.data_sample_rate < 1.0 else test_data
        self.samples_count = len(samples)
        if not self.samples_count:
            raise ValueError(
                f"No samples! test data size = {len(test_data)} * data sample rate = {self.data_sample_rate} => no samples!"
            )

        last_time = time.time()
        allowed_time_delta = 120  # seconds (NOTE: litellm appears to have an internal timeout of 5-6 minutes.)

        sample_number = 0
        for test_prompt in samples:
            sample_number += 1
            metadata, errors, warnings, lowConfidenceResults = query_runner.run_query(test_prompt)
            if errors:
                me = errors | metadata  # print the error data first.
                self.errors.append(me)
                if self.verbose:
                    print(me)
            if warnings:
                mw = warnings | metadata  # print the warning data first.
                self.warnings.append(mw)
                if self.verbose:
                    print(mw)

            if lowConfidenceResults:
                self.low_confidence_results.extend(lowConfidenceResults)
                if self.verbose:
                    print(lowConfidenceResults)

            lcr_count = len(self.low_confidence_results)
            warnings_count = len(self.warnings)
            errors_count = len(self.errors)
            if not self.accumulate_test_results:
                assert errors_count == 0, f"{errors_count} errors for test prompt #{sample_number}: {test_prompt}"

            # Logic to detect when it appears the system has deadlocked in some way.
            # If so, then error out.
            now = time.time()
            difference = int(last_time - now)
            assert (
                difference <= allowed_time_delta
            ), f"Time difference between inference calls, {difference} exceeds allowed time delta {allowed_time_delta}"
            last_time = now

            # Show we aren't dead by printing counts...
            print(
                f"({sample_number},{lcr_count},{warnings_count},{errors_count}) ",
                end="",
            )
            sys.stdout.flush()  # make sure the previous output isn't buffered...

        self.finish()

    def try_qna_queries(
        self,
        use_case_name: str,
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
        runner = QnAQueryRunner(self.chatbot, self.rating_threshold, self.confidence_threshold)

        self.__try_all_samples(
            method="try_qna_queries",
            use_case_name=use_case_name,
            test_data_path=file_path,
            test_data=data,
            query_runner=runner,
        )

    def try_scenarios(
        self,
        use_case_name: str,
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
        runner = ScenarioQueryRunner(self.chatbot, self.rating_threshold, self.confidence_threshold)

        self.__try_all_samples(
            method="try_scenarios",
            use_case_name=use_case_name,
            test_data_path=file_path,
            test_data=data,
            query_runner=runner,
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
        assert n > 0, f"Collection has no elements! {collection}"
        samples = collection
        if n > minimum_n and sample_rate < 1.0:
            # The samples will be unsorted, but that's okay, as we would like to catch subtle differences
            # in behavior that might be triggered by different ordering.
            k = round(sample_rate * n)
            if k < minimum_n:
                k = minimum_n
            samples = random.sample(collection, k=k)
        return samples
