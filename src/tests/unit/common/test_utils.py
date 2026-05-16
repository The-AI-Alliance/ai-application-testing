"""
Unit tests for the "utils" module using Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import shutil
import unittest
from pathlib import Path
from hypothesis import given, strategies as st

from common.utils import (
    all_use_cases,
    ensure_dirs_exist,
    make_parent_dirs,
    model_dir_name,
    replace_variables,
)

from tests.utils.hypothesis import valid_dirs, replacement_keys


class TestUtils(unittest.TestCase):
    """
    Test the common utilities.
    """

    use_cases = all_use_cases()
    use_cases_names = list(use_cases.keys())
    use_cases_labels = list(use_cases.values())
    test_temp = "./test-temp"

    def tearDown(self):
        self.clean()

    def clean(self):
        """Remove the temporary file and its directory."""
        tt = Path(self.test_temp)
        if tt.exists():
            shutil.rmtree(self.test_temp)

    @given(st.lists(valid_dirs(), max_size=5))
    def test_model_dir_name(self, strs: list[str]):
        s = ":".join(strs)
        expected = s.replace(":", "_")
        self.assertEqual(expected, model_dir_name(s))

    @given(st.sampled_from(use_cases_names))
    def test_use_cases(self, use_case_name: str):
        self.assertEqual(3, len(self.use_cases))  # sanity check
        self.assertTrue(use_case_name.find(" ") < 0)  # sanity check
        self.assertIsNotNone(self.use_cases.get(use_case_name))

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_that_do_not_exist(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok=False)
        self.assertTrue(path.exists())
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_with_allowed_preexisting_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok=False)
        self.assertTrue(path.exists())
        path2 = make_parent_dirs(file, exist_ok=True)
        self.assertEqual(path, path2)
        self.assertEqual(Path(fdir), path)
        self.clean()

    def test_make_parent_dirs_with_file_in_cwd(self):
        path = make_parent_dirs("./foo.txt", exist_ok=False)
        self.assertEqual(Path("."), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_does_not_raise_for_existing_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok=True)
        ensure_dirs_exist(fdir)
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_raises_for_missing_dirs(self, dirs: list[str]):
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        with self.assertRaises(ValueError):
            ensure_dirs_exist(fdir)

    @given(replacement_keys(), st.text())
    def test_replace_variables_replaces_keys_with_values(
        self, keys: list[str], separator: str
    ):
        keys2 = ["{{" + key + "}}" for key in keys]
        values = [key.upper() for key in keys]
        kvs = dict([(keys[i], values[i]) for i in list(range(len(keys)))])
        s = separator + separator.join(keys2) + separator
        expected = separator + separator.join(values) + separator
        actual = replace_variables(s, kvs)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
