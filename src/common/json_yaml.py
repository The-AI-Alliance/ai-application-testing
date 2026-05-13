# Allow types to self-reference during their definitions.
# from __future__ import annotations

import json
import re
import yaml
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Mapping, MutableMapping


def load_yaml(path: Path) -> Mapping[str, Any]:
    """Parse a YAML file and return the corresponding Mapping."""
    return yaml.safe_load(path.read_text())


class DatetimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return {"__class__": "datetime", "iso_str": o.isoformat()}
        return super().default(o)


class DatetimeDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=DatetimeDecoder.from_dict)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> Any:
        if d.get("__class__") == "datetime":
            iso_str = d.get("iso_str", "")
            if iso_str:
                return datetime.fromisoformat(iso_str)
        return d


def_datetime_encoder = DatetimeEncoder()
def_datetime_decoder = DatetimeDecoder()


def encode_json(dct: Mapping[str, Any]) -> str:
    """Create a JSON string from the input object."""
    return def_datetime_encoder.encode(dct)


def decode_json(text: Any) -> MutableMapping[str, Any]:
    """Parse a JSON string, returning a dictionary or raise a ValueError error string if parsing fails."""
    try:
        obj = def_datetime_decoder.decode(text)
        return obj
    except (JSONDecodeError, TypeError) as err:
        raise ValueError(
            f"JSONDecodeError or TypeError {err}: text not JSON? <{text}> (type: {type(text)})"
        ) from err


def extract_jsonl_list(text: str) -> tuple[list[str], list[str]]:
    """
    Parse the input text and return a list of JSONL strings.

    Sometimes the JSONL we ask for comes back without line feeds between the JSONL docs.
    We also don't want commas between the JSONL records.
    Try to detect and fix these cases, then split the string into JSONL lines.

    Args:
        - text to parse into a list of JSONL records

    Return
        Tuple of two lists of strings. The first list is the successfully
        parsed JSONL strings. The second list are any "substrings" of the
        input text that didn't parse. Hopefully, this list is empty.
        If the input string is empty, striped for leading and trailing whitespace,
        ([],[]) is returned.
    """
    if not text.strip():
        return [], []
    split = re.sub(r"\}[,\s]*\{", "}\x00{", text)  # Use an unlikely delimiter...
    fixed = re.split("\x00", split)
    jsonls = []
    errors = []
    for s in fixed:
        try:
            decode_json(s)
            # It parsed! Use s
            jsonls.append(s)
        except ValueError:
            errors.append(s)
    return jsonls, errors


def from_json(json_str: str, keys_indices: list[Any]) -> Any:
    """
    Parse the input JSON string and return the value found by
    using the list of keys_indices _or_ list indices, one at a time.
    When more than one key is specified, all of them except the
    last must return either a dictionary or a list, depending on
    what the next "key" is.

    Args:
        - json_str (str): The JSON string to parse.
        - keys_indices (list[Any]): a non-empty list of strings and/or integers.
          If a value is a `str`, it is assumed to be a dictionary key.
          If a value is an `int`, it is assumed to be a list index.
          If a value is a different type, `ValueError` is raised.

    Return:
        If successful, the value found by walking the keys and indices.
        If unsuccessful, one of the following exceptions is raised:
        * ValueError for an empty keys_indices list.
        * JSONDecodeError if the line can't be parsed as JSON.
        * KeyError if the dictionary from the parsed JSON doesn't have a key specified.
        * TypeError if a previous key in the list of keys_indices returned a non-dictionary or non-list object.
    """
    if not keys_indices:
        raise ValueError("Input keys must be nonzero length!")

    value = json.loads(json_str)
    for key_index in keys_indices:
        value = value[key_index]
    return value
