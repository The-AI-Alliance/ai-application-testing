"""
Unit tests for the common "utils" module.
Uses Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import re
import shutil
from datetime import timedelta
from pathlib import Path
from hypothesis import given, strategies as st

from common.utils import (
    all_use_cases,
    datetimes_approx_equal,
    ensure_dirs_exist,
    make_parent_dirs,
    model_dir_name,
    ExpectedFail,
)

from tests.common.hypothesis.datetimes import year_2000


def valid_dirs(min_size: int = 1, max_size: int = 5):
    """Hypothesis strategy for generating directory names."""
    return st.text(alphabet=st.characters(codec="ascii"), min_size=min_size, max_size=max_size).map(
        lambda s: re.sub(r"\W", "_", s)
    )


def test_expected_fail():
    def foo(exc):
        raise exc

    def bar(msg):
        print(msg)

    class FooException(BaseException):
        def __init__(self, msg):
            super().__init__(msg)

    ef = ExpectedFail(ValueError)
    ef(lambda: foo(ValueError("oops!")))
    try:
        ef(lambda: foo(FooException("fail!")))
    except AssertionError:
        pass
    try:
        ef(lambda: bar("Didn't fail!"))
    except AssertionError:
        pass


@given(st.datetimes(min_value=year_2000), st.lists(st.integers(min_value=-120, max_value=120), min_size=0, max_size=10))
def test_datetimes_approx_equal_returns_true_and_empty_string_if_datetimes_approx_equal(dt, ns):
    for n in ns:
        delta = timedelta(seconds=n)
        dt2 = dt + delta
        eql, msg = datetimes_approx_equal(dt, dt2, delta)
        assert eql
        assert msg == ""


@given(st.datetimes(min_value=year_2000), st.lists(st.integers(min_value=1, max_value=4), min_size=0, max_size=3))
def test_datetimes_approx_equal_returns_false_and_non_empty_string_if_not_datetimes_approx_equal(dt, ns):
    for n in ns:
        delta = timedelta(seconds=n)
        delta1 = timedelta(seconds=n + 1)
        dtp = dt + delta1
        eqlp, msgp = datetimes_approx_equal(dt, dtp, delta)
        assert not eqlp
        assert msgp != ""
        dtm = dt - delta1
        eqlm, msgm = datetimes_approx_equal(dt, dtm, delta)
        assert not eqlm
        assert msgm != ""


use_cases = all_use_cases()
use_cases_names = list(use_cases.keys())
use_cases_labels = list(use_cases.values())
test_temp = "./test-temp"


def clean():
    """Remove the temporary file and its directory."""
    tt = Path(test_temp)
    if tt.exists():
        shutil.rmtree(test_temp)


clean()


@given(st.lists(valid_dirs(), max_size=5))
def test_model_dir_name(strs: list[str]):
    """Check model to directory name conversion."""
    s = ":".join(strs)
    expected = s.replace(":", "_")
    assert expected == model_dir_name(s)


@given(st.sampled_from(use_cases_names))
def test_use_cases(use_case_name: str):
    """Check for expected use case names."""
    assert 3 == len(use_cases)  # sanity checl
    assert use_case_name.find(" ") < 0  # sanity check
    assert use_cases.get(use_case_name) is not None


@given(st.lists(valid_dirs(), max_size=5))
def test_make_parent_dirs_that_do_not_exist(dirs: list[str]):
    """Check that making making parent directories works."""
    fdir = f"{test_temp}/{'/'.join(dirs)}"
    file = f"{fdir}/foo.txt"
    path = make_parent_dirs(file, exist_ok=False)
    assert path.exists()
    assert Path(fdir) == path
    clean()


@given(st.lists(valid_dirs(), max_size=5))
def test_make_parent_dirs_with_allowed_preexisting_dirs(dirs: list[str]):
    """Check that making making parent directories with allowed pre-existing directories works."""
    fdir = f"{test_temp}/{'/'.join(dirs)}"
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
    fdir = f"{test_temp}/{'/'.join(dirs)}"
    path = make_parent_dirs(f"{fdir}/foo.txt", exist_ok=True)
    ensure_dirs_exist(fdir)
    assert Path(fdir) == path
    clean()


@given(st.lists(valid_dirs(), max_size=5))
def test_ensure_dirs_exist_raises_for_missing_dirs(dirs: list[str]):
    """Check that ensure_dirs_exists raises for missing directories."""
    fdir = f"{test_temp}/{'/'.join(dirs)}"
    ef = ExpectedFail(ValueError)
    ef(lambda: ensure_dirs_exist(fdir))
