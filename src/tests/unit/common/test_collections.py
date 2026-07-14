"""
Unit tests for the "collections" module using Hypothesis for property-based testing.
https://hypothesis.readthedocs.io/en/latest/
"""

import unittest
from typing import Any
from hypothesis import given, strategies as st

from common.collections import (
    get_chain,
    dict_permutations,
    dict_pop,
    get,
    mult,
)


class TestCollections(unittest.TestCase):
    """
    Test the collections utilities.
    """

    def _check(self, dictionary: dict[str, Any], n: int = -1):
        actual = dict_permutations(dictionary, max_size=n)

        # Check the size of the returned array.
        def _length(col):
            lc = len(col)
            return lc if n < 0 or lc <= n else n

        lens = [_length(col) for col in dictionary.values()]
        expected_len = mult(lens, skip_zeros=True)
        self.assertEqual(
            expected_len,
            len(actual),
            f"actual: {actual}, d: {dictionary}, n: {n}, lens: {lens}",
        )
        # Check other expected sizes:
        expected_dict_len = 0
        for col in dictionary.values():
            if len(col) > 0:
                expected_dict_len += 1
        for i in range(expected_len):
            for j in range(i + 1, expected_len):
                leni = len(actual[i])
                lenj = len(actual[j])
                self.assertEqual(
                    expected_dict_len,
                    leni,
                    f"i={i}: {expected_dict_len} != {leni}, {actual[i]}",
                )
                self.assertEqual(
                    expected_dict_len,
                    lenj,
                    f"j={j}: {expected_dict_len} != {lenj}, {actual[j]}",
                )
                self.assertNotEqual(
                    actual[i], actual[j], f"{i}, {j}: {actual[i]}, d = {dictionary}"
                )

        # Adding one or more keys with empty values doesn't add to the permutations:
        actual2 = dict_permutations(
            dictionary | {"empty-1": [], "empty-2": []}, max_size=n
        )
        self.assertEqual(expected_len, len(actual2))

    @given(st.integers(min_value=0, max_value=10))
    def test_get_chain_returns_value_at_end_of_chain(self, depth: int):
        """Check that get_chain() returns the value at the end of the chain."""
        keys = [str(i) for i in range(depth)]
        root = {}
        d = root
        for k in keys:
            d[k] = {}
            d = d[k]
        d[str(depth)] = depth
        keys.append(str(depth))
        self.assertEqual(depth, get_chain(root, keys), f"{depth}: {keys}, {d}")

    @given(st.integers(min_value=0, max_value=3))
    def test_get_chain_can_mix_dict_and_sequence_referencing(self, depth: int):
        """Check that get_chain() can mix dictionary and sequence referencing."""
        keys = [str(i) for i in range(depth)]
        root = {}
        d = root
        for k in keys:
            d[k] = {}
            d = d[k]
        ary = [{"zero": 0}, {"one": 1}]
        d[str(depth)] = ary
        keys.append(str(depth))
        self.assertEqual(
            0, get_chain(root, keys + [0, "zero"]), f"{depth}: {keys}, {root}"
        )
        self.assertEqual(
            1, get_chain(root, keys + [1, "one"]), f"{depth}: {keys}, {root}"
        )

    @given(st.integers(min_value=0, max_value=10))
    def test_get_chain_ends_early_and_returns_None_at_first_None_value(
        self, depth: int
    ):
        """Check that get_chain() ends early and returns None at the first None value encountered."""
        keys = [str(i) for i in range(depth)]
        keys2 = [str(i) for i in range(2 * depth)]
        root = {}
        d = root
        for k in keys:
            d[k] = {}
            d = d[k]
        d[str(depth)] = None
        self.assertIsNone(get_chain(root, keys2), f"{depth}: {keys2}, {d}")

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10), st.text(max_size=10), max_size=4
        )
    )
    def test_get_returns_value_for_the_key(self, dictionary: dict[str, str]):
        """Check that get returns the value for the key, when it exists."""
        for key in dictionary:
            self.assertIsNotNone(get(dictionary, key))

    @given(st.sets(st.text(min_size=1, max_size=10), max_size=4))
    def test_get_raises_a_ValueError_if_None_would_be_returned_for_an_unknown_key( # pylint: disable=invalid-name
        self, set: set[str]
    ):
        """Check that get raises a ValueError if None would be returned for an unknown key."""
        dictionary = {}
        for key in set:
            with self.assertRaises(ValueError):
                get(dictionary, key)

    @given(st.sets(st.text(min_size=1, max_size=10), max_size=4))
    def test_get_raises_a_ValueError_if_None_would_be_returned_for_a_known_key_with_None_value_default_ignored( # pylint: disable=invalid-name
        self, keyset: set[str]
    ):
        """Check that get raises a ValueError if None would be returned for a known key with a None value."""
        dictionary = {}
        for key in keyset:
            dictionary[key] = None
            with self.assertRaises(ValueError):
                get(dictionary, key)
            with self.assertRaises(ValueError):
                get(dictionary, key, "hello!")

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=5),
            st.sets(st.text(max_size=10), max_size=4),
            max_size=4,
        )
    )
    def test_dict_permutations(self, dictionary: dict[str, Any]):
        """
        Check that dict_permutations returns a list of dicts with all permutations of single key-values
        We use a set for the values because we want to assume uniqueness, which is how
        this feature will be used.
        """
        self._check(dictionary)

    @given(
        st.dictionaries(
            st.text(min_size=1), st.sets(st.text(), max_size=4), max_size=4
        ),
        st.integers(min_value=0, max_value=4),
    )
    def test_dict_permutations_limit_n(self, dictionary: dict[str, Any], n: int):
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
        dictionary = {"k1": ["v11", "v12"], "k2": ["v21", "v22"]}
        actualm1 = dict_permutations(dictionary, max_size=-1)
        # Note the ordering in expectedm1; this is how the dictionaries happen to be
        # constructed. There is no requirement for this ordering, so this assumption
        # could be break! If so, just verify the two lists are equal in length and and
        # they contain the same dictionary elements.
        expectedm1 = [
            {"k1": "v12", "k2": "v22"},
            {"k1": "v12", "k2": "v21"},
            {"k1": "v11", "k2": "v22"},
            {"k1": "v11", "k2": "v21"},
        ]
        self.assertEqual(expectedm1, actualm1)

        actual0 = dict_permutations(dictionary, max_size=0)
        expected0 = []
        self.assertEqual(expected0, actual0)

        actual1 = dict_permutations(dictionary, max_size=1)
        expected1 = [{"k1": "v11", "k2": "v21"}]
        self.assertEqual(expected1, actual1)

    @given(st.lists(st.integers(), max_size=5))
    def test_mult_with_not_skipping_zeros(self, ints: list[int]):
        """Check that mult() when zeros aren't skipped."""
        expected = 0
        if ints:
            expected = 1
            for n in ints:
                expected *= n

        self.assertEqual(expected, mult(ints))

    @given(st.lists(st.integers(), max_size=5))
    def test_mult_with_skipping_zeros(self, ints: list[int]):
        """Check that mult() when zeros are skipped."""
        ints2 = [n for n in ints if n]
        expected = 0
        if ints2:
            expected = 1
            for n in ints2:
                expected *= n

        self.assertEqual(expected, mult(ints, skip_zeros=True))

    @given(st.dictionaries(st.text(min_size=1, max_size=5), st.integers()))
    def test_dict_pop_returns_value_for_key_and_deletes_from_dict(self, dictionary):
        """Check that dict_pop() returns the value for the key and deletes the pair from the dictionary."""
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
    def test_dict_pop_returns_None_for_nonexistent_key_and_leaves_dict_unchanged(self, dictionary):
        """Check that dict_pop() returns None for a nonexistent key and leaves the dictionary unchanged."""
        dlen = len(dictionary)
        keys = dictionary.keys()
        for key in list(keys):
            key2 = key + key
            if key2 in dictionary:  # just in case...
                key2 = key2 + key2
            actual_value = dict_pop(dictionary, key2)
            self.assertEqual(None, actual_value)
            self.assertTrue(key2 not in dictionary)
            self.assertEqual(dlen, len(dictionary))


if __name__ == "__main__":
    unittest.main()
