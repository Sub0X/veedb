Quick Start Guide
==================

This guide will help you get started with VeeDB quickly and efficiently.

Basic Setup
-----------

First, import the necessary components:

.. code-block:: python

   import asyncio
   from veedb import VNDB, QueryRequest
   from veedb.exceptions import VNDBAPIError

Simple Example
--------------

Here's a basic example that demonstrates the core functionality:

.. code-block:: python

   import asyncio
   from veedb import VNDB, QueryRequest

   async def main():
       # Create a client instance
       async with VNDB() as client:
           # Get database statistics
           stats = await client.get_stats()
           print(f"Total visual novels: {stats.vn}")
           print(f"Total characters: {stats.chars}")
           
           # Query for visual novels
           query = QueryRequest(
               filters=["title", "~", "Fate"],  # Search for titles containing "Fate"
               fields="id, title, rating, released",  # Fields to retrieve
               results=5  # Limit to 5 results
           )
           
           response = await client.vn.query(query)
           
           for vn in response.results:
               print(f"{vn.title} ({vn.released}): {vn.rating}")

   # Run the async function
   asyncio.run(main())

Authentication
--------------

For authenticated operations (like managing lists), you'll need an API token:

.. code-block:: python

   import os
   from veedb import VNDB

   async def authenticated_example():
       # Get token from environment variable (recommended)
       api_token = os.environ.get("VNDB_API_TOKEN")
       
       async with VNDB(api_token=api_token) as client:
           # Get authentication info
           auth_info = await client.get_authinfo()
           print(f"Logged in as: {auth_info.username}")
           
           # Now you can access authenticated endpoints
           # like user lists, etc.

Getting an API Token
~~~~~~~~~~~~~~~~~~~~

1. Go to https://vndb.org/u/tokens
2. Create a new token with appropriate permissions
3. Store it securely as an environment variable:

.. code-block:: bash

   # Windows PowerShell
   $env:VNDB_API_TOKEN = "your-token-here"
   
   # Or add to your profile permanently
   [Environment]::SetEnvironmentVariable("VNDB_API_TOKEN", "your-token-here", "User")

Using Different Endpoints
-------------------------

VeeDB provides convenient client objects for each endpoint:

.. code-block:: python

   async def endpoint_examples():
       async with VNDB() as client:
           # Visual Novel queries
           vn_response = await client.vn.query(QueryRequest(
               filters=["id", "=", "v17"],
               fields="title, description, rating"
           ))
           
           # Character queries
           char_response = await client.character.query(QueryRequest(
               filters=["name", "~", "Saber"],
               fields="name, description, vns{title}"
           ))
           
           # Release queries
           release_response = await client.release.query(QueryRequest(
               filters=["platforms", "=", ["win"]],
               fields="title, released, platforms"
           ))

Filter Validation
-----------------

VeeDB includes a powerful filter validation system:

.. code-block:: python

   async def validation_example():
       async with VNDB() as client:
           # Validate a filter before using it
           result = await client.validate_filters("/vn", ["title", "=", "Test"])
           
           if result['valid']:
               print("Filter is valid!")
           else:
               print(f"Errors: {result['errors']}")
               print(f"Suggestions: {result['suggestions']}")
           
           # Get available fields for an endpoint
           fields = await client.get_available_fields("/vn")
           print(f"Available VN fields: {fields[:10]}")

Complex Queries
---------------

You can build complex filter expressions:

.. code-block:: python

   async def complex_query_example():
       async with VNDB() as client:
           # Complex filter with AND/OR logic
           complex_filter = [
               "and",
               ["title", "~", "fate"],
               ["or",
                   ["rating", ">", 8.0],
                   ["released", ">", "2010-01-01"]
               ]
           ]
           
           query = QueryRequest(
               filters=complex_filter,
               fields="title, rating, released, description",
               sort="rating",
               reverse=True,
               results=10
           )
           
           response = await client.vn.query(query)
           
           for vn in response.results:
               print(f"{vn.title}: {vn.rating} ({vn.released})")

Error Handling
--------------

Always handle potential API errors:

.. code-block:: python

   from veedb.exceptions import (
       VNDBAPIError, 
       AuthenticationError, 
       RateLimitError,
       NotFoundError
   )

   async def error_handling_example():
       try:
           async with VNDB(api_token="invalid-token") as client:
               await client.get_authinfo()
       
       except AuthenticationError:
           print("Invalid API token")
       except RateLimitError:
           print("Rate limit exceeded - wait before retrying")
       except NotFoundError:
           print("Requested resource not found")
       except VNDBAPIError as e:
           print(f"API error: {e}")

Sandbox Mode
------------

For testing and development, use sandbox mode:

.. code-block:: python

   async def sandbox_example():
       # Use sandbox for testing
       async with VNDB(use_sandbox=True) as client:
           stats = await client.get_stats()
           print(f"Sandbox stats: {stats.vn} VNs")

Configuration Options
---------------------

VeeDB supports various configuration options:

.. code-block:: python

   async def configuration_example():
       async with VNDB(
           api_token="your-token",
           use_sandbox=False,
           schema_cache_dir="./my_cache",
           schema_cache_ttl_hours=12.0,
           local_schema_path="./schema.json"
       ) as client:
           # Your code here
           pass

Best Practices
--------------

1. **Use Context Manager**: Always use ``async with VNDB() as client`` to ensure proper cleanup
2. **Validate Filters**: Use the validation system to catch errors early
3. **Handle Errors**: Implement proper error handling for production code
4. **Limit Results**: Use the ``results`` parameter to avoid overwhelming responses
5. **Cache Schema**: Configure appropriate cache TTL for your use case
6. **Environment Variables**: Store API tokens as environment variables, not in code

Next Steps
----------

- Read the :doc:`filter_validation` guide for advanced filtering
- Check out the :doc:`examples` for more detailed examples
- Browse the :doc:`api/client` for complete API reference
- Learn about :doc:`authentication` for user-specific operations
