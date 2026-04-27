"""
Abstraction for tool that manages "resources".
"""

# Allow types to self-reference during their definitions.
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Callable, Tuple
from uuid import uuid4

from common.file_persistent_storage import FilePersistentStorage

class ResourceManager:
    """
    A simple tool for managing "resources" using local file storage for persistence.
    
    Resources are stored in a JSONL file where each line is a JSON object
    representing a resource instance. The method return values are designed to work
    with LLMs in an agent context.
    """

    def __init__(self,
        resources_file: Path | str,
        start_empty: bool = False,
        logger: logging.Logger | None = None):
        """
        Initialize the manager.
        
        Args:
            - resources_file (Path | str): Path to the JSONL file storing the resources
            - start_empty (bool): True if we should clear the file and start "empty" or False if we should just load whatever resources the file already contains.
            - logger (logging.Logger | None): Optional logger instance; it not provided a default logger is created
        """
        if logger:
            self.logger: logging.Logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.INFO)

        self.storage = FilePersistentStorage(Path(resources_file), logger)
        self.resources: dict[str, dict[str, Any]] = {}
        if start_empty:
            self.storage.clear()
            self.logger.info("Starting 'empty' with no resource records")
        else:
            all_count, loaded_count, errors = self._load_resources()
            self.logger.info(f"Loaded {loaded_count} resource records (out of {all_count} read)")
            if errors:
                self.logger.error(f"Errors while loading resource records: {', '.join(errors)}")

    def clear(self):
        """Remove all resources and clear the persistent records."""
        self.resources.clear()
        self.storage.clear()

    def _ignore(self, resource: dict[str,Any]) -> bool:
        """
        A hook that subclasses can override to tell methods to "ignore"
        a resource for various actions. This is designed to support the case
        where updates are made to a resource in the persistent file, but older
        versions exist in the file, etc.
        """
        return False

    def _load_resources(self) -> tuple[int,int,list[str]]:
        """
        Load resources from the JSONL file. `self._ignore(resource)` is called
        on all loaded resources and any of them for which `True` is returned
        are ignored.
        
        Returns:
            A tuple `(all_count, loaded_count, list[messages])`, where `all_count` is the count of all 
            resource records in storage, `loaded_count` is <= `all_count` is the number
            successfully parsed and not filtered out by `self._ignore()`, and `list[messages]`
            are error messages or [] if no errors occurred.
        """
        resources, errors = self.storage.load()
        loaded_count = len(resources)
        error_count  = len(errors)
        all_count    = loaded_count + error_count
        if errors:
            self.logger.error(f"{error_count} records out of {all_count} failed to parse: {errors}")

        self.resources = {}
        for resource in resources:
            # Only load non-cancelled resources and those with ids.
            if not self._ignore(resource):
                id = resource.get('id')
                if id:
                    self.resources[id] = resource
                else:
                    error_msg = f"resource doesn't have an id! resource = {resource}."
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    error_count  += 1
                    loaded_count -= 1
        return all_count, loaded_count, errors
    
    def _save_resources(self, resources: list[dict[str, Any]]) -> tuple[int,str]:
        """
        Append one or more resources to the JSONL file.
        
        Args:
            - resources(list[dict[str, Any]]): A list of resource dictionaries to save.

        Returns:
            A tuple with the count of records saved, which should equal the length of 
            the input records list, and an error message string or '' if no errors occurred.
        """
        count = self.storage.save(resources)
        lena = len(resources)
        error_msg = ''
        if count != lena:
            diff = lena - count
            error_msg = f"Failed to save {diff} out of {lena} resources to the storage file {self.storage.storage_path}. resources = {resources}"
            self.logger.error(error_msg)
        return count, error_msg

    def _is_valid_date_time(self, 
        a_date_time: datetime,
        in_the_past_allowed: bool = False,
        unique_datetime_key: str = '') -> tuple[bool, str]:
        """
        Check if the resource time is valid. Subclasses can add more filtering
        by implementing `_further_date_time_validation()`.
        
        Args:
            - a_date_time (datetime: The proposed resource time
            - in_the_past_allowed (bool): If False (default), a time is invalid if it is in the past. 
              To facilitate some scenarios around "now", like tests, we actually require the
              time to be within one second of now. If the argument is True, then past datetimes 
              are allowed without constraints.
            - unique_datetime_key (str): If not empty, we will check all resources for datetimes 
              with this key and treat `a_date_time` as invalid if any of those found datetimes
              are within one second of `a_date_time`. However, any resources where `self._ignore()`
              returns True won't be checked.
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        one_second = timedelta(seconds=1)
        min_allowed_datetime = datetime.now() - one_second 
        if not in_the_past_allowed and a_date_time < min_allowed_datetime:
            return False, "The date-time is in the past, which is not allowed."
        
        success, message = self._further_date_time_validation(a_date_time)
        if not success:
            return success, message

        # Check if the time slot is already "used". We check if any
        # occupied times are within 1 second of the proposed time, but
        # ignore resources if `ignore_filter(resource)` returns `True`.
        if unique_datetime_key:
            for resource in self.resources.values():
                dt = resource.get(unique_datetime_key)
                if not dt:
                    self.logger.error(f"""_is_valid_date_time(): Resource found without a datetime for key "{unique_datetime_key}"! {resource}""")
                else:
                    dtm1 = dt - one_second 
                    dtp1 = dt + one_second
                    if not self._ignore(resource) and dtm1 < a_date_time and dtp1 > a_date_time:
                        return False, f"""The time slot {a_date_time} for key "{unique_datetime_key}" is already reserved."""
        
        return True, ""
    
    def _further_date_time_validation(self, a_date_time: datetime) -> tuple[bool,str]:
        """
        A hook for subclasses to validate the input datetime.

        Args:
            - a_date_time (datetime): A datetime to validate
            
        Returns:
            A tuple with `(True, '')` on success or `(False, error_message)` on failure.
        """
        return True, ''

    def _create_resource(self, fields: dict[str,Any]) -> tuple[str,str]:
        """
        Create a new resource. This method is intended to be called by
        subclass "domain-specific" methods, rather than being called directly
        by users. Calls `_is_valid_resource()` to perform any validation required 
        on the input `fields`.
        
        Args:
            - fields (dict[str,Any]): The dictionary to use to create the resource record.
              Calls `_is_valid_resource()` to perform any validation required 
              on the input `fields`.
            
        Returns:
            A tuple with `(id, success_message)` on success, where `id` is the non-empty 
            string with the id (a UUID) of the successfully-created resource, or on failure,
            `('', error_message)`.
        """        
        success, message = self._is_valid_resource(fields)
        if not success:
            self.logger.error(f"_create_resource(): {message}")
            return '', message

        # Create the resource and save it to the persistent file.
        resource_id = str(uuid4())
        fields['id'] = resource_id
        self.resources[resource_id] = fields
        self._save_resources([fields])
        success_msg = f"Resource created at {datetime.now()} with ID {resource_id}."
        self.logger.info(success_msg)
        return resource_id, success_msg
        
    def _is_valid_resource(self, fields: dict[str,Any]) -> tuple[bool,str]:
        """
        A hook for subclasses to validate the fields for a resource.
        Args:
            - fields (dict[str,Any]): The dictionary to use to create the resource record.
            
        Returns:
            A tuple with `(True, '')` on success or `(False, error_message)` on failure.
        """
        return True, ''

    def set_resources(
        self,
        resources: list[dict[str,Any]]
    ) -> Tuple[int, str]:
        """
        Set the resources, replacing the current list. Normally, _create_resource() should be used.
        This method is primarily for "deserializing" from storage, like JSON.
        
        Args:
            - resources (list[dict[str,Any]]): list of resources, used to replace _all_ the existing resources.
              Each dictionary must have an `id` key-value pair and the values must be unique.
              Calls `_is_valid_resource()` to perform some validation required on the input "fields" for each resource.
            
        Returns:
            When successful, returns the count of resources set, which will equal `len(resources)`, 
            and an empty message string. If unsuccessful, e.g., one or resources fail validation,
            then returns 0 and an error message string, in which case no changes are made to the 
            existing resources.
        """
        # Unique ids?
        ids = [a['id'] for a in resources]
        unique = set(ids)
        if len(unique) != len(ids):
            return 0, f"{len(ids) - len(unique)} out of {len(ids)} ids are not unique! {ids}"

        # Validate the resource records
        errors = []
        good_resources = []
        for resource in resources:
            success, message = self._is_valid_resource(resource)
            if success:
                good_resources.append(resource)
            else:
                errors.append(f""" "{resource}" -> Error: {message}""")
        if errors:
            error_msg = f"{len(errors)} resources are invalid: [{", ".join(errors)}]"
            self.logger.error(error_msg)
            return 0, error_msg
        
        # All good at this point!
        # Save to memory and file
        self.clear()
        self.resources = dict([(a['id'], a) for a in resources])
        self._save_resources(resources)
        self.logger.info(f"Records replaced with {len(self.resources)} new resources.")
        return len(self.resources), ''
        
    def get_resources_count(self) -> int:
        """
        Return the number of resources, ignoring those where 
        `self._ignore(resource)` returns `True`.
        """
        count = 0
        for resource in self.resources.values():
            if not self._ignore(resource):
                count += 1
        return count

    def get_resource_by_id(self, resource_id: str) -> dict[str, Any]:
        """
        Get a specific resource by ID.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            Resource dictionary or {} if not found
        """
        return self.resources.get(resource_id, {})

    def get_resources_by_criteria(self, 
        criteria: dict[str,Callable[[Any],bool]],
        sort_by_key: str = '') -> list[dict[str,Any]]:
        """
        Retrieve the resources for the specified criteria. First, locate
        the key-values in a resource for each key in `criteria`. Then, use the
        criteria's corresponding value, `v`, to see if the resource's corresponding value
        matches. if `v` is `None`, we assume a match. Otherwise, `v` is called with the
        resource's corresponding value and if `True` is returned, then the value
        matches. Finally,  Also, resources are ignored if `self._ignore(resource)` returns `True`.
        
        Args:
            - criteria (dict[str,Callable[[Any],bool]]): A non-empty dictionary of 
              key-value pairs for finding matches. See the method comments for 
              description  of the value in `criteria`.
            - sort_by_key (str): If not empty, then sort the list by the resource 
              values that correspond to key `sort_by_key`. If this key doesn't exist
              in all the resources, then the resulting `KeyError` will be logged and
              the unsorted list will be returned.
            
        Returns:
            list[dict[str,Any]] with resources that match the criteria, or [] if no matches are found.
        """
        found = []
        for resource in self.resources.values():
            if self._ignore(resource):
                continue
            for key, matcher in criteria.items():
                if matcher and not matcher(resource[key]):
                    continue
            # If here, we have a match!
            found.append(resource)
        
        if sort_by_key:
            try:
                found.sort(key = lambda res: res[sort_by_key])
            except KeyError as ke:
                self.logger.error(f"KeyError thrown '{ke}'' for missing sort_by_key value, '{sort_by_key}' in found resources: {found}")

        return found

    def get_resource_ids_by_criteria(self, criteria: dict[str,Any]) -> list[str]:
        """
        Calls `get_resources_by_criteria` to get resources for the specified criteria,
        i.e., where keys in `criteria` are found in the resources and the values found
        match the corresponding `criteria` value. For the found resources, just the ids
        are returned.
        
        Args:
            criteria (dict[str,Any]): A non-empty dictionary of key-value pairs for finding matches
            
        Returns:
            list[str] with IDs for the resources that match the criteria, or [] if no matches are found.
        """
        found = self.get_resources_by_criteria(criteria)
        return [resource['id'] for resource in found]
