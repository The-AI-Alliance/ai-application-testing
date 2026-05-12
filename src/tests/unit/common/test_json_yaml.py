# Unit tests for the "utils" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

import json
import re
import shutil
import unittest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Mapping

from common.json_yaml import (
    extract_jsonl_list,
    decode_json,
    encode_json,
    from_json,
)


class TestJsonYaml(unittest.TestCase):
    """
    Test the JSON and YAML utilities.
    """

    def clean_text(s: str) -> str:
        """Fix some problematic substrings that cause problems with JSON conversion."""
        s1 = re.sub(r'"', r"\"", s)
        s2 = re.sub(r"\}[,\s]*\{", "_ _", s1)
        return s2

    def escaped_dquotes(min_size: int = 0, max_size: int = 5):
        return st.text(
            alphabet=st.characters(codec="utf-8"), min_size=min_size, max_size=max_size
        ).map(lambda s: TestJsonYaml.clean_text(s))

    def __check_encode_decode_json(
        self,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        d1 = {
            "question": question,
            "answer": {
                "label": label,
                "prescription": prescription,
                "body-part": body_part,
                "timestamp": timestamp,
            },
        }
        js = encode_json(d1)
        d2 = decode_json(js)
        self.assertEqual(question, d1["question"])
        self.assertEqual(question, d2["question"])
        a1 = d1["answer"]
        a2 = d2["answer"]
        self.assertEqual(label, a1["label"])
        self.assertEqual(prescription, a1["prescription"])
        self.assertEqual(body_part, a1["body-part"])
        self.assertEqual(label, a2["label"])
        self.assertEqual(prescription, a2["prescription"])
        self.assertEqual(body_part, a2["body-part"])
        self.assertEqual(timestamp, a1["timestamp"])
        self.assertEqual(timestamp, a2["timestamp"])

    @given(
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        st.datetimes(),
    )
    def test_encode_json_handles_datetimes_and_returns_valid_JSON(
        self,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        self.__check_encode_decode_json(
            question, label, prescription, body_part, timestamp
        )

    @given(
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        st.datetimes(),
    )
    def test_decode_json_handles_datetimes_and_returns_valid_JSON(
        self,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        self.__check_encode_decode_json(
            question, label, prescription, body_part, timestamp
        )

    @given(
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        st.datetimes(),
    )
    def test_decode_json_JSONDecoderError_on_bad_input_str(
        self,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        """We only worry about parsing responses we expect to receive..."""
        js = """{{
            {quote}question{quote}: {quote}{question}{quote},
            {quote}answer{quote}: {{
                {quote}label{quote}: {quote}{label}{quote},
                {quote}prescription{quote}: {quote}{prescription}{quote},
                {quote}body-part{quote}: {quote}{body_part}{quote},
                {quote}timestamp{quote}: {quote}{timestamp}{quote}
            }}
        }}"""
        for quote in ["'", ""]:
            with self.assertRaises(ValueError):
                jsq = js.format(
                    quote=quote,
                    question=question,
                    label=label,
                    prescription=prescription,
                    body_part=body_part,
                    timestamp=timestamp,
                )
                decode_json(jsq)

    def do_test_extract_jsonl_list(
        self,
        delim: str,
        size: int,
        question: str = "question",
        label: str = "label",
        prescription: str = "prescription",
        body_part: str = "body_part",
        timestamp: datetime = datetime.now(),
    ):
        """We only worry about parsing responses we expect to receive..."""

        def d(i: int) -> Mapping[str, Any]:
            i_seconds = timedelta(seconds=i)
            return {
                "question": f"{question} {i}",
                "answer": {
                    "label": f"{label} {i}",
                    "prescription": f"{prescription} {i}",
                    "body-part": f"{body_part} {i}",
                    "timestamp": timestamp + i_seconds,
                },
            }

        jsons = [encode_json(d(n)) for n in range(size)]
        strs, errors = extract_jsonl_list(delim.join(jsons))
        self.assertEqual(
            size, len(strs), f"delim = <{delim}>, jsons = {jsons}, strs = {strs}"
        )
        self.assertEqual(
            0, len(errors), f"delim = <{delim}>, jsons = {jsons}, errors = {errors}"
        )
        for n in range(size):
            data = decode_json(strs[n])
            self.assertEqual(f"{question} {n}", data["question"])
            answ = data["answer"]
            self.assertEqual(f"{label} {n}", answ["label"])
            self.assertEqual(f"{prescription} {n}", answ["prescription"])
            self.assertEqual(f"{body_part} {n}", answ["body-part"])
            self.assertEqual(timestamp + timedelta(seconds=n), answ["timestamp"])

    def test_extract_jsonl_list_returns_empty_lists_if_text_empty(self):
        for delim in ["", " ", "\n", "\t"]:
            self.do_test_extract_jsonl_list(delim, 0)

    @given(
        st.integers(min_value=0, max_value=5),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        st.datetimes(),
    )
    def test_extract_jsonl_list_handles_valid_JSONL_one_per_line(
        self,
        size: int,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        for delim in ["", " ", "\t"]:
            d = f"{delim}\n{delim}"
            self.do_test_extract_jsonl_list(
                d, size, question, label, prescription, body_part, timestamp
            )
            self.do_test_extract_jsonl_list(
                "," + d, size, question, label, prescription, body_part, timestamp
            )
            self.do_test_extract_jsonl_list(
                d + ",", size, question, label, prescription, body_part, timestamp
            )

    @given(
        st.integers(min_value=0, max_value=5),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        escaped_dquotes(),
        st.datetimes(),
    )
    def test_extract_jsonl_list_handles_invalid_JSONL_all_on_one_line(
        self,
        size: int,
        question: str,
        label: str,
        prescription: str,
        body_part: str,
        timestamp: datetime,
    ):
        for delim in ["", " ", "\t"]:
            self.do_test_extract_jsonl_list(
                delim, size, question, label, prescription, body_part, timestamp
            )
            self.do_test_extract_jsonl_list(
                "," + delim, size, question, label, prescription, body_part, timestamp
            )
            self.do_test_extract_jsonl_list(
                delim + ",", size, question, label, prescription, body_part, timestamp
            )

    def test_from_json(self):
        d = {
            "one": 1,
            "two": {
                "two1": 2
            },
            "three": [
                {
                    "three1": 3,
                    "three2": 3.12
                },
                "3.2"
            ]
        }
        js = json.dumps(d)
        self.assertEqual(1,     from_json(js, ["one"]))
        self.assertEqual(2,     from_json(js, ["two", "two1"]))
        self.assertEqual(3,     from_json(js, ["three", 0, "three1"]))
        self.assertEqual(3.12,  from_json(js, ["three", 0, "three2"]))
        self.assertEqual("3.2", from_json(js, ["three", 1]))
        with self.assertRaises(ValueError):
            from_json(js, [])
        for kis in [[4], [4.1], ["four"], ["two", "two2"], ["three", 0, "three3"]]:
            with self.assertRaises(KeyError):
                from_json(js, kis)
        for kis in [["one", "bad"], ["two", "two1", "bad"], ["three", "three1"], ["three", 4.1]]:
            with self.assertRaises(TypeError):
                from_json(js, kis)
        for js2 in ["[", "]", "{", "}"]:
            with self.assertRaises(JSONDecodeError):
                from_json(js2, ["ignored"])


if __name__ == "__main__":
    unittest.main()
