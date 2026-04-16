# Unit tests for the "collections" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

import os, tempfile
import unittest
from datetime import datetime
from hypothesis import given, strategies as st
from pathlib import Path
from typing import Any

from common.file_persistent_storage import FilePersistentStorage

class TestFilePersistentStorage(unittest.TestCase):
    """
    Test the FilePersistentStorage utility.
    """

    def _make_tool(self, file_name: str = '', clear: bool = True) -> FilePersistentStorage:
        if not file_name:
            file_name = self.temp_file.name
        self.tool = FilePersistentStorage(file_name)
        if clear:
            self.tool.clear()
        return self.tool

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.temp_file.close()
        self._make_tool()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_initialization_creates_file(self):
        """Test that initialization creates the JSONL file if it doesn't exist"""
        self.assertTrue(os.path.exists(self.temp_file.name))

    @given(
        st.lists(
            st.dictionaries(
                st.text(min_size=1, max_size=10), 
                st.one_of(
                    st.text(max_size=10), 
                    st.integers(), 
                    st.floats(
                        allow_nan=False,
                        allow_infinity=False,
                        allow_subnormal=False))),
            min_size = 0, max_size=5),
        st.datetimes())
    def test_save_load(self, lst: list[dict[str,Any]], dt: datetime):
        """
        Check that saving, then reloading dictionaries works as expected.
        """
        self.tool.clear()
        for d in lst:
            d['timestamp'] = dt
        count = self.tool.save(lst)
        self.assertEqual(len(lst), count)
        
        lst2, errors = self.tool.load()
        self.assertEqual(lst, lst2, f"list: {lst}, list2: {lst2}")
        self.assertEqual(0, len(errors), str(errors))

    @given(
        st.lists(
            st.dictionaries(
                st.text(min_size=1, max_size=10), 
                st.one_of(
                    st.text(max_size=10), 
                    st.integers(), 
                    st.floats(
                        allow_nan=False,
                        allow_infinity=False,
                        allow_subnormal=False))),
            min_size = 0, max_size=5))
    def test_clear_empties_file(self, lst: list[dict[str,Any]]):
        """
        Check that saving, then reloading dictionaries works as expected.
        """
        self.tool.clear()
        self.tool.save(lst)
        count = self.tool.save(lst)
        self.assertEqual(len(lst), count)

        self.tool.clear()
        lst2, errors = self.tool.load()
        self.assertEqual([], lst2, f"list2: {lst2}")
        self.assertEqual(0, len(errors), str(errors))


if __name__ == "__main__":
    unittest.main()