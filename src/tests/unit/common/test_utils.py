"""
Unit tests for the "utils" module using Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import re
import shutil
import unittest
from pathlib import Path
from hypothesis import given, strategies as st

from common.utils import (
    all_use_cases,
    ensure_dirs_exist,
    make_parent_dirs,
    model_dir_name,
)


def valid_dirs(min_size: int = 1, max_size: int = 5):
    """Hypothesis strategy for generating directory names."""
    return st.text(
        alphabet=st.characters(codec="ascii"), min_size=min_size, max_size=max_size
    ).map(lambda s: re.sub(r"\W", "_", s))


class TestUtils(unittest.TestCase): # pylint: disable=unused-variable
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
        """Check model to directory name conversion."""
        s = ":".join(strs)
        expected = s.replace(":", "_")
        self.assertEqual(expected, model_dir_name(s))

    @given(st.sampled_from(use_cases_names))
    def test_use_cases(self, use_case_name: str):
        """Check for expected use case names."""
        self.assertEqual(3, len(self.use_cases))  # sanity check
        self.assertTrue(use_case_name.find(" ") < 0)  # sanity check
        self.assertIsNotNone(self.use_cases.get(use_case_name))

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_that_do_not_exist(self, dirs: list[str]):
        """Check that making making parent directories works."""
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok=False)
        self.assertTrue(path.exists())
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_make_parent_dirs_with_allowed_preexisting_dirs(self, dirs: list[str]):
        """Check that making making parent directories with allowed pre-existing directories works."""
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        file = f"{fdir}/foo.txt"
        path = make_parent_dirs(file, exist_ok=False)
        self.assertTrue(path.exists())
        path2 = make_parent_dirs(file, exist_ok=True)
        self.assertEqual(path, path2)
        self.assertEqual(Path(fdir), path)
        self.clean()

    def do_test_make_parent_dirs(self, exist_ok: bool):
        """Check that making making parent directories for the current working directory does nothing."""
        path = make_parent_dirs("./foo.txt", exist_ok=exist_ok)
        self.assertEqual(Path("."), path)
        self.clean()

    def test_make_parent_dirs_with_file_in_cwd_does_nothing(self):
        """Check that making making parent directories for the current working directory does nothing."""
        do_test_make_parent_dirs(False)

    def test_make_parent_dirs_with_file_in_cwd_ignores_exist_ok_flag(self):
        """Check that making making parent directories for the current working directory ignores the exist_ok flag."""
        do_test_make_parent_dirs(False)
        do_test_make_parent_dirs(True)

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_does_not_raise_for_existing_dirs(self, dirs: list[str]):
        """Check that ensure_dirs_exists does not raise for existing directories."""
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok=True)
        ensure_dirs_exist(fdir)
        self.assertEqual(Path(fdir), path)
        self.clean()

    @given(st.lists(valid_dirs(), max_size=5))
    def test_ensure_dirs_exist_raises_for_missing_dirs(self, dirs: list[str]):
        """Check that ensure_dirs_exists raises for missing directories."""
        fdir = f"{self.test_temp}/{'/'.join(dirs)}"
        with self.assertRaises(ValueError):
            ensure_dirs_exist(fdir)


if __name__ == "__main__":
    unittest.main()
