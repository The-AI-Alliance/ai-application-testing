# Unit tests for the "utils" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st
import unittest
from pathlib import Path
import json, os, re, sys, shutil

from common.utils import (
    all_use_cases,
    ensure_dirs_exist,
    extract_jsonl,
    make_parent_dirs,
    model_dir_name,
    parse_json,
)

class TestUtils(unittest.TestCase):
    """
    Test the utilities.
    """

    use_cases = all_use_cases()
    use_cases_names = list(use_cases.keys())
    use_cases_labels = list(use_cases.values())
    test_temp = './test-temp'

    def valid_dirs(min_size: int = 1, max_size: int = 5):
        return st.text(alphabet=st.characters(codec='ascii'), min_size=min_size, max_size=max_size).map(
            lambda s: re.sub(r'\W', '_', s))
    def escaped_dquotes(min_size: int = 0, max_size: int = 5):
        return st.text(alphabet=st.characters(codec='utf-8'), min_size=min_size, max_size=max_size).map(
            lambda s: re.sub(r'"', r'\"', s))

    def tearDown(self):
        self.clean()

    def clean(self):
        tt = Path(self.test_temp)
        if tt.exists():
            shutil.rmtree(self.test_temp)

    @given(st.lists(valid_dirs(), max_size=5))
    def test_model_dir_name(self, strs: [str]):
        s = ':'.join(strs)
        expected = s.replace(':', '_')
        self.assertEqual(expected, model_dir_name(s))

    @given(st.sampled_from(use_cases_names))
    def test_use_cases(self, use_case_name: str):
        self.assertEqual(3, len(self.use_cases)) # sanity check
        self.assertTrue(use_case_name.find(' ') < 0) # sanity check
        self.assertIsNotNone(self.use_cases.get(use_case_name))

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_that_do_not_exist(self, dirs: [str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok = False)
        self.assertTrue(path.exists())
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_with_allowed_preexisting_dirs(self, dirs: [str]):
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
    def test_ensure_dirs_exist_does_not_raise_for_existing_dirs(self, dirs: [str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok = False)
        ensure_dirs_exist(fdir)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_raises_for_missing_dirs(self, dirs: [str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        with self.assertRaises(ValueError):
            ensure_dirs_exist(fdir)

    @given(escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes())
    def test_parse_json_handles_valid_JSON(self, question: str, label: str, prescription: str, body_part: str):
        """We only worry about parsing responses we expect to receive..."""
        d1 = {
            "question": question,
            "answer": {
                "label": label,
                "prescription": prescription,
                "body-part": body_part
            }
        }
        js = json.dumps(d1)
        d2 = parse_json(js)
        self.assertEqual(question, d1['question'])
        self.assertEqual(question, d2['question'])
        a1 = d1['answer']
        a2 = d2['answer']
        self.assertEqual(label, a1['label'])
        self.assertEqual(prescription, a1['prescription'])
        self.assertEqual(body_part, a1['body-part'])
        self.assertEqual(label, a2['label'])
        self.assertEqual(prescription, a2['prescription'])
        self.assertEqual(body_part, a2['body-part'])


    @given(escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes())
    def test_parse_json_JSONDecoderError_on_bad_input_str(self, question: str, label: str, prescription: str, body_part: str):
        """We only worry about parsing responses we expect to receive..."""
        js = """{{
            {quote}question{quote}: {quote}{question}{quote},
            {quote}answer{quote}: {{
                {quote}label{quote}: {quote}{label}{quote},
                {quote}prescription{quote}: {quote}{prescription}{quote},
                {quote}body-part{quote}: {quote}{body_part}{quote}
            }}
        }}"""
        for quote in ["'", ""]:
            with self.assertRaises(ValueError):
                jsq = js.format(quote=quote, question=question, label=label,
                    prescription=prescription, body_part=body_part)
                parse_json(jsq)
        
        jsdq = js.format(quote='"', question=question, label=label,
                prescription=prescription, body_part=body_part)
        with self.assertRaises(ValueError):
            parse_json('{'+jsdq)
        with self.assertRaises(ValueError):
            parse_json(jsdq+'}')

    def do_test_extract_jsonl(self, delim: str,
        size: int, question: str, label: str, prescription: str, body_part: str):
        """We only worry about parsing responses we expect to receive..."""
        def d(i: int) -> {str,str}:
            return {
                "question": f"{question} {i}",
                "answer": {
                    "label": f"{label} {i}",
                    "prescription": f"{prescription} {i}",
                    "body-part": f"{body_part} {i}",
                }
            }
        jsons = [json.dumps(d(n)) for n in range(size)]
        strs = extract_jsonl(delim.join(jsons))
        self.assertEqual(size, len(strs))
        for n in range(size):
            d = parse_json(strs[n])
            self.assertEqual(f"{question} {n}", d['question'])
            a = d['answer']
            self.assertEqual(f"{label} {n}", a['label'])
            self.assertEqual(f"{prescription} {n}", a['prescription'])
            self.assertEqual(f"{body_part} {n}", a['body-part'])

    @given(st.integers(min_value=0, max_value=5),
        escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes())
    def test_extract_jsonl_handles_valid_JSONL_one_per_line(self, 
        size: int, question: str, label: str, prescription: str, body_part: str):
        """We only worry about parsing responses we expect to receive..."""
        self.do_test_extract_jsonl('\n', size, question, label, prescription, body_part)

    @given(st.integers(min_value=0, max_value=5),
        escaped_dquotes(), escaped_dquotes(), escaped_dquotes(), escaped_dquotes())
    def test_extract_jsonl_handles_invalid_JSONL_all_on_one_line(self, 
        size: int, question: str, label: str, prescription: str, body_part: str):
        """We only worry about parsing responses we expect to receive..."""
        self.do_test_extract_jsonl('',   size, question, label, prescription, body_part)
        self.do_test_extract_jsonl(' ',  size, question, label, prescription, body_part)
        self.do_test_extract_jsonl('\t', size, question, label, prescription, body_part)

if __name__ == "__main__":
    unittest.main()