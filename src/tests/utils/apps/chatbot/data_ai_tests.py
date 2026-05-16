"""
Types to encapsulate individual instances of AI test data,
such as a Q&A pair or a scenario, plus metadata.
"""

# Allow types to self-reference during their definitions.
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Mapping, Sequence, Tuple, Type

from common.collections import get_chain, get

from apps.chatbot import ChatBotAgent
from apps.chatbot.tools.resource_manager import ResourceManager


class BaseAITest(ABC):
    """Base class for `QnATest`, `ScenarioTest`, etc."""

    def __repr__(self) -> str:
        return self.json()

    def to_dict(self) -> Mapping[str, Any]:
        class_name = self.__class__.__name__
        d = {"name": class_name}
        d.update(vars(self))
        return d

    def json(self) -> str:
        return json.dumps(self.to_dict())


class QnATest(BaseAITest):
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


class ScenarioTest(BaseAITest):
    """
    Class to hold the test data for a "scenario" test, where one or more
    round trip interactions between the user (or AI surrogate) and the system
    are expected to occur.
    """

    @classmethod
    def get_known_scenario_kinds(cls) -> Mapping[str, Type[ScenarioTest]]:
        """Corresponding to the known subtypes of ScenarioTest."""
        return {
            "appointment": AppointmentScenarioTest,
        }

    class Inputs:
        def __init__(
            self, required_information: list[dict[str, str]], pre_conditions: list[str]
        ):
            self.required_information = required_information
            self.pre_conditions = pre_conditions

        def __repr__(self) -> str:
            return self.json()

        def to_dict(self) -> Mapping[str, Any]:
            class_name = self.__class__.__name__
            d = {"name": class_name}
            d.update(vars(self))
            return d

        def json(self) -> str:
            return json.dumps(self.to_dict())

    class SuccessFailure:
        def __init__(self, succeeded: bool, text: str, post_conditions: list[str]):
            self.succeeded = succeeded
            self.text = text
            self.post_conditions = post_conditions

        def __repr__(self) -> str:
            return self.json()

        def to_dict(self) -> Mapping[str, Any]:
            class_name = self.__class__.__name__
            d = {"name": class_name}
            d.update(vars(self))
            return d

        def json(self) -> str:
            return json.dumps(self.to_dict())

    class Success(SuccessFailure):
        def __init__(self, text: str, post_conditions: list[str]):
            super().__init__(True, text, post_conditions)

    class Failure(SuccessFailure):
        def __init__(self, text: str, post_conditions: list[str]):
            super().__init__(False, text, post_conditions)

    def __init__(
        self,
        scenario: str,
        inputs: Inputs,
        successes: list[Success],
        failures: list[Failure],
        initial_queries: list[str],
    ):
        self.scenario = scenario
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

    def start(self, chatbot: ChatBotAgent) -> None:
        """
        Called at the start of the test. Captures the data needed
        for the pre- and post-condition checks. Note that pre-conditions
        can't be checked now, because we don't yet know information like
        the patient name and one or more date times that might be needed.
        However, we save the appointments list before the scenario and we
        get the required information at the end, so we can check the pre-
        conditions _then_.
        """
        self.chatbot = chatbot
        self._custom_start()

    @abstractmethod
    def _custom_start(self) -> None:
        """
        Subclass hook for custom setup at the start of a test.
        Called first, before any other shared processing, by
        `self.start()`, which you shouldn't override!
        """

    def end(self, result: dict[str, Any]) -> Tuple[bool, dict[str, Any]]:
        """
        Called after the test has finished. Captures the data needed
        for the post-condition checks. Then performs all checks.
        """
        self._custom_end(result)
        self.check_required_information(result)
        self.check_conditions(result)
        success = (
            self.errors["required-information"] == []
            and self.errors["pre-conditions"] == []
            and self.errors["post-conditions"] == []
        )
        return success, self.errors

    @abstractmethod
    def _custom_end(self, result: dict[str, Any]):
        """
        Subclass hook for custom handling at the end of a test.
        Called first, before any other shared processing, by
        `self.end()`, which you shouldn't override!
        """

    def check_required_information(self, result: dict[str, Any]):
        """
        Analyze the results for required information and attempt to convert string values
        to the correct types. Add any errors to `self.errors['required-information']`.
        If successful, the string value for a label is replaced with the parsed object.
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
                value, err_msg = self._parse_value(label, value_str)
                if err_msg:
                    self.errors["required-information"].append(
                        f"{label}: value type error: {err_msg}"
                    )
                else:
                    captures[label] = value

    def check_conditions(self, result: dict[str, Any]) -> None:
        """
        Verify that the desired pre- and post-conditions were satisfied.
        Calls `self._custom_check_conditions()`, which subclasses should
        define.
        """
        self._custom_check_conditions(result)

    @abstractmethod
    def _custom_check_conditions(self, result: dict[str, Any]) -> None:
        pass

    def _parse_value(self, label: str, value: str) -> Tuple[Any, str]:
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
    def from_dict(cls, obj: Mapping[str, Any]):
        """
        Parse a nested dictionary loaded from a scenario test data file
        and construct a ScenarioTest instance from it.
        """
        scenario = get(obj, "scenario")
        inputs = get(obj, "inputs")
        outputs = get(obj, "outputs")

        # Inputs, successes, and initial queries can't be empty.
        # Failures can be empty.
        inputs = ScenarioTest.Inputs(
            required_information=get(inputs, "required-information"),
            pre_conditions=get(inputs, "pre-conditions"),
        )
        successes = [
            ScenarioTest.Success(
                text=get(s, "text"),
                post_conditions=get(s, "post-conditions"),
            )
            for s in get(outputs, "successes")
        ]
        failures = [
            ScenarioTest.Failure(
                text=get(f, "text"),
                post_conditions=get(f, "post-conditions"),
            )
            for f in get(outputs, "failures", [])
        ]
        initial_queries = get(obj, "initial-queries")

        return cls(
            scenario=scenario,
            inputs=inputs,
            successes=successes,
            failures=failures,
            initial_queries=initial_queries,
        )

    def __repr__(self) -> str:
        return self.json()

    def to_dict(self) -> Mapping[str, Any]:
        class_name = self.__class__.__name__
        d = {"name": class_name}
        d.update(vars(self))
        return d

    def json(self) -> str:
        d = self.to_dict()
        d["inputs"]    = d["inputs"].json()
        d["successes"] = [s.json() for s in d["successes"]]
        d["failures"]  = [f.json() for f in d["failures"]]
        return json.dumps(d)


class AppointmentScenarioTest(ScenarioTest):
    """
    Class to hold the test data for a "scenario" test for managing
    appointments, where one or more round trip interactions between
    the user (or AI surrogate) and the system are expected to occur.
    """

    def __init__(
        self,
        scenario: str,
        inputs: ScenarioTest.Inputs,
        successes: list[ScenarioTest.Success],
        failures: list[ScenarioTest.Failure],
        initial_queries: list[str],
    ):
        super().__init__(scenario, inputs, successes, failures, initial_queries)

    def _custom_start(self):
        """
        Custom setup for appointment scenario tests.
        """
        self.am = self.chatbot.appointment_manager
        self.start_appointments = self.am.appointments.copy()
        self.end_appointments: dict[str, dict[str, Any]] = {}

    def _custom_end(self, result: dict[str, Any]):
        """
        Custom handling after the test has finished.
        """
        self.end_appointments = self.am.appointments.copy()

    def _custom_check_conditions(self, result: dict[str, Any]) -> None:
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
        for sf in s_or_f:
            for pc in sf.post_conditions:
                match pc:
                    case (
                        "appointment-at-date-time-for-patient"
                        | "appointment-at-new-date-time-for-patient"
                    ):
                        self.check_appointment_at_date_time_for_patient(
                            True, True, "post-conditions", result
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
        captures = result.get("captures")
        if not captures:
            self.errors[which_conditions].append("No data was 'captured'.")
        else:
            if include_patient_name:
                pn = get_chain(captures, ["patient_name", "value"])
                errors = get_chain(captures, ["patient_name", "errors"])
                if errors:
                    self.errors[which_conditions].append(f"patient-name: {errors}")
                    run_criteria = False
                elif pn:
                    criteria["patient-name"] = pn
                else:
                    self.errors[which_conditions].append("patient-name is empty")
                    run_criteria = False

                adt = get_chain(captures, ["appointment-date-time", "value"])
                errors = get_chain(captures, ["appointment-date-time", "errors"])
                if errors:
                    self.errors[which_conditions].append(
                        f"appointment-date-time: {errors}"
                    )
                    run_criteria = False
                elif adt:
                    criteria["appointment-date-time"] = adt
                else:
                    self.errors[which_conditions].append(
                        "appointment-date-time is empty"
                    )
                    run_criteria = False

                if run_criteria:
                    found = ResourceManager.get_resources_by_criteria_from(
                        list(appointments.values()), criteria
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
