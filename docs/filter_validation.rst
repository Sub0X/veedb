Filter Validation Guide
=======================

The VeeDB library includes a comprehensive filter validation system that helps you validate filters against the VNDB API schema before making requests. This system automatically downloads and caches the schema, validates your filter expressions, and provides helpful suggestions when validation fails.

Key Features
------------

- **Automatic Schema Caching**: Downloads and caches the VNDB API schema locally with TTL support
- **Filter Validation**: Validates filter expressions against available fields for each endpoint
- **Field Suggestions**: Provides suggestions for misspelled or invalid field names
- **Nested Field Support**: Handles complex nested field structures with dot notation
- **Endpoint Discovery**: Lists all available API endpoints and their fields
- **Integration**: Seamlessly integrated into both the main VNDB client and individual endpoint clients

Basic Usage
-----------

The validation system is automatically integrated into the VNDB client:

.. code-block:: python

   import asyncio
   from veedb import VNDB, QueryRequest

   async def main():
       async with VNDB() as client:
           # Enable validation (enabled by default)
           client.enable_validation = True
           
           try:
               # This will validate the filter before sending
               query = QueryRequest(
                   filters=["title", "~", "Fate"],
                   fields="id, title, rating"
               )
               response = await client.vn.query(query)
               print(f"Found {len(response.results)} visual novels")
               
           except Exception as e:
               print(f"Validation error: {e}")

   asyncio.run(main())

Direct Validation
-----------------

You can also use the validation system directly:

.. code-block:: python

   from veedb import FilterValidator, SchemaCache

   async def validate_filters():
       # Create validator
       validator = FilterValidator(SchemaCache())
       
       # Validate a filter
       result = await validator.validate_filters(
           "/vn", 
           ["title", "=", "Test"]
       )
       
       if result['valid']:
           print("Filter is valid!")
       else:
           print(f"Errors: {result['errors']}")
           print(f"Suggestions: {result['suggestions']}")

Field Discovery
---------------

Discover available fields for any endpoint:

.. code-block:: python

   async def discover_fields():
       async with VNDB() as client:
           # Get all available fields for the VN endpoint
           fields = await client.get_available_fields("/vn")
           print("Available VN fields:")
           for field in sorted(fields):
               print(f"  - {field}")
           
           # Get fields with pattern matching
           title_fields = [f for f in fields if "title" in f.lower()]
           print(f"Title-related fields: {title_fields}")

Nested Field Validation
-----------------------

The validator supports complex nested field structures:

.. code-block:: python

   async def nested_fields_example():
       async with VNDB() as client:
           try:
               # Valid nested field
               query = QueryRequest(
                   filters=["developers.name", "=", "Key"],
                   fields="id, title, developers.name"
               )
               response = await client.vn.query(query)
               
           except Exception as e:
               print(f"Error: {e}")

Error Handling and Suggestions
------------------------------

The validator provides helpful error messages and suggestions:

.. code-block:: python

   from veedb.exceptions import FilterValidationError

   async def handle_validation_errors():
       async with VNDB() as client:
           try:
               # Intentionally use an invalid field
               query = QueryRequest(
                   filters=["titel", "=", "Test"],  # Misspelled "title"
                   fields="id, titel"
               )
               response = await client.vn.query(query)
               
           except FilterValidationError as e:
               print(f"Validation failed: {e}")
               print(f"Suggestions: {e.suggestions}")
               # Output might include: "Did you mean 'title'?"

Performance Considerations
--------------------------

Schema Caching
~~~~~~~~~~~~~~

The validation system caches the API schema to improve performance:

.. code-block:: python

   from veedb import SchemaCache

   # Configure cache settings
   cache = SchemaCache(
       cache_dir="./vndb_cache",
       cache_ttl=3600  # 1 hour
   )
   
   # The cache is automatically used by the validator

Disabling Validation
~~~~~~~~~~~~~~~~~~~~

For production environments where performance is critical, you can disable validation:

.. code-block:: python

   async with VNDB() as client:
       # Disable validation for better performance
       client.enable_validation = False
       
       # Queries will skip validation
       response = await client.vn.query(query)

Advanced Usage
--------------

Custom Validation Logic
~~~~~~~~~~~~~~~~~~~~~~~

You can extend the validation system for custom use cases:

.. code-block:: python

   from veedb import FilterValidator

   class CustomValidator(FilterValidator):
       async def validate_filters(self, endpoint, filters, client=None):
           # Call parent validation
           result = await super().validate_filters(endpoint, filters, client)
           
           # Add custom validation logic
           if result['valid']:
               # Additional custom checks
               custom_result = self._custom_validation(filters)
               if not custom_result['valid']:
                   result['valid'] = False
                   result['errors'].extend(custom_result['errors'])
           
           return result
       
       def _custom_validation(self, filters):
           # Your custom validation logic here
           return {'valid': True, 'errors': []}

Building Validation Tools
~~~~~~~~~~~~~~~~~~~~~~~~~

Create tools that help users build valid queries:

.. code-block:: python

   async def build_query_builder():
       """Interactive query builder with validation."""
       async with VNDB() as client:
           endpoint = "/vn"
           fields = await client.get_available_fields(endpoint)
           
           print("Available fields:")
           for i, field in enumerate(sorted(fields), 1):
               print(f"{i:2d}. {field}")
           
           # Let user build filters interactively
           filters = []
           while True:
               field = input("Enter field name (or 'done'): ")
               if field == 'done':
                   break
                   
               if field not in fields:
                   suggestions = [f for f in fields if field.lower() in f.lower()]
                   print(f"Invalid field. Suggestions: {suggestions[:5]}")
                   continue
               
               operator = input("Enter operator (=, !=, >, <, ~): ")
               value = input("Enter value: ")
               
               filters.extend([field, operator, value])
               
               # Validate current filters
               validator = FilterValidator()
               result = await validator.validate_filters(endpoint, filters)
               
               if result['valid']:
                   print("✓ Filter is valid")
               else:
                   print(f"✗ Validation errors: {result['errors']}")
           
           return filters

This validation system ensures your queries are correct before they reach the API, saving time and providing a better development experience.
