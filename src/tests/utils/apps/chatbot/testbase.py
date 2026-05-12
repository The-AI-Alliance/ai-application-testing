# Common code for tests of the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/


import json
import logging
import os
import random
import re
import time
import unittest
from datetime import datetime
from io import StringIO, TextIOWrapper
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from apps.chatbot import (
    ChatBot,
    ChatBotSimple,
    ChatBotAgent,
    ChatBotResponseHandler,
    ChatBotShell,
)
from apps.chatbot.tools import ResourceManager
from common.collections import chain, dict_pop, get
from common.json_yaml import decode_json


class BaseTest:
    """Base class for `QnATest` and `ScenarioTest`."""


class QnATest(BaseTest):
    """
    Class to hold a benchmark Q&A pair: a query
    and expected results: labels, actions, and rating.
    """

    def __init__(
        self,
        query: str,
        labels: Sequence[str],
        actions: Sequence[str],
        rating: int,
        reason: str = "",
        keywords: Mapping[str, str] = {},
    ):
        super().__init__()
        self.query = query
        self.labels = labels
        self.actions = actions
        self.rating = rating
        self.reason = reason if reason else ""
        self.keywords = keywords
        errors = []
        if not self.query:
            errors.append("empty query")
        if not self.labels:
            errors.append("empty labels")
        if rating < 0 or rating > 5:
            errors.append(
                f"invalid rating {self.rating} (not between 0 and 5, inclusive)"
            )
        if errors:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

    def __repr__(self) -> str:
        return self.json()

    def dict(self) -> dict[str, Any]:
        d = {"name": "QnATest"}
        d.update(vars(self))
        return d

    def json(self) -> str:
        return json.dumps(self.dict())


