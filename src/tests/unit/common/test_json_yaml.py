"""
Test the JSON and YAML utilities.
Unit tests for the "utils" module using Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import json
import re
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from typing import Any, Mapping, Sequence

from common.json_yaml import (
    extract_jsonl_list,
    decode_json_dict,
    decode_json_list,
    encode_json,
    from_json,
)
from common.utils import ExpectedFail

from tests.common.hypothesis.datetimes import year_2000


def clean_text(s: str) -> str:
    """Fix some problematic substrings that cause problems with JSON conversion."""
    s1 = re.sub(r'"', r"\"", s)
    s2 = re.sub(r"\}[,\s]*\{", "_ _", s1)
    return s2


def escaped_dquotes(min_size: int = 0, max_size: int = 5):
    return st.text(alphabet=st.characters(codec="utf-8"), min_size=min_size, max_size=max_size).map(
        lambda s: clean_text(s)
    )


def __check_encode_decode_json_dict(
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    l1, qs, ls, ps, bs, ts = __make_dict_list(1, question, label, prescription, body_part, timestamp)
    d1 = l1[0]
    js = encode_json(d1)
    d2 = decode_json_dict(js)
    assert isinstance(d2, Mapping), f"Not a Mapping! <{d2}>, for js = <{js}>"
    __check_dict(qs[0], ls[0], ps[0], bs[0], ts[0], d1, d2)


def __check_encode_decode_json_list(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    l1, qs, ls, ps, bs, ts = __make_dict_list(count, question, label, prescription, body_part, timestamp)

    js = encode_json(l1)
    l2 = decode_json_list(js)
    assert isinstance(l2, Sequence), f"Not a Sequence! <{l2}>, for js = <{js}>"
    for i in range(count):
        __check_dict(qs[i], ls[i], ps[i], bs[i], ts[i], l1[i], l2[i])


def __make_dict_list(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    qs = []
    ls = []
    ps = []
    bs = []
    ts = []
    one_second = timedelta(seconds=1)
    t = timestamp
    lists = []
    for i in range(count):
        qs.append(f"{i}: {question}")
        ls.append(f"{i}: {label}")
        ps.append(f"{i}: {prescription}")
        bs.append(f"{i}: {body_part}")
        ts.append(t)
        lists.append(
            {
                "question": qs[i],
                "answer": {
                    "label": ls[i],
                    "prescription": ps[i],
                    "body-part": bs[i],
                    "timestamp": t,
                },
            }
        )
        t = t + one_second
    return lists, qs, ls, ps, bs, ts


def __check_dict(
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
    d_actual: Mapping[str, Any],
    d_expected: Mapping[str, Any],
):
    a1 = d_actual["answer"]
    a2 = d_expected["answer"]
    assert question == d_actual["question"]
    assert question == d_expected["question"]
    assert label == a1["label"]
    assert prescription == a1["prescription"]
    assert body_part == a1["body-part"]
    assert label == a2["label"]
    assert prescription == a2["prescription"]
    assert body_part == a2["body-part"]
    assert timestamp == a1["timestamp"]
    assert timestamp == a2["timestamp"]


@given(
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_encode_json_dict_handles_datetimes_and_returns_valid_JSON(
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    __check_encode_decode_json_dict(question, label, prescription, body_part, timestamp)


@given(
    st.integers(min_value=0, max_value=5),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_decode_json_list_handles_datetimes_and_returns_valid_JSON(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    __check_encode_decode_json_list(count, question, label, prescription, body_part, timestamp)


"""We only worry about parsing responses we expect to receive..."""
js_template = """{{
    {quote}question{quote}: {quote}{question}{quote},
    {quote}answer{quote}: {{
        {quote}label{quote}: {quote}{label}{quote},
        {quote}prescription{quote}: {quote}{prescription}{quote},
        {quote}body-part{quote}: {quote}{body_part}{quote},
        {quote}timestamp{quote}: {quote}{timestamp}{quote}
    }}
}}"""


@given(
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_decode_json_dict_ValueError_on_bad_input_str(
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    for quote in ["'", ""]:
        jss = __make_quoted_json_strings(1, quote, question, label, prescription, body_part, timestamp)
        jsq = jss[0]  # check for a single "bad" dict.
        ef = ExpectedFail(ValueError)
        ef(lambda: decode_json_dict(jsq))


@given(
    st.integers(min_value=1, max_value=3),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_decode_json_list_ValueError_on_bad_input_str(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    for quote in ["'", ""]:
        jss = __make_quoted_json_strings(count, quote, question, label, prescription, body_part, timestamp)
        jsqs = "[\n" + ",\n".join(jss) + "\n]"
        ef = ExpectedFail(ValueError)
        ef(lambda: decode_json_list(jsqs))


@given(
    st.integers(min_value=1, max_value=3),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_decode_json_dict_ValueError_on_input_list_of_dicts_str(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    jss = __make_quoted_json_strings(count, '"', question, label, prescription, body_part, timestamp)
    jsqs = "[\n" + ",\n".join(jss) + "\n]"
    ef = ExpectedFail(ValueError)
    ef(lambda: decode_json_dict(jsqs))


@given(
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_decode_json_list_ValueError_on_input_dict_str(
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    jss = __make_quoted_json_strings(1, '"', question, label, prescription, body_part, timestamp)
    ef = ExpectedFail(ValueError)
    ef(lambda: decode_json_dict(jss[0]))


def __make_quoted_json_strings(
    count: int,
    quote: str,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    _, qs, ls, ps, bs, ts = __make_dict_list(count, question, label, prescription, body_part, timestamp)
    jss = []
    for i in range(count):
        jss.append(
            js_template.format(
                quote=qs[i],
                question=qs[i],
                label=ls[i],
                prescription=ps[i],
                body_part=bs[i],
                timestamp=ts[i],
            )
        )
    return jss


def do_test_extract_jsonl_list(
    delim: str,
    count: int,
    question: str = "question",
    label: str = "label",
    prescription: str = "prescription",
    body_part: str = "body_part",
    timestamp: datetime = datetime.now(),
):
    lists, qs, ls, ps, bs, ts = __make_dict_list(count, question, label, prescription, body_part, timestamp)

    jsons = [encode_json(d) for d in lists]
    strs, errors = extract_jsonl_list(delim.join(jsons))
    assert count == len(strs), f"delim = <{delim}>, jsons = {jsons}, strs = {strs}"
    assert 0 == len(errors), f"delim = <{delim}>, jsons = {jsons}, errors = {errors}"
    for n in range(count):
        data = decode_json_dict(strs[n])
        assert qs[n] == data["question"]
        answ = data["answer"]
        assert ls[n] == answ["label"]
        assert ps[n] == answ["prescription"]
        assert bs[n] == answ["body-part"]
        assert ts[n] == answ["timestamp"]


def test_extract_jsonl_list_returns_empty_lists_if_text_empty():
    for delim in ["", " ", "\n", "\t"]:
        do_test_extract_jsonl_list(delim, 0)


@given(
    st.integers(min_value=0, max_value=5),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_extract_jsonl_list_handles_valid_JSONL_one_per_line(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    for delim in ["", " ", "\t"]:
        d = f"{delim}\n{delim}"
        do_test_extract_jsonl_list(d, count, question, label, prescription, body_part, timestamp)
        do_test_extract_jsonl_list("," + d, count, question, label, prescription, body_part, timestamp)
        do_test_extract_jsonl_list(d + ",", count, question, label, prescription, body_part, timestamp)


@given(
    st.integers(min_value=0, max_value=5),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    escaped_dquotes(),
    st.datetimes(min_value=year_2000),
)
def test_extract_jsonl_list_handles_invalid_JSONL_all_on_one_line(
    count: int,
    question: str,
    label: str,
    prescription: str,
    body_part: str,
    timestamp: datetime,
):
    for delim in ["", " ", "\t"]:
        do_test_extract_jsonl_list(delim, count, question, label, prescription, body_part, timestamp)
        do_test_extract_jsonl_list("," + delim, count, question, label, prescription, body_part, timestamp)
        do_test_extract_jsonl_list(delim + ",", count, question, label, prescription, body_part, timestamp)


def test_from_json():
    d = {
        "one": 1,
        "two": {"two1": 2},
        "three": [{"three1": 3, "three2": 3.12}, "3.2"],
    }
    js = json.dumps(d)
    assert 1 == from_json(js, ["one"])
    assert 2 == from_json(js, ["two", "two1"])
    assert 3 == from_json(js, ["three", 0, "three1"])
    assert 3.12 == from_json(js, ["three", 0, "three2"])
    assert "3.2" == from_json(js, ["three", 1])

    efve = ExpectedFail(ValueError)
    efke = ExpectedFail(KeyError)
    efte = ExpectedFail(TypeError)
    efje = ExpectedFail(JSONDecodeError)

    efve(lambda: from_json(js, []))

    for kis in [[4], [4.1], ["four"], ["two", "two2"], ["three", 0, "three3"]]:
        efke(lambda: from_json(js, kis))
    for kis in [
        ["one", "bad"],
        ["two", "two1", "bad"],
        ["three", "three1"],
        ["three", 4.1],
    ]:
        efte(lambda: from_json(js, kis))
    for js2 in ["[", "]", "{", "}"]:
        efje(lambda: from_json(js2, ["ignored"]))
