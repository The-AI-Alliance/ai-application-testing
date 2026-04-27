"""
Test utilities, e.g., strategy generators for Hypothesis.
"""
from hypothesis import given, strategies as st

def_person_name_part_regex_format = r"['\w][-'\w]{%d,%d}"

def person_name_parts(
    regex_format: str = def_person_name_part_regex_format,
    min_size: int     =  1,
    max_size: int     = 10):

    """
    A Hypothesis strategy for generating parts of a person's name.

    Args:
        - regex_format (str): The allowed format for name parts. It is a `printf`-style 
          format string that takes two integer arguments (i.e., `%d`) provided by
          `min_size`, for the minimum length, and `max_size`, for the maximum length.
          The regex will be used for a full match, even if it doesn't start with "^" nor
          end with "$".
        - min_size (int): The minimum length for the name part; >= 1
        - max_size (int): The maximum length for the name part; >= min_size

    Returns:
        A strategy for parts of a person's name.
    """
    if min_size < 1:
        min_size = 1
    if max_size < min_size:
        max_size = min_size
    # We subtract one, because we already capture the opening character separately.
    regex_str = regex_format % (min_size-1, max_size-1)
    return st.from_regex(regex_str, fullmatch=True)

def person_names(
    regex_format: str     = def_person_name_part_regex_format,
    min_size: int         =  1,
    max_size: int         =  3,
    min_part_length: int  =  1,
    max_part_length: int  = 10):

    """
    A Hypothesis strategy for generating peoples names, consisting of
    one or more name parts, returned as a list of strings.

    Args:
        - regex_format (str): The allowed format for name parts. See documentation for it in `person_name_parts()`.
        - min_size (int): The minimum number of parts in the name, e.g., 3 for "First Middle Last"; >= 1
        - max_size (int): The maximum number of parts in the name, e.g., 3 for "First Middle Last"; >= min_size
        - min_part_length (int): The minimum length for every part of a name; >= 1
        - max_part_length (int): The maximum length for every part of a name; >= min_part_length

    Returns:
        A strategy for names, which will be returned as a list of parts.
    """
    if min_size < 1:
        min_size = 1
    if max_size < min_size:
        max_size = min_size
    return st.lists(person_name_parts(regex_format,
            min_size=min_part_length, max_size=max_part_length),
        min_size=min_size, max_size=max_size)
