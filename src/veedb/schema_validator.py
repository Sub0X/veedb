import asyncio
import orjson # Added for faster JSON processing
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from difflib import get_close_matches
import aiohttp

from .exceptions import InvalidRequestError, VNDBAPIError
from .methods.fetch import _fetch_api # Ensure this import is present

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
        # Use string paths initially to avoid any Path recursion issues
        self._cache_dir_str = str(cache_dir) if cache_dir else ".veedb_cache"
        self._cache_filename_str = str(cache_filename) if cache_filename else "schema.json"
        self._local_schema_path_str = str(local_schema_path) if local_schema_path else None
        
        # Create Path objects only when needed and with error handling
        self._cache_dir = None
        self._cache_file = None
        self._local_schema_path = None
        
        self.ttl_seconds = ttl_hours * 3600
        self._schema_data: Optional[Dict[str, Any]] = None

    @property
    def cache_dir(self) -> Path:
        """Safely get the cache directory Path object."""
        if self._cache_dir is None:
            try:
                self._cache_dir = Path(self._cache_dir_str)
            except Exception:
                self._cache_dir = Path(".veedb_cache")
        return self._cache_dir
    
    @property
    def cache_file(self) -> Path:
        """Safely get the cache file Path object."""
        if self._cache_file is None:
            try:
                self._cache_file = self.cache_dir / self._cache_filename_str
            except Exception:
                self._cache_file = Path(".veedb_cache") / "schema.json"
        return self._cache_file
    
    @property
    def local_schema_path(self) -> Optional[Path]:
        """Safely get the local schema path Path object."""
        if self._local_schema_path is None and self._local_schema_path_str:
            try:
                self._local_schema_path = Path(self._local_schema_path_str)
            except Exception:
                self._local_schema_path = None
        return self._local_schema_path

    def is_cached(self) -> bool:
        """Check if the schema file exists in the cache or if a local path is provided."""
        if self._local_schema_path_str:
            try:
                # Use os.path.isfile instead of Path.is_file() to avoid recursion
                return os.path.isfile(self._local_schema_path_str)
            except (RecursionError, OSError, Exception):
                pass
        
        try:
            # Use os.path.exists instead of Path.exists() to avoid recursion
            cache_path = os.path.join(self._cache_dir_str, self._cache_filename_str)
            return os.path.exists(cache_path)
        except (RecursionError, OSError, Exception):
            return False

    def get_cache_age(self) -> float:
        """Get the age of the cache file in seconds. Returns 0 if using local_schema_path."""
        if self._local_schema_path_str:
            try:
                # Use os.path.isfile instead of Path methods to avoid recursion
                if os.path.isfile(self._local_schema_path_str):
                    # Treat local schema as always up-to-date unless explicitly updated
                    return 0.0
            except (RecursionError, OSError, Exception):
                pass
        
        try:
            cache_path = os.path.join(self._cache_dir_str, self._cache_filename_str)
            if not os.path.exists(cache_path):
                return float('inf')
            return time.time() - os.path.getmtime(cache_path)
        except (RecursionError, OSError, Exception):
            return float('inf')

    def is_cache_expired(self) -> bool:
        """Check if the cached schema has expired. Local schema path is never considered expired by this check."""
        if self._local_schema_path_str and os.path.isfile(self._local_schema_path_str):
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
        
        # Use orjson for writing
        with open(target_path, 'wb') as f: # Open in binary mode for orjson
            f.write(orjson.dumps(schema_data, option=orjson.OPT_INDENT_2))
        self._schema_data = schema_data # Update in-memory cache as well
        
    def load_schema(self) -> Optional[Dict[str, Any]]:
        """Load the schema data from the local_schema_path (if provided) or the cache file."""
        if self._local_schema_path_str and os.path.isfile(self._local_schema_path_str):
            try:
                # Use orjson for reading
                with open(self._local_schema_path_str, 'rb') as f: # Open in binary mode for orjson
                    return orjson.loads(f.read())
            except Exception:
                # If local schema fails to load, fall back to cache or download
                pass 
        
        # Use os.path instead of Path methods to avoid recursion issues
        try:
            cache_path_str = os.path.join(self._cache_dir_str, self._cache_filename_str)
            cache_file_exists = os.path.isfile(cache_path_str) # Changed from os.path.exists to os.path.isfile
        except (RecursionError, OSError, Exception):
            # If there's any issue with the cache_file path, return None
            return None
            
        if cache_file_exists:
            try:
                # Use orjson for reading
                with open(cache_path_str, 'rb') as f: # Open in binary mode for orjson
                    return orjson.loads(f.read())
            except Exception:
                pass
        return None

    def invalidate_cache(self):
        """Remove the cache file. Does not remove user-provided local_schema_path."""
        self._schema_data = None
        try:
            cache_path = os.path.join(self._cache_dir_str, self._cache_filename_str)
            if os.path.exists(cache_path):
                os.remove(cache_path)
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
        """Fetch the schema from the VNDB API directly."""
        try:
            # Call the API directly to avoid recursion - do NOT call client.get_schema()
            url = f"{client.base_url}/schema"
            session = client._get_session()
            
            # Use the imported _fetch_api
            # The schema endpoint typically does not require a token.
            response_data = await _fetch_api(
                session=session,
                method="GET",
                url=url,
                token=None # Explicitly None for public schema endpoint
            )
            if not isinstance(response_data, dict):
                raise VNDBAPIError(f"Schema download did not return a valid JSON object. Received type: {type(response_data)}")
            return response_data
        except aiohttp.ClientError as e:
            raise VNDBAPIError(f"Failed to download schema due to network/HTTP error: {e}") from e
        except Exception as e:
            # Catch other potential errors during the fetch or processing
            raise VNDBAPIError(f"An unexpected error occurred while downloading schema: {e}") from e

    async def update_local_schema_from_api(self, client: 'VNDB') -> Dict[str, Any]:
        """Forces a download of the schema and saves it to local_schema_path if configured, else to cache."""
        if not self.local_schema_path:
            # If no specific local path, update the default cache file.
            # Or, one might choose to raise an error if this method is called without a local_schema_path configured.
            # For now, let's assume it updates the primary schema location (local if set, else cache).
            pass # Fall through to get_schema with force_download
        return await self.get_schema(client, force_download=True)

    async def _download_schema(self, client: 'VNDB') -> Dict[str, Any]:
        """Fetch the schema from the VNDB API directly."""
        try:
            # Call the API directly to avoid recursion - do NOT call client.get_schema()
            url = f"{client.base_url}/schema"
            session = client._get_session()
            
            # Use the imported _fetch_api
            # The schema endpoint typically does not require a token.
            response_data = await _fetch_api(
                session=session,
                method="GET",
                url=url,
                token=None # Explicitly None for public schema endpoint
            )
            if not isinstance(response_data, dict):
                raise VNDBAPIError(f"Schema download did not return a valid JSON object. Received type: {type(response_data)}")
            return response_data
        except aiohttp.ClientError as e:
            raise VNDBAPIError(f"Failed to download schema due to network/HTTP error: {e}") from e
        except Exception as e:
            # Catch other potential errors during the fetch or processing
            raise VNDBAPIError(f"An unexpected error occurred while downloading schema: {e}") from e

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