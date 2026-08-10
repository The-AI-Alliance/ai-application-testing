"""
Unit tests for the "collections" module using Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import os
import tempfile
from datetime import datetime
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from common.file_persistent_storage import FilePersistentStorage
from tests.common.hypothesis.datetimes import local_datetimes_2000

# pylint: disable=unused-variable,missing-function-docstring


class TestFilePersistentStorageUtil:
    """Class to test file persistent storage."""

    def __init__(self):
        """Set up test fixtures"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(  # noqa: SIM115 pylint: disable=consider-using-with
            mode="w", delete=True, delete_on_close=False, suffix=".jsonl"
        )
        self.temp_file.close()
        self.tool = FilePersistentStorage(self.temp_file.name)
        self.tool.clear()

    def test_initialization_creates_file(self):
        """Check that initialization creates the JSONL file if it doesn't exist"""
        # self.init()
        assert os.path.exists(self.temp_file.name)

    @given(
        st.lists(
            st.dictionaries(
                st.text(min_size=1, max_size=10),
                st.one_of(
                    st.text(max_size=10),
                    st.integers(),
                    st.floats(allow_nan=False, allow_infinity=False, allow_subnormal=False),
                ),
            ),
            min_size=0,
            max_size=5,
        ),
        local_datetimes_2000(),
    )
    def test_save_load(self, lst: list[dict[str, Any]], dt: datetime):
        """
        Check that saving, then reloading dictionaries works as expected.
        """
        # self.init()
        for d in lst:
            d["timestamp"] = dt
        count = self.tool.save(lst)
        assert len(lst) == count

        lst2, errors = self.tool.load()
        assert lst == lst2, f"list: {lst}, list2: {lst2}"
        assert 0 == len(errors), str(errors)

    @given(
        st.lists(
            st.dictionaries(
                st.text(min_size=1, max_size=10),
                st.one_of(
                    st.text(max_size=10),
                    st.integers(),
                    st.floats(allow_nan=False, allow_infinity=False, allow_subnormal=False),
                ),
            ),
            min_size=0,
            max_size=5,
        )
    )
    def test_clear_empties_file(self, lst: list[dict[str, Any]]):
        """
        Check that saving, then reloading dictionaries works as expected.
        """
        # self.init()
        self.tool.save(lst)
        count = self.tool.save(lst)
        assert len(lst) == count

        self.tool.clear()
        lst2, errors = self.tool.load()
        assert not lst2, f"list2: {lst2}"
        assert 0 == len(errors), str(errors)
