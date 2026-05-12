"""Miscellaneous utilities for working with collections."""

from typing import Any, MutableMapping

def get(dictionary: dict[str, Any], key: str, default: Any | None = None) -> Any:
    """
    Instead of returning None, raise a `ValueError` if `None`
    would be returned.
    """
    value = dictionary.get(key, default)
    if value is None:
        raise ValueError(
            f"No value for key {key} and default value is None in {dictionary}."
        )
    else:
        return value


def chain(dictionary: dict[str, Any], keys: list[str]) -> Any | None:
    """
    'Chain' calls to get on `dictionary` and nested dictionaries, stopping
    at the first `None` value returned. This eliminates the tedium of
    doing this one call at a time and checking for None each time.
    If `keys` is empty, `None` is returned.
    """
    value = None
    d = dictionary
    for key in keys:
        value = d.get(key)
        if value is None:
            return value
        else:
            d = value
    return value


def dict_permutations(
    dictionary: dict[str, Any], max_size: int = -1
) -> list[dict[str, Any]]:
    """
    From an input dictionary, where the values are collections, return an array of dictionaries
    with all permutations of the same keys and individual values from the value collections.
    For example, for this input dictionary:
    ```
    d = {
        'k1': ['v11', 'v12'],
        'k2': ['v21', 'v22'],
    }
    ```

    The following array is returned:
    ```
    [{'k2': 'v22', 'k1': 'v12'},
     {'k2': 'v21', 'k1': 'v12'},
     {'k2': 'v22', 'k1': 'v11'},
     {'k2': 'v21', 'k1': 'v11'}]
    ```

    If `max_size` >= 0, the value arrays are effectively truncated to that size, e.g., for
    `max_size == 0`, `[]` will be returned, for `max_size == 1`, `[{'k1': 'v11', 'k2': 'v21'}]`
    will be returned.

    If any key has an empty values collection, no entries for that key will appear in the output.
    For example, with `d` above, `dict_permutations(d) == dict_permutations(d | {'empty':[]})`.
    """

    def perm(array, d):
        if len(d) == 0:
            return array
        else:
            key, values = d.popitem()
            if not values:
                return perm(array, d)
            else:
                array2 = []
                lenv = len(values)
                n = lenv if max_size < 0 or lenv <= max_size else max_size
                for value in list(values)[0:n]:
                    kv = {key: value}
                    if not array:
                        array2.append(kv)
                    else:
                        for d2 in array:
                            array2.append(d2 | kv)
            return perm(array2, d)

    dcopy = dictionary.copy()
    return list(reversed(perm([], dcopy)))  # return in input order!


def mult(collection: list[int], skip_zeros: bool = False) -> int:
    """Multiple the integers in the collection, optionally _skipping zeros!_"""
    values = collection if not skip_zeros else [n for n in collection if n]
    if values:
        result = 1
        for v in values:
            result *= v
        return result
    else:
        return 0

def dict_pop(dictionary: MutableMapping[str, Any], key: str) -> Any:
    """
    Works like dict.pop() should work; rather than raise an exception,
    just return None and don't modify the dictionary.
    """
    try:
        return dictionary.pop(key)
    except KeyError:
        return None
