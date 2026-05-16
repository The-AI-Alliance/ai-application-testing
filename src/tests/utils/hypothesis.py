"""Reusable Hypothesis utilities."""

import re
from hypothesis import strategies as st


def valid_dirs(min_size: int = 1, max_size: int = 5):
    """Hypothesis strategy for generating directory names."""
    return st.text(
        alphabet=st.characters(codec="ascii"), min_size=min_size, max_size=max_size
    ).map(lambda s: re.sub(r"\W", "_", s))


def replacement_keys(
    min_key_size: int = 1, max_key_size: int = 5, min_size: int = 0, max_size: int = 10
):
    """
    Hypothesis strategy for generating a list of strings that do not contains
    `{{...}}`.
    """
    return st.lists(
        st.text(
            alphabet=st.characters(codec="ascii"),
            min_size=min_key_size,
            max_size=max_key_size,
        ).map(lambda s: re.sub(r"[{}]+", "_", s)),
        min_size=min_size,
        max_size=max_size,
    )


def escaped_dquotes(min_size: int = 0, max_size: int = 5):
    return st.text(
        alphabet=st.characters(codec="utf-8"), min_size=min_size, max_size=max_size
    ).map(lambda s: clean_text(s))


def clean_text(s: str) -> str:
    """Fix some problematic substrings that cause problems with JSON conversion."""
    s1 = re.sub(r'"', r"\"", s)
    s2 = re.sub(r"\}[,\s]*\{", "_ _", s1)
    return s2
