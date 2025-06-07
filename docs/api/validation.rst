Validation System
=================

VeeDB includes a comprehensive filter validation system that helps ensure your queries are correct before sending them to the API.

Filter Validator
----------------

.. autoclass:: veedb.FilterValidator
   :members:
   :show-inheritance:
   :no-index:
   
   The main validation class that checks filters against the VNDB API schema.
   
   **Example Usage:**
   
   .. code-block:: python
   
      from veedb import FilterValidator, SchemaCache
      
      # Create validator with custom cache
      validator = FilterValidator(SchemaCache(cache_ttl=3600))
      
      # Validate filters
      result = await validator.validate_filters("/vn", ["title", "=", "Test"], client)
      
      if result['valid']:
          print("Filter is valid!")
      else:
          print(f"Errors: {result['errors']}")
          print(f"Suggestions: {result['suggestions']}")

Schema Cache
------------

.. autoclass:: veedb.SchemaCache
   :members:
   :show-inheritance:
   :no-index:
   
   Manages downloading, caching, and retrieval of the VNDB API schema.
   
   **Configuration:**
   
   .. code-block:: python
   
      from veedb import SchemaCache
      
      # Default configuration
      cache = SchemaCache()
      
      # Custom configuration
      cache = SchemaCache(
          cache_dir="./my_cache",     # Custom cache directory
          cache_ttl=7200,             # 2 hours TTL (in seconds)
          local_schema_path="./schema.json"  # Use local schema file
      )

Validation Methods
------------------

Filter Validation
~~~~~~~~~~~~~~~~~

.. automethod:: veedb.FilterValidator.validate_filters
   :no-index:

   Validates a filter expression against the API schema.
   
   **Parameters:**
   
   - ``endpoint`` (str): API endpoint to validate against (e.g., "/vn", "/character")
   - ``filters`` (Union[List, str, None]): Filter expression to validate
   - ``client`` (VNDB): VNDB client instance for schema access
   
   **Returns:**
   
   - ``Dict[str, Any]``: Validation result containing:
     
     - ``valid`` (bool): Whether the filter is valid
     - ``errors`` (List[str]): List of validation errors
     - ``suggestions`` (List[str]): Suggested corrections for invalid fields
     - ``available_fields`` (List[str]): All available fields for the endpoint
   
   **Example:**
   
   .. code-block:: python
   
      result = await validator.validate_filters("/vn", ["title", "=", "Test"], client)
      
      if not result['valid']:
          for error in result['errors']:
              print(f"Error: {error}")
          
          if result['suggestions']:
              print(f"Suggestions: {', '.join(result['suggestions'])}")

Field Suggestions
~~~~~~~~~~~~~~~~~

.. automethod:: veedb.FilterValidator.suggest_fields
   :no-index:

   Provides suggestions for misspelled or invalid field names.
   
   **Parameters:**
   
   - ``field_name`` (str): The invalid field name
   - ``available_fields`` (List[str]): List of valid field names
   - ``max_suggestions`` (int): Maximum number of suggestions to return (default: 5)
   
   **Returns:**
   
   - ``List[str]``: List of suggested field names
   
   **Example:**
   
   .. code-block:: python
   
      suggestions = validator.suggest_fields("titl", ["title", "original", "aliases"])
      # Returns: ["title"]

Available Fields
~~~~~~~~~~~~~~~~

.. automethod:: veedb.FilterValidator.get_available_fields
   :no-index:

   Get all available fields for an endpoint.
   
   **Parameters:**
   
   - ``endpoint`` (str): API endpoint
   - ``client`` (VNDB): VNDB client instance
   
   **Returns:**
   
   - ``List[str]``: List of available field names including nested fields
   
   **Example:**
   
   .. code-block:: python
   
      fields = await validator.get_available_fields("/vn", client)
      print(f"Available VN fields: {fields}")

Endpoint Discovery
~~~~~~~~~~~~~~~~~~

.. automethod:: veedb.FilterValidator.list_endpoints
   :no-index:

   Get all available API endpoints.
   
   **Parameters:**
   
   - ``client`` (VNDB): VNDB client instance
   
   **Returns:**
   
   - ``List[str]``: List of available endpoints
   
   **Example:**
   
   .. code-block:: python
   
      endpoints = await validator.list_endpoints(client)
      print(f"Available endpoints: {endpoints}")

Schema Cache Methods
--------------------

Cache Status
~~~~~~~~~~~~

.. automethod:: veedb.SchemaCache.is_cached
   :no-index:

   Check if the schema is cached locally.
   
   **Returns:**
   
   - ``bool``: True if schema file exists or local schema path is configured

.. automethod:: veedb.SchemaCache.get_cache_age
   :no-index:

   Get the age of the cached schema in seconds.
   
   **Returns:**
   
   - ``float``: Age in seconds, or 0.0 for local schema, inf if not cached

.. automethod:: veedb.SchemaCache.is_cache_expired
   :no-index:

   Check if the cached schema has expired based on TTL.
   
   **Returns:**
   
   - ``bool``: True if cache has expired (local schemas never expire)

Cache Management
~~~~~~~~~~~~~~~~

.. automethod:: veedb.SchemaCache.invalidate_cache
   :no-index:

   Invalidate the cached schema, forcing a refresh on next access.

.. automethod:: veedb.SchemaCache.save_schema
   :no-index:

   Save schema data to cache or local file.
   
   **Parameters:**
   
   - ``schema_data`` (Dict[str, Any]): Schema data to save
   - ``to_local_path`` (bool): Whether to save to local schema path (default: False)

