import asyncio
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from difflib import get_close_matches
import aiohttp

from .exceptions import InvalidRequestError, VNDBAPIError

# Forward declaration for type hinting
if "VNDB" not in globals():
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .client import VNDB

class SchemaCache:
    """
    Manages the download, caching, and retrieval of the VNDB API schema.
    """
    def __init__(self, cache_dir: str = ".veedb_cache", cache_filename: str = "schema.json", ttl_hours: float = 24.0, local_schema_path: Optional[str] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / cache_filename
        self.ttl_seconds = ttl_hours * 3600
        self._schema_data: Optional[Dict[str, Any]] = None
        self.local_schema_path = Path(local_schema_path) if local_schema_path else None

    def is_cached(self) -> bool:
        """Check if the schema file exists in the cache or if a local path is provided."""
        if self.local_schema_path and self.local_schema_path.is_file():
            return True
        return self.cache_file.is_file()

    def get_cache_age(self) -> float:
        """Get the age of the cache file in seconds. Returns 0 if using local_schema_path."""
        if self.local_schema_path and self.local_schema_path.is_file():
            # Treat local schema as always up-to-date unless explicitly updated
            return 0.0
        if not self.cache_file.is_file(): # Changed from self.is_cached() to self.cache_file.is_file()
            return float('inf')
        return time.time() - self.cache_file.stat().st_mtime

    def is_cache_expired(self) -> bool:
        """Check if the cached schema has expired. Local schema path is never considered expired by this check."""
        if self.local_schema_path and self.local_schema_path.is_file():
            return False # Local schema is not subject to TTL expiration, only manual updates
        return self.get_cache_age() > self.ttl_seconds

    def save_schema(self, schema_data: Dict[str, Any], to_local_path: bool = False):
        """Save the schema data to the cache file or the specified local_schema_path."""
        target_path = self.local_schema_path if to_local_path and self.local_schema_path else self.cache_file
        if not target_path:
            # This case should ideally not be hit if logic is correct, but as a fallback:
            target_path = self.cache_file
        
        target_dir = target_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2)
        self._schema_data = schema_data # Update in-memory cache as well

    def load_schema(self) -> Optional[Dict[str, Any]]:
        """Load the schema data from the local_schema_path (if provided) or the cache file."""
        if self.local_schema_path and self.local_schema_path.is_file():
            try:
                with open(self.local_schema_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                # If local schema fails to load, fall back to cache or download
                pass 
        
        if self.cache_file.is_file(): # Changed from self.is_cached()
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def invalidate_cache(self):
        """Remove the cache file. Does not remove user-provided local_schema_path."""
        self._schema_data = None
        try:
            if self.cache_file.exists():
                os.remove(self.cache_file)
        except FileNotFoundError:
            pass

    async def get_schema(self, client: 'VNDB', force_download: bool = False) -> Dict[str, Any]:
        """
        Get the schema. Prioritizes local_schema_path, then cache, then download.
        If force_download is True, it will download and update the primary schema location.
        """
        if force_download:
            schema = await self._download_schema(client)
            # Save to local_schema_path if it's configured, otherwise to default cache file
            self.save_schema(schema, to_local_path=bool(self.local_schema_path))
            return schema
        
        if self._schema_data and not self.is_cache_expired() and not (self.local_schema_path and self.local_schema_path.is_file()):
            # Use in-memory if not expired AND not primarily using a local file (which would be loaded directly)
            return self._schema_data
            
        loaded_schema = self.load_schema() # Tries local_schema_path first, then cache_file
        if loaded_schema and not self.is_cache_expired(): # is_cache_expired is aware of local_schema_path
            self._schema_data = loaded_schema
            return loaded_schema

        # If local schema was specified but not found or failed to load, or cache expired/not found
        schema = await self._download_schema(client)
        # Save to local_schema_path if it's configured, otherwise to default cache file
        self.save_schema(schema, to_local_path=bool(self.local_schema_path))
        return schema

    async def update_local_schema_from_api(self, client: 'VNDB') -> Dict[str, Any]:
        """Forces a download of the schema and saves it to local_schema_path if configured, else to cache."""
        if not self.local_schema_path:
            # If no specific local path, update the default cache file.
            # Or, one might choose to raise an error if this method is called without a local_schema_path configured.
            # For now, let's assume it updates the primary schema location (local if set, else cache).
            pass # Fall through to get_schema with force_download
        return await self.get_schema(client, force_download=True)

    async def _download_schema(self, client: 'VNDB') -> Dict[str, Any]:
        """Fetch the schema from the VNDB API."""
        try:
            return await client.get_schema()
        except VNDBAPIError as e:
            # If download fails but a stale cache exists, use it as a fallback
            if self.is_cached():
                schema = self.load_schema()
                if schema:
                    return schema
            raise e # Re-raise if there's no cache at all

class FilterValidator:
    """
    Validates filter expressions against the VNDB API schema.
    """
    def __init__(self, schema_cache: Optional[SchemaCache] = None, local_schema_path: Optional[str] = None):
        self.schema_cache = schema_cache or SchemaCache(local_schema_path=local_schema_path)
        self._field_cache: Dict[str, List[str]] = {}

    def _extract_fields(self, schema: Dict[str, Any], endpoint: str) -> List[str]:
        """Recursively extract all valid field names for an endpoint, including nested ones."""
        if endpoint in self._field_cache:
            return self._field_cache[endpoint]

        all_fields: Set[str] = set()
        
        def recurse(obj: Dict[str, Any], prefix: str, full_schema: Dict[str, Any], visited_endpoints: Set[str]):
            if "_inherit" in obj:
                inherited_endpoint = obj["_inherit"]
                if inherited_endpoint in visited_endpoints:
                    return  # Break recursion
                
                if inherited_endpoint in full_schema["api_fields"]:
                    new_visited = visited_endpoints | {inherited_endpoint}
                    recurse(full_schema["api_fields"][inherited_endpoint], prefix, full_schema, new_visited)

            for key, value in obj.items():
                if key == "_inherit":
                    continue
                
                new_prefix = f"{prefix}.{key}" if prefix else key
                all_fields.add(new_prefix)

                if isinstance(value, dict):
                    # Pass the original visited_endpoints set for parallel branches
                    recurse(value, new_prefix, full_schema, visited_endpoints)

        api_fields = schema.get("api_fields", {})
        if endpoint in api_fields:
            initial_visited = {endpoint}
            recurse(api_fields[endpoint], "", schema, initial_visited)

        field_list = sorted(list(all_fields))
        self._field_cache[endpoint] = field_list
        return field_list

    def suggest_fields(self, field: str, available_fields: List[str]) -> List[str]:
        """Suggest corrections for a misspelled field name."""
        return get_close_matches(field, available_fields, n=3, cutoff=0.7)

    async def get_available_fields(self, endpoint: str, client: 'VNDB') -> List[str]:
        """Get all available filterable fields for a given endpoint."""
        schema = await self.schema_cache.get_schema(client) # Removed force_download=False, get_schema handles logic
        return self._extract_fields(schema, endpoint)

    async def list_endpoints(self, client: 'VNDB') -> List[str]:
        """List all available API endpoints from the schema."""
        schema = await self.schema_cache.get_schema(client) # Removed force_download=False
        return sorted(list(schema.get("api_fields", {}).keys()))
        
    async def validate_filters(self, endpoint: str, filters: Union[List, str, None], client: 'VNDB') -> Dict[str, Any]:
        """
        Validate a filter expression for a given endpoint.

        Returns:
            A dictionary containing the validation result.
        """
        if not filters:
            return {'valid': True, 'errors': [], 'suggestions': [], 'available_fields': []}
            
        available_fields = await self.get_available_fields(endpoint, client)
        errors: List[str] = []
        suggestions: Set[str] = set()

        def _validate_recursive(current_filter):
            if not isinstance(current_filter, list) or len(current_filter) < 1:
                errors.append(f"Invalid filter format: {current_filter}")
                return

            operator = current_filter[0].lower()

            if operator in ["and", "or"]:
                if len(current_filter) < 3:
                    errors.append(f"'{operator}' filter requires at least two sub-filters.")
                for sub_filter in current_filter[1:]:
                    _validate_recursive(sub_filter)
            else: # Assumes a simple predicate like ["field", "op", "value"]
                if len(current_filter) != 3:
                    errors.append(f"Simple filter predicate must have 3 elements: [field, operator, value]. Found: {current_filter}")
                    return

                field_name = current_filter[0]
                if field_name not in available_fields:
                    errors.append(f"Invalid field '{field_name}' for endpoint '{endpoint}'.")
                    field_suggestions = self.suggest_fields(field_name, available_fields)
                    if field_suggestions:
                        suggestions.update(field_suggestions)

        _validate_recursive(filters)

        return {
            'valid': not errors,
            'errors': errors,
            'suggestions': sorted(list(suggestions)),
            'available_fields': available_fields
        }