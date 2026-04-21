"""
"Persistent storage" of JSONL data in a local file.
"""

from __future__ import annotations 
import json
import logging
from collections.abc import Hashable
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Callable, Optional

from common.utils import decode_json, encode_json

class FilePersistentStorageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FilePersistentStorage):
            return {"__class__": "FilePersistentStorage", "path": str(obj.storage_file)}
        return super().default(obj)

class FilePersistentStorageDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=FilePersistentStorageDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        if d.get("__class__") == "FilePersistentStorage":
            return FilePersistentStorage(d.get("path"))
        return d

class FilePersistentStorageError(Exception):
    """Custom exception for storage-related errors"""
    pass

class FilePersistentStorage:
    """
    Tool for managing JSONL records in a local file.
    """

    def_json_encoder = FilePersistentStorageEncoder()
    def_json_decoder = FilePersistentStorageDecoder()

    def encode_json(dct: dict[str,Any]) -> str:
        """Create a JSON string from the input object."""
        return FilePersistentStorage.def_json_encoder.encode(dct)

    def decode_json(text: Any) -> dict[str,Any]:
        """Parse a JSON string, returning a dictionary."""
        return FilePersistentStorage.def_json_decoder.decode(text)

    def __init__(self,
        storage_file: Path | str,
        logger: Optional[logging.Logger] = None):
        """
        Initialize the appointment tool.
        
        Args:
        - storage_file: Path to the JSONL file for storing data
        - logger: Optional logger instance
        """
        self.storage_file = Path(storage_file)
        if logger:
            self.logger: logging.Logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.INFO)

        # Create file if it doesn't exist
        self.__create_file(remove_old = False)
    
    def __create_file(self, remove_old: bool = False):
        """
        Create the records file. If it already exists and remove_old is False,
        then nothing is done.
        """
        if remove_old:
            self.storage_file.unlink(missing_ok=True)
        if not self.storage_file.exists():
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            self.storage_file.touch()

    def clear(self):
        """Clear the storage file of all records."""
        self.__create_file(remove_old = True)

    def load(self) -> tuple[list[dict[str, Any]], list[str]]:
        """
        Load records from the JSONL storage file.
        Any timestamps are parsed with datetime.fromisoformat().

        Returns:

        A tuple of lists. The first list has dictionaries successfully parsed
        from the JSONL records. The list reflects the same order found in the file, so when
        later records are intended to override earlier records, that can be 
        inferred by code using this module and the list ordering. The second list
        contains any JSONL records that failed to parse.
        """
        dicts = []
        errors = []
        if self.storage_file.exists():
            with open(self.storage_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = decode_json(line)
                            dicts.append(d)
                        except json.JSONDecodeError as e:
                            errors.append(line)
                            self.logger.error(f"Error parsing record line: {e} (line: {line})")
        return dicts, errors

    def save(self, records: list[dict[str, Any]]) -> int:
        """
        Append the list of records to the JSONL file. To overwrite the
        existing records file, call clear(), then save().
        
        Args:
        - records: list of dictionaries to convert to JSONL and write.

        Returns:
        The count of the number of records written, which should be equal to len(records).
        """
        count = 0
        with open(self.storage_file, 'a') as f:
            for record in records:
                f.write(encode_json(record) + '\n')
                count += 1
        return count
    
    def __str__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        """Create a JSON string from the object."""
        return FilePersistentStorage.def_json_encoder.encode(self)

    def from_json(text: Any) -> FilePersistentStorage:
        """Attempt to parse a JSON object, returning an instance."""
        return FilePersistentStorage.def_json_decoder.decode(text)
