# Unit tests for the "utils" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

import json, os, re, sys, shutil, unittest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

from common.utils import (
    all_use_cases,
    dict_pop,
    ensure_dirs_exist,
    extract_jsonl_list,
    make_parent_dirs,
    model_dir_name,
    decode_json,
    encode_json,
)

class TestUtils(unittest.TestCase):
    """
    Test the utilities.
    """

    use_cases = all_use_cases()
    use_cases_names = list(use_cases.keys())
    use_cases_labels = list(use_cases.values())
    test_temp = './test-temp'

    def clean_text(s: str) -> str:
        """Fix some problematic substrings that cause problems with JSON conversion."""
        s1 = re.sub(r'"', r'\"', s)
        s2 = re.sub(r'\}[,\s]*\{', '_ _', s1)
        return s2

    def valid_dirs(min_size: int = 1, max_size: int = 5):
        return st.text(alphabet=st.characters(codec='ascii'), min_size=min_size, max_size=max_size).map(
            lambda s: re.sub(r'\W', '_', s))
    def escaped_dquotes(min_size: int = 0, max_size: int = 5):
        return st.text(alphabet=st.characters(codec='utf-8'), min_size=min_size, max_size=max_size).map(
            lambda s: TestUtils.clean_text(s))

    def tearDown(self):
        self.clean()

    def clean(self):
        tt = Path(self.test_temp)
        if tt.exists():
            shutil.rmtree(self.test_temp)

    @given(st.lists(valid_dirs(), max_size=5))
    def test_model_dir_name(self, strs: list[str]):
        s = ':'.join(strs)
        expected = s.replace(':', '_')
        self.assertEqual(expected, model_dir_name(s))

    @given(st.sampled_from(use_cases_names))
    def test_use_cases(self, use_case_name: str):
        self.assertEqual(3, len(self.use_cases)) # sanity check
        self.assertTrue(use_case_name.find(' ') < 0) # sanity check
        self.assertIsNotNone(self.use_cases.get(use_case_name))

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_that_do_not_exist(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok = False)
        self.assertTrue(path.exists())
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_with_allowed_preexisting_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok = False)
        self.assertTrue(path.exists())
        path2 = make_parent_dirs(file, exist_ok = True)
        self.assertEqual(path, path2)
        self.assertEqual(Path(fdir), path)
        self.clean()

    def test_make_parent_dirs_with_file_in_cwd(self):
        path = make_parent_dirs('./foo.txt', exist_ok = False)
        self.assertEqual(Path('.'), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_does_not_raise_for_existing_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok = False)
        ensure_dirs_exist(fdir)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_raises_for_missing_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        with self.assertRaises(ValueError):
            ensure_dirs_exist(fdir)

    def __check_encode_decode_json(self, 
        question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
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
        self.assertEqual(question,  d1['question']) 
        self.assertEqual(question,  d2['question']) 
        a1 = d1['answer']
        a2 = d2['answer']
        self.assertEqual(label, a1['label'])
        self.assertEqual(prescription, a1['prescription'])
        self.assertEqual(body_part, a1['body-part'])
        self.assertEqual(label, a2['label'])
        self.assertEqual(prescription, a2['prescription'])
        self.assertEqual(body_part, a2['body-part'])
        self.assertEqual(timestamp, a1['timestamp'])
        self.assertEqual(timestamp, a2['timestamp'])

    @given(escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), st.datetimes())
    def test_encode_json_handles_datetimes_and_returns_valid_JSON(self, 
        question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
        self.__check_encode_decode_json(question, label, prescription, body_part, timestamp)

    @given(escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), st.datetimes())
    def test_decode_json_handles_datetimes_and_returns_valid_JSON(self, 
        question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
        self.__check_encode_decode_json(question, label, prescription, body_part, timestamp)

    @given(escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), st.datetimes())
    def test_decode_json_JSONDecoderError_on_bad_input_str(self, 
        question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
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
                jsq = js.format(quote=quote, question=question, label=label,
                    prescription=prescription, body_part=body_part, timestamp=timestamp)
                decode_json(jsq)
        
        jsdq = js.format(quote='"', question=question, label=label,
                prescription=prescription, body_part=body_part, timestamp=timestamp)

    def do_test_extract_jsonl_list(self, 
        delim: str,
        size: int, 
        question: str = 'question',
        label: str = 'label',
        prescription: str = 'prescription',
        body_part: str = 'body_part',
        timestamp: datetime = datetime.now()):
        """We only worry about parsing responses we expect to receive..."""
        def d(i: int) -> Mapping[str,Any]:
            i_seconds = timedelta(seconds=i)
            return {
                "question": f"{question} {i}",
                "answer": {
                    "label": f"{label} {i}",
                    "prescription": f"{prescription} {i}",
                    "body-part": f"{body_part} {i}",
                    "timestamp": timestamp + i_seconds,
                }
            }
        jsons = [encode_json(d(n)) for n in range(size)]
        strs, errors = extract_jsonl_list(delim.join(jsons))
        self.assertEqual(size, len(strs), f"delim = <{delim}>, jsons = {jsons}, strs = {strs}")
        self.assertEqual(0, len(errors),  f"delim = <{delim}>, jsons = {jsons}, errors = {errors}")
        for n in range(size):
            data = decode_json(strs[n])
            self.assertEqual(f"{question} {n}", data['question'])
            answ = data['answer']
            self.assertEqual(f"{label} {n}", answ['label'])
            self.assertEqual(f"{prescription} {n}", answ['prescription'])
            self.assertEqual(f"{body_part} {n}", answ['body-part'])
            self.assertEqual(timestamp + timedelta(seconds=n), answ['timestamp'])


    def test_extract_jsonl_list_returns_empty_lists_if_text_empty(self):
        for delim in ['', ' ', '\n', '\t']:
            self.do_test_extract_jsonl_list(delim, 0)

    @given(st.integers(min_value=0, max_value=5),
        escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), st.datetimes())
    def test_extract_jsonl_list_handles_valid_JSONL_one_per_line(self, 
        size: int, question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
        for delim in ['', ' ', '\t']:
            d = f"{delim}\n{delim}"
            self.do_test_extract_jsonl_list(d,     size, question, label, prescription, body_part, timestamp)
            self.do_test_extract_jsonl_list(','+d, size, question, label, prescription, body_part, timestamp)
            self.do_test_extract_jsonl_list(d+',', size, question, label, prescription, body_part, timestamp)

    @given(st.integers(min_value=0, max_value=5),
        escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), st.datetimes())
    def test_extract_jsonl_list_handles_invalid_JSONL_all_on_one_line(self, 
        size: int, question: str, label: str, prescription: str, body_part: str, timestamp: datetime):
        for delim in ['', ' ', '\t']:
            self.do_test_extract_jsonl_list(delim,     size, question, label, prescription, body_part, timestamp)
            self.do_test_extract_jsonl_list(','+delim, size, question, label, prescription, body_part, timestamp)
            self.do_test_extract_jsonl_list(delim+',', size, question, label, prescription, body_part, timestamp)

    @given(st.dictionaries(st.text(min_size=1, max_size=5), st.integers()))
    def test_dict_pop_returns_key_and_deletes_from_dict(self, dictionary):
        dlen = len(dictionary)
        keys = dictionary.keys()
        for key in list(keys):
            expected_value = dictionary[key]
            actual_value = dict_pop(dictionary, key)
            self.assertEqual(expected_value, actual_value)
            self.assertTrue(key not in dictionary)
            dlen -= 1
            self.assertEqual(dlen, len(dictionary))

    @given(st.dictionaries(st.text(min_size=1, max_size=5), st.integers()))
    def test_dict_pop_returns_None_for_nonexistent_key(self, dictionary):
        dlen = len(dictionary)
        keys = dictionary.keys()
        for key in list(keys):
            key2 = key+key
            if key2 in dictionary:  # just in case...
                key2=key2+key2 
            actual_value = dict_pop(dictionary, key2)
            self.assertEqual(None, actual_value)
            self.assertTrue(key2 not in dictionary)
            self.assertEqual(dlen, len(dictionary))

if __name__ == "__main__":
    unittest.main()