.. automethod:: veedb.SchemaCache.load_schema
   :no-index:

   Load schema from cache or local file.
   
   **Returns:**
   
   - ``Optional[Dict[str, Any]]``: Loaded schema data or None if not found

.. automethod:: veedb.SchemaCache.get_schema
   :no-index:

   Get schema, downloading if necessary.
   
   **Parameters:**
   
   - ``client`` (VNDB): VNDB client for downloading schema
   
   **Returns:**
   
   - ``Dict[str, Any]``: Schema data

.. automethod:: veedb.SchemaCache.update_local_schema_from_api
   :no-index:

   Force update of schema from API.
   
   **Parameters:**
   
   - ``client`` (VNDB): VNDB client for API access
   
   **Returns:**
   
   - ``Dict[str, Any]``: Updated schema data

Validation Examples
-------------------

Basic Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import VNDB

   async def basic_validation():
       async with VNDB() as client:
           # Validate a simple filter
           result = await client.validate_filters("/vn", ["title", "=", "Fate/stay night"])
           
           if result['valid']:
               print("✓ Filter is valid")
           else:
               print("✗ Filter has errors:")
               for error in result['errors']:
                   print(f"  - {error}")

Complex Filter Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def complex_validation():
       async with VNDB() as client:
           # Complex nested filter
           complex_filter = [
               "and",
               ["title", "~", "fate"],
               ["or",
                   ["rating", ">", 8.0],
                   ["tags.name", "=", "Romance"]
               ]
           ]
           
           result = await client.validate_filters("/vn", complex_filter)
           
           if result['valid']:
               print("✓ Complex filter is valid")
               # Safe to use in query
               query = QueryRequest(filters=complex_filter, fields="title, rating")
               response = await client.vn.query(query)

Auto-Correction
~~~~~~~~~~~~~~~

.. code-block:: python

   async def auto_correction():
       async with VNDB() as client:
           # Filter with typo
           result = await client.validate_filters("/vn", ["titl", "=", "Test"])
           
           if not result['valid'] and result['suggestions']:
               print(f"Invalid field 'titl'")
               print(f"Did you mean: {result['suggestions'][0]}")
               
               # Use suggestion
               corrected_filter = ["title", "=", "Test"]  # Use suggested field
               corrected_result = await client.validate_filters("/vn", corrected_filter)
               
               if corrected_result['valid']:
                   print("✓ Corrected filter is valid")

Field Discovery
~~~~~~~~~~~~~~~

.. code-block:: python

   async def field_discovery():
       async with VNDB() as client:
           # Get all available fields
           fields = await client.get_available_fields("/vn")
           
           # Categorize fields
           simple_fields = [f for f in fields if '.' not in f]
           nested_fields = [f for f in fields if '.' in f]
           
           print(f"Simple fields ({len(simple_fields)}): {simple_fields[:10]}")
           print(f"Nested fields ({len(nested_fields)}): {nested_fields[:10]}")
           
           # Get available endpoints
           endpoints = await client.list_endpoints()
           print(f"Available endpoints: {endpoints}")

Custom Validator Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import FilterValidator, SchemaCache

   async def custom_validator():
       # Create custom cache with 6-hour TTL
       cache = SchemaCache(
           cache_dir="./validation_cache",
           cache_ttl=21600,  # 6 hours in seconds
           local_schema_path="./schemas/vndb.json"
       )
       
       # Create validator with custom cache
       validator = FilterValidator(schema_cache=cache)
       
       async with VNDB() as client:
           # Use custom validator
           result = await validator.validate_filters("/vn", ["title", "=", "Test"], client)
           
           # Check cache status
           print(f"Schema cached: {cache.is_cached()}")
           print(f"Cache age: {cache.get_cache_age():.2f} seconds")
           print(f"Cache expired: {cache.is_cache_expired()}")

Error Types
-----------

The validation system can return various types of errors:

Field Errors
~~~~~~~~~~~~

- **Unknown field**: Field name doesn't exist in the schema
- **Invalid nested field**: Nested field path is incorrect
- **Type mismatch**: Filter value type doesn't match field type

Syntax Errors
~~~~~~~~~~~~~

- **Invalid filter structure**: Malformed filter expression
- **Missing operator**: Filter missing comparison operator
- **Invalid operator**: Unsupported comparison operator for field type

Usage Errors
~~~~~~~~~~~~

- **Endpoint not found**: Invalid endpoint name
- **Permission required**: Field requires authentication

Suggestions Algorithm
---------------------

The suggestion system uses fuzzy string matching to provide helpful corrections:

1. **Exact prefix matches**: Fields starting with the input
2. **Fuzzy matching**: Similar fields using difflib.get_close_matches
3. **Nested field handling**: Suggestions for nested field paths
4. **Ranking**: Results ranked by similarity score

**Example:**

.. code-block:: python

   # Input: "titl"
   # Suggestions: ["title"] (exact match after adding 'e')
   
   # Input: "develper"
   # Suggestions: ["developer", "developers"] (close matches)
   
   # Input: "tags.nam"
   # Suggestions: ["tags.name"] (nested field correction)

Best Practices
--------------

1. **Always Validate**: Validate filters before making API calls
2. **Handle Suggestions**: Implement auto-correction using suggestions
3. **Cache Appropriately**: Use reasonable TTL for your use case
4. **Check Permissions**: Some fields require authentication
5. **Use Nested Fields**: Take advantage of nested field validation

Integration Tips
----------------

**Form Validation**: Use in web forms to validate user input
**Auto-Complete**: Build auto-complete using available fields
**Error Recovery**: Implement graceful error handling with suggestions
**Performance**: Cache validation results for repeated queries
**Testing**: Use validation in tests to ensure query correctness
