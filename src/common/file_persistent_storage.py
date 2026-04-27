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

class FilePersistentStorageError(Exception):
    """Custom exception for storage-related errors"""
    pass

class FilePersistentStorage:
    def __init__(self,
        storage_path: Path | str,
        logger: Optional[logging.Logger] = None):
        """
        Initialize the appointment tool.
        
        Args:
            - storage_path: Path to the JSONL file for storing data
            - logger: Optional logger instance
        """
        self.storage_path = Path(storage_path)
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
            self.storage_path.unlink(missing_ok=True)
        if not self.storage_path.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.touch()

    def clear(self):
        """Clear the storage file of all records."""
        self.__create_file(remove_old = True)

    def load(self) -> tuple[list[dict[str, Any]], list[str]]:
        """
        Load records from the JSONL storage file and parses them using `decode_json(line)`.

        Returns:
            A tuple of lists. The first list has dictionaries successfully parsed
            from the JSONL records. The list reflects the same order found in the file, so when
            later records are intended to override earlier records, that can be 
            inferred by code using this module and the list ordering. The second list
            contains any JSONL records that failed to parse.
        """
        dicts = []
        errors = []
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
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
        Append the list of records to the JSONL file, encoding them
        using `encode_json(record)`. To overwrite the
        existing records in the storage file, call `clear()`, then
        `save()` with _all_ the records.
        
        Args:
            - records: list of dictionaries to convert to JSONL and write.

        Returns:
            The count of the number of records written, which should be equal to len(records).
        """
        count = 0
        with open(self.storage_path, 'a') as f:
            for record in records:
                f.write(encode_json(record) + '\n')
                count += 1
        return count
    
    def __str__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        """Create a JSON string from the object."""
        return json.dumps({
            '__class__':    'FilePersistentStorage', 
            'storage_path': self.storage_path,
        })

    def from_json(text: Any) -> FilePersistentStorage:
        """Attempt to parse a JSON object, returning an instance."""
        d = json.loads(text)
        return FilePersistentStorage(d.get('storage_path', ''))
