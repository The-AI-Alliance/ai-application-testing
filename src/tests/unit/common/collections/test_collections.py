# Unit tests for the "collections" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

import json, os, re, sys, shutil
import unittest
from hypothesis import given, strategies as st
from pathlib import Path
from typing import Any

from common.collections import dict_permutations, mult

class TestCollections(unittest.TestCase):
    """
    Test the collections utilities.
    """

    def _check(self, dictionary: dict[str,Any], n:int = -1):
        actual = dict_permutations(dictionary, max_size=n)
        # Check the size of the returned array.
        def _length(col):
            lc = len(col)
            return lc if n < 0 or lc <= n else n
        lens = [_length(col) for col in dictionary.values()]
        expected_len = mult(lens, skip_zeros=True)
        self.assertEqual(expected_len, len(actual), f"actual: {actual}, d: {dictionary}, n: {n}, lens: {lens}")
        # Check other expected sizes:
        expected_dict_len = sum([1 for col in dictionary.values() if len(col) > 0])
        for i in range(expected_len):
            for j in range(i+1, expected_len):
                leni = len(actual[i])
                lenj = len(actual[j])
                self.assertEqual(expected_dict_len, leni, f"i={i}: {expected_dict_len} != {leni}, {actual[i]}")
                self.assertEqual(expected_dict_len, lenj, f"j={j}: {expected_dict_len} != {lenj}, {actual[j]}")
                self.assertNotEqual(actual[i], actual[j], f"{i}, {j}: {actual[i]}, d = {dictionary}")

        # Adding one or more keys with empty values doesn't add to the permutations:
        actual2 = dict_permutations(dictionary | {'empty-1': [], 'empty-2': []}, max_size=n)
        self.assertEqual(expected_len, len(actual2))

    @given(
        st.dictionaries(st.text(min_size=1, max_size=10), st.sets(st.text(max_size=10), max_size=4), max_size=4))
    def test_dict_permutations(self, dictionary: dict[str,Any]):
        """
        Check that dict_permutations returns a list of dicts with all permutations of single key-values
        We use a set for the values because we want to assume uniqueness, which is how
        this feature will be used.
        """
        self._check(dictionary)

    @given(
        st.dictionaries(st.text(min_size=1), st.sets(st.text(), max_size=4), max_size=4),
        st.integers(min_value=0, max_value=4))
    def test_dict_permutations_limit_n(self, dictionary: dict[str,Any], n: int):
        """
        Check that dict_permutations returns a list of dicts with all permutations of single key-values,
        but truncating the input collections to size n.
        We use a set for the values because we want to assume uniqueness, which is how
        this feature will be used.
        """
        self._check(dictionary, n=n)

    def test_dict_permutations_limit_n_special_cases(self):
        """
        Check that dict_permutations returns a list of dicts with all permutations of 
        the single key-values, but truncating the input collections to size n.
        We use a set for the values because we want to assume uniqueness, which is how
        this feature will be used.
        Manually check a few cases.
        """
        dictionary = {'k1': ['v11', 'v12'], 'k2': ['v21', 'v22']}
        actualm1 = dict_permutations(dictionary, max_size=-1)
        # Note the ordering in expectedm1; this is how the dictionaries happen to be
        # constructed. There is no requirement for this ordering, so this assumption
        # could be break! If so, just verify the two lists are equal in length and and
        # they contain the same dictionary elements.
        expectedm1 = [
            {'k1': 'v12', 'k2': 'v22'},
            {'k1': 'v12', 'k2': 'v21'},
            {'k1': 'v11', 'k2': 'v22'},
            {'k1': 'v11', 'k2': 'v21'},
        ]
        self.assertEqual(expectedm1, actualm1)

        actual0 = dict_permutations(dictionary, max_size=0)
        expected0 = []
        self.assertEqual(expected0, actual0)

        actual1 = dict_permutations(dictionary, max_size=1)
        expected1 = [{'k1': 'v11', 'k2': 'v21'}]
        self.assertEqual(expected1, actual1)

    @given(st.lists(st.integers(), max_size=5))
    def test_mult_with_not_skipping_zeros(self, ints: list[int]):
        expected = 0
        if ints:
            expected = 1
            for n in ints:
                expected *= n

        self.assertEqual(expected, mult(ints))

    @given(st.lists(st.integers(), max_size=5))
    def test_mult_with_skipping_zeros(self, ints: list[int]):
        ints2 = [n for n in ints if n]
        expected = 0
        if ints2:
            expected = 1
            for n in ints2:
                expected *= n

        self.assertEqual(expected, mult(ints, skip_zeros=True))

if __name__ == "__main__":
    unittest.main()