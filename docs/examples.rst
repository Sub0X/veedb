Examples
========

This section contains comprehensive examples demonstrating various VeeDB features and use cases.

Basic Queries
-------------

Simple Visual Novel Search
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from veedb import VNDB, QueryRequest

   async def search_visual_novels():
       async with VNDB() as client:
           # Search for visual novels with "fate" in the title
           query = QueryRequest(
               filters=["title", "~", "fate"],
               fields="id, title, rating, released, description",
               sort="rating",
               reverse=True,  # Highest rated first
               results=10
           )
           
           response = await client.vn.query(query)
           
           print(f"Found {len(response.results)} visual novels:")
           for vn in response.results:
               print(f"  {vn.title} ({vn.released})")
               print(f"    Rating: {vn.rating}")
               if vn.description:
                   print(f"    {vn.description[:100]}...")
               print()

   asyncio.run(search_visual_novels())

Character Search
~~~~~~~~~~~~~~~~

.. code-block:: python

   async def search_characters():
       async with VNDB() as client:
           query = QueryRequest(
               filters=["name", "~", "saber"],
               fields="name, original, description, vns{title, id}",
               results=5
           )
           
           response = await client.character.query(query)
           
           for char in response.results:
               print(f"Character: {char.name}")
               if char.original:
                   print(f"  Original: {char.original}")
               if char.vns:
                   print(f"  Appears in: {[vn.title for vn in char.vns]}")
               print()

Release Information
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def get_release_info():
       async with VNDB() as client:
           query = QueryRequest(
               filters=["vn", "=", ["v17"]],  # Ever17 releases
               fields="title, released, platforms, languages, vn{title}"
           )
           
           response = await client.release.query(query)
           
           for release in response.results:
               print(f"Release: {release.title}")
               print(f"  VN: {release.vn.title if release.vn else 'Unknown'}")
               print(f"  Released: {release.released}")
               print(f"  Platforms: {release.platforms}")
               print(f"  Languages: {release.languages}")
               print()

Advanced Filtering
------------------

Complex Filter Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def complex_filtering():
       async with VNDB() as client:
           # Find highly-rated recent visual novels
           complex_filter = [
               "and",
               ["rating", ">", 8.0],
               ["released", ">", "2020-01-01"],
               ["or",
                   ["tags", "=", ["g1092"]],  # Romance tag
                   ["tags", "=", ["g1093"]]   # Drama tag
               ]
           ]
           
           query = QueryRequest(
               filters=complex_filter,
               fields="title, rating, released, tags{name}",
               sort="rating",
               reverse=True,
               results=15
           )
           
           response = await client.vn.query(query)
           
           print("Highly-rated recent VNs with Romance or Drama:")
           for vn in response.results:
               tag_names = [tag.name for tag in vn.tags] if vn.tags else []
               print(f"  {vn.title} ({vn.released}) - {vn.rating}")
               print(f"    Tags: {', '.join(tag_names[:5])}")

Nested Field Queries
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def nested_field_example():
       async with VNDB() as client:
           # Query VNs with detailed developer information
           query = QueryRequest(
               filters=["developers.name", "~", "type-moon"],
               fields="""
                   title, rating, 
                   developers{name, original, type},
                   image{url}
               """,
               results=10
           )
           
           response = await client.vn.query(query)
           
           for vn in response.results:
               print(f"VN: {vn.title} (Rating: {vn.rating})")
               if vn.developers:
                   for dev in vn.developers:
                       print(f"  Developer: {dev.name} ({dev.type})")
               if vn.image:
                   print(f"  Image: {vn.image.url}")
               print()

Filter Validation
-----------------

Validating Filters Before Use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def filter_validation_example():
       async with VNDB() as client:
           # Test various filters
           test_filters = [
               ["title", "=", "Test"],           # Valid
               ["titl", "=", "Test"],            # Invalid - typo
               ["rating", ">", 8.0],             # Valid
               ["tags.nam", "=", "Romance"],     # Invalid - typo in nested field
               ["developers.name", "~", "Key"]   # Valid
           ]
           
           for filter_expr in test_filters:
               result = await client.validate_filters("/vn", filter_expr)
               
               if result['valid']:
                   print(f"✓ Valid: {filter_expr}")
               else:
                   print(f"✗ Invalid: {filter_expr}")
                   print(f"  Errors: {result['errors']}")
                   if result['suggestions']:
                       print(f"  Suggestions: {result['suggestions']}")
               print()

