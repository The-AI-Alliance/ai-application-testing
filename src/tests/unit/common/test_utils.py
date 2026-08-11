"""
Unit tests for the common "utils" module.
Uses Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import re
import shutil
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from common.utils import (
    ExpectedFail,
    all_use_cases,
    ensure_dirs_exist,
    make_parent_dirs,
    model_dir_name,
)

USE_CASES = all_use_cases()
USE_CASES_NAMES = list(USE_CASES.keys())
# USE_CASES_LABELS = list(USE_CASES.values())
TEST_TEMP = "./test-temp"


def valid_dirs(min_size: int = 1, max_size: int = 5):
    """Hypothesis strategy for generating directory names."""
    return st.text(alphabet=st.characters(codec="ascii"), min_size=min_size, max_size=max_size).map(
        lambda s: re.sub(r"\W", "_", s)
    )


def clean():
    """Remove the temporary file and its directory."""
    tt = Path(TEST_TEMP)
    if tt.exists():
        shutil.rmtree(TEST_TEMP)


# pylint: disable=unused-variable


@given(st.text())
def test_expected_fail(label: str):
    """Test that an expected failure occurs."""

    def should_raise(exc):
        raise exc

    def should_not_raise():
        pass

    class ExpectedException(BaseException):
        """For testing expected exceptions."""

        def __init__(self, msg):
            super().__init__(msg)

    ef = ExpectedFail(ValueError)
    ef(lambda: should_raise(ValueError(f"oops! {label}")))
    try:
        ef(lambda: should_raise(ExpectedException(f"fail! {label}")))
    except AssertionError:
        pass
    try:
        ef(should_not_raise)
    except AssertionError:
        pass


@given(st.lists(valid_dirs(), max_size=5))
def test_model_dir_name(strs: list[str]):
    """Check model to directory name conversion."""
    s = ":".join(strs)
    expected = s.replace(":", "_")
    assert expected == model_dir_name(s)


@given(st.sampled_from(USE_CASES_NAMES))
def test_use_cases(use_case_name: str):
    """Check for expected use case names."""
    assert 3 == len(USE_CASES)  # sanity checl
    assert use_case_name.find(" ") < 0  # sanity check
    assert USE_CASES.get(use_case_name) is not None


@given(st.lists(valid_dirs(), max_size=5))
def test_make_parent_dirs_that_do_not_exist(dirs: list[str]):
    """Check that making making parent directories works."""
    fdir = f"{TEST_TEMP}/{'/'.join(dirs)}"
    file = f"{fdir}/foo.txt"
    path = make_parent_dirs(file, exist_ok=False)
    assert path.exists()
    assert Path(fdir) == path
    clean()


@given(st.lists(valid_dirs(), max_size=5))
def test_make_parent_dirs_with_allowed_preexisting_dirs(dirs: list[str]):
    """Check that making making parent directories with allowed pre-existing directories works."""
    fdir = f"{TEST_TEMP}/{'/'.join(dirs)}"
    file = f"{fdir}/foo.txt"
    path = make_parent_dirs(file, exist_ok=False)
    assert path.exists()
    path2 = make_parent_dirs(file, exist_ok=True)
    assert path == path2
    assert Path(fdir) == path
    clean()


def do_test_make_parent_dirs(exist_ok: bool):
    """Check that making making parent directories for the current working directory does nothing."""
    path = make_parent_dirs("./foo.txt", exist_ok=exist_ok)
    assert Path(".") == path
    clean()


def test_make_parent_dirs_with_file_in_cwd_does_nothing():
    """Check that making making parent directories for the current working directory does nothing."""
    do_test_make_parent_dirs(False)


def test_make_parent_dirs_with_file_in_cwd_ignores_exist_ok_flag():
    """Check that making making parent directories for the current working directory ignores the exist_ok flag."""
    do_test_make_parent_dirs(False)
    do_test_make_parent_dirs(True)


@given(st.lists(valid_dirs(), max_size=5))
def test_ensure_dirs_exist_does_not_raise_for_existing_dirs(dirs: list[str]):
    """Check that ensure_dirs_exists does not raise for existing directories."""
    fdir = f"{TEST_TEMP}/{'/'.join(dirs)}"
    path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok=True)
    ensure_dirs_exist(fdir)
    assert Path(fdir) == path
    clean()


@given(st.lists(valid_dirs(), max_size=5))
def test_ensure_dirs_exist_raises_for_missing_dirs(dirs: list[str]):
    """Check that ensure_dirs_exists raises for missing directories."""
    fdir = f"{TEST_TEMP}/{'/'.join(dirs)}"
    ef = ExpectedFail(ValueError)
    ef(lambda: ensure_dirs_exist(fdir))