class ScenarioTest(BaseTest):
    """
    Class to hold the test data for a "scenario" test, where one or more
    round trip interactions between the user (or AI surrogate) and the system
    are expected to occur.
    """

    class Inputs:
        def __init__(
            self, required_information: list[dict[str, str]], pre_conditions: list[str]
        ):
            self.required_information = required_information
            self.pre_conditions = pre_conditions

    class Success:
        def __init__(self, success_text: str, success_post_conditions: list[str]):
            self.success_text = success_text
            self.success_post_conditions = success_post_conditions

    class Failure:
        def __init__(self, failure_text: str, failure_post_conditions: list[str]):
            self.failure_text = failure_text
            self.failure_post_conditions = failure_post_conditions

    def __init__(
        self,
        scenario: str,
        inputs: Inputs,
        successes: list[Success],
        failures: list[Failure],
        initial_queries: list[str],
    ):

        self.scenario = (scenario,)
        self.inputs = inputs
        self.successes = successes
        self.failures = failures
        self.initial_queries = initial_queries
        self.start_data = {}
        self.end_data = {}
        self.errors = {
            "required-information": [],
            "pre-conditions": [],
            "post-conditions": [],
        }

    def start(self, chatbot: ChatBotAgent) -> dict[str, Any]:
        """
        Called at the start of the test. Captures the data needed
        for the pre- and post-condition checks. Note that pre-conditions
        can't be checked now, because we don't yet know information like
        the patient name and one or more date times that might be needed.
        However, we save the appointments list before the scenario and we
        get the required information at the end, so we can check the pre-
        conditions _then_.
        """
        # TODO: hard-codes awareness of particular scenarios, which
        # should be abstracted away eventually.
        am = chatbot.appointment_manager
        self.start_appointments = am.appointments.copy()

    def end(
        self, chatbot: ChatBotAgent, result: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Called after the test has finished. Captures the data needed
        for the post-condition checks. Then performs all checks.
        """
        # TODO: hard-codes awareness of particular scenarios, which
        # should be abstracted away eventually.
        am = chatbot.appointment_manager
        self.end_appointments = am.appointments.copy()
        self.check_required_information(chatbot, result)
        self.check_conditions(chatbot, result)
        success = (
            self.errors["required-information"] == []
            and self.errors["pre-conditions"] == []
            and self.errors["post-conditions"] == []
        )
        return success, self.errors

    def check_required_information(self, chatbot: ChatBotAgent, result: dict[str, Any]):
        """
        Analyze the results for required information and atempt to convert string values to the
        correct types. Add any errors to `self.errors['required-information']`. If successful,
        the string value for a label is replaced with the parsed object.
        """
        captures = get(result, "captured_values")
        for info in self.inputs.required_information:
            label = get(info, "label")
            value_str: str = captures.get("label")
            if not value_str:
                self.errors["required-information"].append(
                    f"{label}: value not captured"
                )
            else:
                value, err_msg = self.parse_value(label, value_str)
                if err_msg:
                    self.errors["required-information"].append(
                        f"{label}: value type error: {err_msg}"
                    )
                else:
                    captures[label] = value

    def check_appointment_at_date_time_for_patient(
        self,
        should_find: bool,
        include_patient_name: bool,
        which_conditions: str,
        result: dict[str, Any],
    ):
        appointments = (
            self.start_appointments
            if which_conditions == "pre-conditions"
            else self.end_appointments
        )
        run_criteria = True
        criteria = {}
        if include_patient_name:
            pn = chain(result.captures, ["patient_name", "value"])
            errors = chain(result.captures, ["patient_name", "errors"])
            if errors:
                self.errors[which_conditions].append(f"patient-name: {errors}")
                run_criteria = False
            elif pn:
                criteria["patient-name"] = pn
            else:
                self.errors[which_conditions].append("patient-name is empty")
                run_criteria = False

            adt = chain(result.captures, ["appointment-date-time", "value"])
            errors = chain(result.captures, ["appointment-date-time", "errors"])
            if errors:
                self.errors[which_conditions].append(f"appointment-date-time: {errors}")
                run_criteria = False
            elif adt:
                criteria["appointment-date-time"] = adt
            else:
                self.errors[which_conditions].append("appointment-date-time is empty")
                run_criteria = False

            if run_criteria:
                found = ResourceManager.get_resources_by_criteria_from(
                    appointments, criteria
                )
                if found and not should_find:
                    self.errors[which_conditions].append(
                        f"Found appointment, but not expected for criteria {criteria}"
                    )
                if not found and should_find:
                    self.errors[which_conditions].append(
                        f"No appointment found for criteria {criteria}"
                    )

    def check_appointments_count(self, delta: int, result: dict[str, Any]):
        len_start = len(self.start_appointments)
        len_end = len(self.end_appointments)
        if len_start + delta != len_end:
            self.errors["post-conditions"].append(
                f"After vs. before appointments counts {len_start + delta} != {len_end}"
            )

    def appointments_unchanged(self, result: dict[str, Any]):
        if not self.start_appointments == self.end_appointments:
            self.errors["post-conditions"].append(
                f"Start and end appointments differ: {self.start_appointments} != {self.end_appointments}"
            )

    def check_conditions(
        self, chatbot: ChatBotAgent, result: dict[str, Any]
    ) -> dict[str, Any]:
        for pc in self.inputs.pre_conditions:
            match pc:
                case "appointment-at-date-time-for-patient":
                    self.check_appointment_at_date_time_for_patient(
                        True, True, "pre-conditions", result
                    )
                case "no-appointment-at-date-time-for-patient":
                    self.check_appointment_at_date_time_for_patient(
                        False, True, "pre-conditions", result
                    )
                case "no-appointment-at-date-time":
                    self.check_appointment_at_date_time_for_patient(
                        False, False, "pre-conditions", result
                    )

        s_or_f = self.successes if result["succeeded"] else self.failures
        for pc in s_or_f.post_conditions:
            match pc:
                case (
                    "appointment-at-date-time-for-patient"
                    | "appointment-at-new-date-time-for-patient"
                ):
                    self.check_appointment_at_date_time_for_patient(
                        True, True, "post-conditions", result, self.end_appointments
                    )
                case "no-appointment-at-date-time-for-patient":
                    self.check_appointment_at_date_time_for_patient(
                        False, True, "post-conditions", result
                    )
                case "no-appointment-at-date-time":
                    self.check_appointment_at_date_time_for_patient(
                        False, False, "post-conditions", result
                    )
                case "appointments-unchanged":
                    self.appointments_unchanged(result)
                case "before-appointments-count":
                    self.check_appointments_count(0, result)
                case "before-appointments-count-minus-one":
                    self.check_appointments_count(-1, result)
                case "before-appointments-count-plus-one":
                    self.check_appointments_count(1, result)

    def parse_value(self, label: str, value: str) -> tuple[Any, str]:
        """
        Assume a JSON string for a single value or a list of values.
        Parse with json.loads(), then convert any datetimes found.
        """
        try:
            obj = json.loads(value)
            if isinstance(obj, list):
                lst = []
                for x in obj:
                    try:
                        x2 = datetime.fromisoformat(x)
                        lst.append(x2)
                    except ValueError:
                        lst.append(x)
                return lst, ""
            else:
                return obj, ""
        except json.decoder.JSONDecodeError as e:
            return value, f"Label {label} value {value} is not valid JSON: {e}"

    @classmethod
    def from_dict(obj: dict[str, Any]):
        """
        Parse a nested dictionary loaded from a scenario test data file
        and construct a ScenarioTest instance from it.
        """
        scenario = get(obj, "scenario")
        inputs = get(obj, "inputs")
        outputs = get(obj, "outputs")
        successes = [
            (s.get("text"), s.get("post_conditions")) for s in get(outputs, "successes")
        ]
        failures = [
            (f.get("text"), f.get("post_conditions")) for f in get(outputs, "failures")
        ]

        inputs = ScenarioTest.Inputs(
            required_information=get(inputs, "required-information"),
            pre_conditions=get(inputs, "pre-conditions"),
        )
        successes = [
            ScenarioTest.Success(
                success_text=get(s, "text"),
                success_post_conditions=get(s, "post_conditions"),
            )
            for s in get(outputs, "successes")
        ]
        failures = [
            ScenarioTest.Failure(
                failure_text=get(f, "text"),
                failure_post_conditions=get(f, "post_conditions"),
            )
            for f in get(outputs, "failures")
        ]

        initial_queries = get(obj, "initial-queries")

        return ScenarioTest(
            scenario=scenario,
            inputs=inputs,
            successes=successes,
            failures=failures,
            initial_queries=initial_queries,
        )

    def __repr__(self) -> str:
        return self.json()

    def dict(self) -> dict[str, Any]:
        d = {"name": "ScenarioTest"}
        d.update(vars(self))
        return d

    def json(self) -> str:
        return json.dumps(self.dict())


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
        test_prompt: QnATest,
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
            "test_prompt": self.test_prompt.dict(),
            "rating_threshold": self.rating_threshold,
            "confidence_threshold": self.confidence_threshold,
        }

    def json(self) -> str:
        return json.dumps(self.dict())


class TestBase(unittest.TestCase):
    """
    Base class for tests that need to instantiate a ChatBot, but not necessarily run inference with it.
    Use `TestBaseRunner`, a derived class of this class, for those tests.
    """

    default_confidence_threshold: float = ChatBot.default_confidence_threshold
    default_rating_threshold: int = 4
    log_file_name: str = ""
    log_file: TextIOWrapper = None
    which_chatbot_choice: str = ""
    which_chatbot: ChatBot | None = None

    def make_chatbot(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Determine which ChatBot implementation to use based on environment variable
        self.assertNotEqual("", TestBase.which_chatbot_choice)
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

    def _get_data_file(
        self, use_case_name: str, require_simple_or_agent: bool = False
    ) -> Path:
        """
        Look for a "{use_case_name}-simple.jsonl" or a
        "{use_case_name}-scenario.json" file first, depending on which
        ChatBot we are testing, and if not found, then look for a
        "{use_case_name}.jsonl" file. However, only look for the second
        file if `require_simple_or_agent` is False. If it is true, we
        require that the `*-simple.jsonl` or `*-scenario.json` be found.
        Fail the test if a data file can't be found.
        """
        ss = [f"-{TestBase.which_chatbot_choice}"]
        if not require_simple_or_agent:
            ss.append("")
        files = [
            TestBaseRunner.benchmark_data_dir / f"{use_case_name}{s}.jsonl" for s in ss
        ]
        for file in files:
            if file.exists():
                return file
        self.fail(f"Data files {files} don't exist for use case {use_case_name}!")

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
        TestBase.which_chatbot = (
            "ChatBotAgent"
            if TestBase.which_chatbot_choice == "agent"
            else "ChatBotSimple"
        )

        def_log_dir = "tests/logs"
        log_file_template = os.environ.get("TESTS_LOGS_FILE_TEMPLATE")
        if not log_file_template:
            print("WARNING: TESTS_LOGS_FILE_TEMPLATE undefined. Using default value.")
            log_file_template = f"{def_log_dir}/{{which_chatbot}}-{{class_name}}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        log_file_path = Path(
            log_file_template.format(
                class_name=cls.__name__, which_chatbot=TestBase.which_chatbot
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

    def __load_qna_test_data(self, path: Path) -> list[QnATest]:
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

    def __load_session_test_data(self, path: Path) -> list[ScenarioTest]:
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open("r") as file:
            lines = file.readlines()
            try:
                objs = decode_json("".join(lines))
                tests = [ScenarioTest.from_dict(obj) for obj in objs]
                return tests
            except ValueError as err:
                raise ValueError(f"Error parsing JSON in file {path}") from err
        if not len(tests):
            raise ValueError(f"No scenario tests were loaded from {path}!")

    def __try_qna_query(
        self,
        test_prompt: QnATest,
        rating_threshold: int = TestBase.default_rating_threshold,
        confidence_threshold: float = TestBase.default_confidence_threshold,
    ):
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
            "test_prompt": test_prompt.dict(),
            "rating_threshold": rating_threshold,
            "confidence_threshold": confidence_threshold,
        }
        # On success this will be returned as empty. If problems are found,
        # we put those kvs first, so they are printed first...
        errors = {}
        warnings = {}

        answer = self.chatbot.query(prompt)
        try:
            if isinstance(answer, str) or answer.get("error"):
                qf = {
                    "query_failure": f"unexpected message returned: {answer}",
                    "metadata": metadata,
                    "error": answer.get("error", ""),
                }
                self.key_results["errors"].append(qf)
                if self.verbose:
                    print(qf)
                return qf

            metadata["answer"] = answer

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
            if actual_confidence < confidence_threshold:
                low_confidence_reasons.append(
                    f"Actual confidence ({actual_confidence}) < confidence threshold ({confidence_threshold})."
                )
            if exp_rating < rating_threshold:
                low_confidence_reasons.append(
                    f"Expected rating ({exp_rating}) < rating threshold ({rating_threshold})."
                )

            if low_confidence_reasons:
                reasons = " ".join(low_confidence_reasons)
                lcr = LowConfidenceResult(
                    prompt,
                    reasons,
                    actual_reply,
                    test_prompt,
                    rating_threshold,
                    confidence_threshold,
                )
                self.key_results["low_confidence_results"].append(lcr)
                if self.verbose:
                    print(lcr)
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
                    warnings["unexpected keywords"] = missing_kvs
        except TypeError as te:
            print(f"TypeError while parsing answer: {answer}")
            raise te

        if errors:
            me = errors | metadata
            self.key_results["errors"].append(me)
            if self.verbose:
                print(me)
        if warnings:
            mw = warnings | metadata
            self.key_results["warnings"].append(mw)
            if self.verbose:
                print(mw)

    def __try_all(
        self,
        method: str,
        use_case_name: str,
        require_simple_or_agent: bool,
        test_data_loader: Callable[[Path], list[BaseTest]],
        try_query: Callable[[BaseTest, int, float], None],
        sample_rate: float,
        rating_threshold: int,
        confidence_threshold: float,
    ):
        """Template method supporting `try_qna_queries` and `try_sessions`."""
        file_name = self._get_data_file(
            use_case_name, require_simple_or_agent=require_simple_or_agent
        )

        if not sample_rate > 0.0:
            sample_rate = self.sample_rate

        d = {
            "step": method,
            "which_chatbot": TestBase.which_chatbot_choice,
            "file_name": str(file_name),
            "sample_rate": sample_rate,
            "rating_threshold": rating_threshold,
            "confidence_threshold": confidence_threshold,
            "accumulate_test_results": self.accumulate_test_results,
        }
        print(json.dumps(d), file=TestBaseRunner.log_file)

        test_prompts = test_data_loader(file_name)
        samples = (
            self._sample(test_prompts, sample_rate)
            if sample_rate < 1.0
            else test_prompts
        )

        last_time = time.time()
        allowed_time_delta = 120  # seconds (NOTE: litellm appears to have an internal timeout of 5-6 minutes.)

        for test_prompt in samples:
            self.samples_count += 1
            try_query(
                test_prompt,
                rating_threshold=rating_threshold,
                confidence_threshold=confidence_threshold,
            )

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
        self.__try_all(
            method="try_qna_queries",
            use_case_name=use_case_name,
            require_simple_or_agent=False,
            test_data_loader=self.__load_qna_test_data,
            try_query=self.__try_qna_query,
            sample_rate=sample_rate,
            rating_threshold=rating_threshold,
            confidence_threshold=confidence_threshold,
        )

    def try_sessions(
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
        self.__try_all(
            method="try_sessions",
            use_case_name=use_case_name,
            require_simple_or_agent=True,
            test_data_loader=self.__load_session_test_data,
            try_query=self.__try_session_query,
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

    def _check_label(self, expected: Sequence[str], actual: str) -> str:
        return (
            ""
            if actual in expected
            else f"""label '{actual}' not in expected: {expected}."""
        )