Getting Available Fields
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def available_fields_example():
       async with VNDB() as client:
           # Get available fields for different endpoints
           endpoints = ["/vn", "/character", "/release", "/producer"]
           
           for endpoint in endpoints:
               fields = await client.get_available_fields(endpoint)
               print(f"Available fields for {endpoint}:")
               
               # Group fields by type (nested vs simple)
               simple_fields = [f for f in fields if '.' not in f]
               nested_fields = [f for f in fields if '.' in f]
               
               print(f"  Simple fields ({len(simple_fields)}): {simple_fields[:10]}")
               if nested_fields:
                   print(f"  Nested fields ({len(nested_fields)}): {nested_fields[:10]}")
               print()

Auto-correction Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def auto_correction_example():
       async with VNDB() as client:
           # Function to auto-correct filters
           async def correct_and_query(endpoint, filters, fields):
               result = await client.validate_filters(endpoint, filters)
               
               if not result['valid'] and result['suggestions']:
                   print(f"Original filter had errors: {result['errors']}")
                   print(f"Trying suggestion: {result['suggestions'][0]}")
                   
                   # Try with the first suggestion
                   corrected_filter = filters.copy()
                   corrected_filter[0] = result['suggestions'][0]
                   
                   # Validate again
                   corrected_result = await client.validate_filters(endpoint, corrected_filter)
                   if corrected_result['valid']:
                       # Use corrected filter
                       query = QueryRequest(filters=corrected_filter, fields=fields)
                       return await client.vn.query(query)
               
               elif result['valid']:
                   query = QueryRequest(filters=filters, fields=fields)
                   return await client.vn.query(query)
               
               return None
           
           # Test with typo
           response = await correct_and_query(
               "/vn", 
               ["titl", "~", "fate"],  # "titl" should be "title"
               "title, rating"
           )
           
           if response:
               print("Query successful after correction:")
               for vn in response.results[:3]:
                   print(f"  {vn.title}: {vn.rating}")

Authentication Examples
-----------------------

User List Management
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from veedb import VNDB, QueryRequest, UlistUpdatePayload

   async def user_list_example():
       api_token = os.environ.get("VNDB_API_TOKEN")
       if not api_token:
           print("Please set VNDB_API_TOKEN environment variable")
           return
       
       async with VNDB(api_token=api_token) as client:
           # Get user info
           auth_info = await client.get_authinfo()
           print(f"Managing lists for user: {auth_info.username}")
           
           # Get user's current VN list
           query = QueryRequest(
               filters=["uid", "=", auth_info.id],
               fields="id, vote, notes, vn{title, rating}",
               results=50
           )
           
           response = await client.ulist.query(query)
           print(f"Found {len(response.results)} VNs in your list:")
           
           for item in response.results[:5]:
               print(f"  {item.vn.title if item.vn else 'Unknown'}")
               print(f"    Your vote: {item.vote}")
               print(f"    Notes: {item.notes or 'No notes'}")
           
           # Add a new VN to list (example)
           # payload = UlistUpdatePayload(
           #     id="v17",
           #     vote=85,
           #     notes="Classic sci-fi visual novel"
           # )
           # await client.ulist.update("v17", payload)
           # print("Added Ever17 to your list!")

Release List Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import RlistUpdatePayload

   async def release_list_example():
       api_token = os.environ.get("VNDB_API_TOKEN")
       
       async with VNDB(api_token=api_token) as client:
           auth_info = await client.get_authinfo()
           
           # Get user's release list
           query = QueryRequest(
               filters=["uid", "=", auth_info.id],
               fields="id, status, release{title, released}"
           )
           
           response = await client.rlist.query(query)
           
           # Group by status
           by_status = {}
           for item in response.results:
               status = item.status or "unknown"
               if status not in by_status:
                   by_status[status] = []
               by_status[status].append(item)
           
           for status, items in by_status.items():
               print(f"{status.title()} ({len(items)} items):")
               for item in items[:3]:
                   release_title = item.release.title if item.release else "Unknown"
                   print(f"  {release_title}")

Error Handling Examples
-----------------------

Comprehensive Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb.exceptions import *

   async def robust_query_example():
       async with VNDB() as client:
           try:
               # This might fail for various reasons
               query = QueryRequest(
                   filters=["invalid_field", "=", "test"],
                   fields="nonexistent_field"
               )
               
               response = await client.vn.query(query)
               
           except InvalidRequestError as e:
               print(f"Invalid request: {e}")
               print("Check your filter syntax and field names")
               
               # Try to get suggestions
               result = await client.validate_filters("/vn", ["invalid_field", "=", "test"])
               if result['suggestions']:
                   print(f"Did you mean: {result['suggestions']}")
           
           except RateLimitError:
               print("Rate limit exceeded - implementing backoff")
               await asyncio.sleep(60)  # Wait before retry
               
           except NotFoundError:
               print("Requested resource not found")
               
           except ServerError as e:
               print(f"Server error: {e}")
               print("Try again later")
               
           except VNDBAPIError as e:
               print(f"General API error: {e}")

