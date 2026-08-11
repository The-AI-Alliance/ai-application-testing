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

    def init(self) -> tuple[FilePersistentStorage, Any]:
        """
        Set up the test objects.
        Hack: We return the temp_file, even though it is never used,
        so that it doesn't go out of scope and get deleted prematurely,
        due to the two flags, `delete=True, delete_on_close=False`.
        """
        # Create a temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(  # noqa: SIM115 pylint: disable=consider-using-with
            mode="w", delete=True, delete_on_close=False, suffix=".jsonl"
        )
        temp_file.close()
        tool = FilePersistentStorage(temp_file.name)
        tool.clear()
        return tool, temp_file

    def test_initialization_creates_file(self):
        """Check that initialization creates the JSONL file if it doesn't exist"""
        tool, _ = self.init()
        assert os.path.exists(tool.storage_path)

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
        tool, _ = self.init()
        for d in lst:
            d["timestamp"] = dt
        count = tool.save(lst)
        assert len(lst) == count

        lst2, errors = tool.load()
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
        tool, _ = self.init()
        tool.save(lst)
        count = tool.save(lst)
        assert len(lst) == count

        tool.clear()
        lst2, errors = tool.load()
        assert not lst2, f"list2: {lst2}"
        assert 0 == len(errors), str(errors)