Retry Logic Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import random

   async def query_with_retry(client, query, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await client.vn.query(query)
               
           except RateLimitError:
               if attempt < max_retries - 1:
                   # Exponential backoff with jitter
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   print(f"Rate limited, waiting {wait_time:.2f}s before retry {attempt + 1}")
                   await asyncio.sleep(wait_time)
               else:
                   raise
                   
           except ServerError:
               if attempt < max_retries - 1:
                   wait_time = 5 + random.uniform(0, 5)
                   print(f"Server error, waiting {wait_time:.2f}s before retry {attempt + 1}")
                   await asyncio.sleep(wait_time)
               else:
                   raise

Performance Examples
--------------------

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   async def batch_processing_example():
       async with VNDB() as client:
           # Get a list of VN IDs to process
           id_query = QueryRequest(
               filters=["rating", ">", 8.5],
               fields="id",
               results=100
           )
           
           response = await client.vn.query(id_query)
           vn_ids = [vn.id for vn in response.results]
           
           # Process in batches to avoid overwhelming the API
           batch_size = 10
           detailed_vns = []
           
           for i in range(0, len(vn_ids), batch_size):
               batch_ids = vn_ids[i:i + batch_size]
               
               # Query details for this batch
               detail_query = QueryRequest(
                   filters=["id", "=", batch_ids],
                   fields="id, title, rating, description, tags{name}"
               )
               
               batch_response = await client.vn.query(detail_query)
               detailed_vns.extend(batch_response.results)
               
               # Small delay between batches to be respectful
               await asyncio.sleep(0.5)
           
           print(f"Processed {len(detailed_vns)} VNs in batches")

Caching Results
~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from pathlib import Path

   class VNCache:
       def __init__(self, cache_file="vn_cache.json"):
           self.cache_file = Path(cache_file)
           self.cache = self.load_cache()
       
       def load_cache(self):
           if self.cache_file.exists():
               with open(self.cache_file) as f:
                   return json.load(f)
           return {}
       
       def save_cache(self):
           with open(self.cache_file, 'w') as f:
               json.dump(self.cache, f, indent=2)
       
       async def get_vn_details(self, client, vn_id):
           if vn_id in self.cache:
               print(f"Cache hit for {vn_id}")
               return self.cache[vn_id]
           
           print(f"Cache miss for {vn_id}, fetching from API")
           query = QueryRequest(
               filters=["id", "=", vn_id],
               fields="id, title, rating, description"
           )
           
           response = await client.vn.query(query)
           if response.results:
               vn_data = {
                   "title": response.results[0].title,
                   "rating": response.results[0].rating,
                   "description": response.results[0].description
               }
               self.cache[vn_id] = vn_data
               self.save_cache()
               return vn_data
           
           return None

   async def caching_example():
       cache = VNCache()
       
       async with VNDB() as client:
           # This will fetch from API first time, cache subsequent times
           vn_details = await cache.get_vn_details(client, "v17")
           print(f"VN: {vn_details['title']}")

Configuration Examples
----------------------

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def custom_config_example():
       # Custom cache configuration
       async with VNDB(
           schema_cache_dir="./my_cache",
           schema_cache_ttl_hours=6.0,  # Refresh every 6 hours
           local_schema_path="./schemas/vndb_schema.json"
       ) as client:
           
           # Check cache status
           print(f"Schema cached: {client._schema_cache_instance.is_cached()}")
           print(f"Cache expired: {client._schema_cache_instance.is_cache_expired()}")
           
           # Force schema update if needed
           if client._schema_cache_instance.is_cache_expired():
               print("Updating schema cache...")
               await client.update_local_schema()

Running the Examples
--------------------

To run these examples:

1. **Install VeeDB**: ``pip install veedb``
2. **Set API Token** (for auth examples): 

   .. code-block:: bash
   
      $env:VNDB_API_TOKEN = "your-token-here"

3. **Save examples** to Python files and run:

   .. code-block:: bash
   
      python example_name.py

4. **Check the results** and modify as needed for your use case.

Each example is self-contained and can be run independently. They demonstrate different aspects of the VeeDB library and can serve as starting points for your own applications.
