Exception Handling
==================

VeeDB provides a comprehensive set of custom exceptions for different error conditions that may occur when interacting with the VNDB API.

Exception Hierarchy
-------------------

All VeeDB exceptions inherit from the base ``VNDBAPIError`` class:

.. code-block:: text

   VNDBAPIError
   ├── AuthenticationError
   ├── RateLimitError  
   ├── InvalidRequestError
   ├── NotFoundError
   ├── ServerError
   └── TooMuchDataSelectedError

Base Exception
--------------

.. autoclass:: veedb.exceptions.VNDBAPIError
   :members:
   :show-inheritance:
   :no-index:
   
   Base exception class for all VNDB API related errors.
   
   **Attributes:**
   
   - ``message`` (str): Error message
   - ``status_code`` (Optional[int]): HTTP status code if applicable
   - ``response_data`` (Optional[dict]): Raw response data from API
   
   **Example:**
   
   .. code-block:: python
   
      try:
          response = await client.vn.query(query)
      except VNDBAPIError as e:
          print(f"API Error: {e}")
          if e.status_code:
              print(f"Status Code: {e.status_code}")

Specific Exceptions
-------------------

Authentication Errors
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.AuthenticationError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when authentication fails or is required but not provided.
   
   **Common Causes:**
   
   - Invalid API token
   - Missing API token for authenticated endpoints
   - Expired API token
   - Insufficient permissions
   
   **Example:**
   
   .. code-block:: python
   
      try:
          auth_info = await client.get_authinfo()
      except AuthenticationError:
          print("Invalid or missing API token")

Rate Limiting Errors
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.RateLimitError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when API rate limits are exceeded.
   
   **Handling Strategy:**
   
   Implement exponential backoff with retry logic.
   
   **Example:**
   
   .. code-block:: python
   
      import asyncio
      import random
      
      async def query_with_retry(client, query, max_retries=3):
          for attempt in range(max_retries):
              try:
                  return await client.vn.query(query)
              except RateLimitError:
                  if attempt < max_retries - 1:
                      wait_time = (2 ** attempt) + random.uniform(0, 1)
                      await asyncio.sleep(wait_time)
                  else:
                      raise

Invalid Request Errors
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.InvalidRequestError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when the request is malformed or contains invalid data.
   
   **Common Causes:**
   
   - Invalid filter syntax
   - Unknown field names
   - Invalid field values
   - Malformed query parameters
   
   **Example:**
   
   .. code-block:: python
   
      try:
          # Invalid field name
          query = QueryRequest(fields="invalid_field")
          response = await client.vn.query(query)
      except InvalidRequestError as e:
          print(f"Invalid request: {e}")
          # Use validation to check filters first
          result = await client.validate_filters("/vn", query.filters)
          if not result['valid']:
              print(f"Validation errors: {result['errors']}")

Not Found Errors
~~~~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.NotFoundError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when a requested resource is not found.
   
   **Common Causes:**
   
   - Invalid entity ID
   - Resource doesn't exist
   - No permission to access resource
   
   **Example:**
   
   .. code-block:: python
   
      try:
          query = QueryRequest(filters=["id", "=", "v999999"])
          response = await client.vn.query(query)
          if not response.results:
              print("VN not found")
      except NotFoundError:
          print("VN with that ID doesn't exist")

Server Errors
~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.ServerError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when the VNDB server encounters an internal error.
   
   **Handling Strategy:**
   
   Retry after a delay, as this is usually temporary.
   
   **Example:**
   
   .. code-block:: python
   
      try:
          response = await client.vn.query(query)
      except ServerError:
          print("Server error - try again later")
          # Implement retry logic with backoff

Too Much Data Errors
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.exceptions.TooMuchDataSelectedError
   :members:
   :show-inheritance:
   :no-index:
   
   Raised when a query selects too much data and exceeds API limits.
   
   **Solutions:**
   
   - Reduce the number of fields requested
   - Add more restrictive filters
   - Use pagination with smaller page sizes
   - Request fewer results
   
   **Example:**
   
   .. code-block:: python
   
      try:
          # Query requesting too many fields for too many results
          query = QueryRequest(
              fields="id, title, description, image, developers, tags, traits",
              results=1000
          )
          response = await client.vn.query(query)
      except TooMuchDataSelectedError:
          print("Query selects too much data")
          # Reduce fields or results
          smaller_query = QueryRequest(
              fields="id, title",
              results=100
          )
          response = await client.vn.query(smaller_query)

Error Handling Patterns
-----------------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb.exceptions import VNDBAPIError

   async def basic_error_handling():
       try:
           async with VNDB() as client:
               response = await client.vn.query(query)
               return response.results
               
       except VNDBAPIError as e:
           print(f"VNDB API error: {e}")
           return []

Specific Error Handling
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb.exceptions import (
       AuthenticationError,
       RateLimitError, 
       InvalidRequestError,
       NotFoundError,
       ServerError,
       TooMuchDataSelectedError
   )

   async def comprehensive_error_handling():
       try:
           async with VNDB(api_token="your-token") as client:
               response = await client.vn.query(query)
               return response.results
               
       except AuthenticationError:
           print("Authentication failed - check your API token")
           return None
           
       except RateLimitError:
           print("Rate limit exceeded - implement backoff")
           return None
           
       except InvalidRequestError as e:
           print(f"Invalid request: {e}")
           # Could implement validation and retry logic here
           return None
           
       except NotFoundError:
           print("Requested resource not found")
           return []
           
       except TooMuchDataSelectedError:
           print("Query too large - reducing scope")
           # Implement logic to reduce query scope
           return None
           
       except ServerError:
           print("Server error - retry later")
           return None

Retry Logic with Exponential Backoff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import random
   from typing import Optional

   async def robust_query(
       client: VNDB, 
       query: QueryRequest, 
       max_retries: int = 3
   ) -> Optional[QueryResponse]:
       
       for attempt in range(max_retries):
           try:
               return await client.vn.query(query)
               
           except RateLimitError:
               if attempt < max_retries - 1:
                   # Exponential backoff: 1s, 2s, 4s, etc.
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   print(f"Rate limited, waiting {wait_time:.2f}s")
                   await asyncio.sleep(wait_time)
               else:
                   print("Max retries exceeded for rate limit")
                   raise
                   
           except ServerError:
               if attempt < max_retries - 1:
                   # Fixed delay for server errors
                   wait_time = 5 + random.uniform(0, 5)
                   print(f"Server error, waiting {wait_time:.2f}s")
                   await asyncio.sleep(wait_time)
               else:
                   print("Max retries exceeded for server error")
                   raise
                   
           except (AuthenticationError, InvalidRequestError, NotFoundError):
               # These errors won't be resolved by retrying
               raise

Validation-First Approach
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def validated_query(client: VNDB, endpoint: str, filters, fields: str):
       # Validate before querying
       validation = await client.validate_filters(endpoint, filters)
       
       if not validation['valid']:
           # Handle validation errors
           print("Validation failed:")
           for error in validation['errors']:
               print(f"  - {error}")
           
           # Try to auto-correct
           if validation['suggestions']:
               print(f"Suggestions: {validation['suggestions']}")
               # Could implement auto-correction logic here
           
           raise InvalidRequestError("Filter validation failed")
       
       # Proceed with validated query
       try:
           query = QueryRequest(filters=filters, fields=fields)
           return await getattr(client, endpoint.strip('/')).query(query)
           
       except VNDBAPIError:
           # Handle API errors
           raise

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def graceful_vn_search(client: VNDB, search_term: str):
       """Search for VNs with graceful degradation on errors."""
       
       # Start with comprehensive query
       full_query = QueryRequest(
           filters=["title", "~", search_term],
           fields="id, title, rating, description, image.url, developers{name}",
           sort="rating",
           reverse=True,
           results=20
       )
       
       try:
           return await client.vn.query(full_query)
           
       except TooMuchDataSelectedError:
           print("Query too large, reducing fields...")
           # Reduce to essential fields only
           reduced_query = QueryRequest(
               filters=["title", "~", search_term],
               fields="id, title, rating",
               sort="rating", 
               reverse=True,
               results=10
           )
           return await client.vn.query(reduced_query)
           
       except RateLimitError:
           print("Rate limited, trying with smaller result set...")
           await asyncio.sleep(2)
           small_query = QueryRequest(
               filters=["title", "~", search_term],
               fields="id, title",
               results=5
           )
           return await client.vn.query(small_query)
           
       except InvalidRequestError:
           print("Invalid search term, trying exact match...")
           # Fall back to exact match
           exact_query = QueryRequest(
               filters=["title", "=", search_term],
               fields="id, title"
           )
           return await client.vn.query(exact_query)

Error Context Preservation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import traceback
   from typing import Optional

   class VNDBError(Exception):
       """Custom application error with context."""
       
       def __init__(self, message: str, original_error: Optional[Exception] = None):
           super().__init__(message)
           self.original_error = original_error
           self.traceback = traceback.format_exc() if original_error else None

   async def contextual_query(client: VNDB, query: QueryRequest):
       try:
           return await client.vn.query(query)
           
       except AuthenticationError as e:
           raise VNDBError(
               "Failed to authenticate with VNDB. Please check your API token.",
               original_error=e
           )
           
       except InvalidRequestError as e:
           raise VNDBError(
               f"Invalid query: {e}. Check your filters and field names.",
               original_error=e
           )
           
       except VNDBAPIError as e:
           raise VNDBError(
               f"VNDB API error: {e}",
               original_error=e
           )

Logging Best Practices
----------------------

.. code-block:: python

   import logging

   # Configure logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   async def logged_operations():
       try:
           async with VNDB() as client:
               logger.info("Starting VNDB query")
               response = await client.vn.query(query)
               logger.info(f"Query successful: {len(response.results)} results")
               return response.results
               
       except AuthenticationError:
           logger.error("Authentication failed")
           raise
           
       except RateLimitError:
           logger.warning("Rate limit exceeded")
           raise
           
       except VNDBAPIError as e:
           logger.error(f"VNDB API error: {e}")
           raise

Testing Error Conditions
------------------------

.. code-block:: python

   import pytest
   from veedb.exceptions import InvalidRequestError

   @pytest.mark.asyncio
   async def test_invalid_filter():
       async with VNDB() as client:
           with pytest.raises(InvalidRequestError):
               invalid_query = QueryRequest(filters=["invalid_field", "=", "test"])
               await client.vn.query(invalid_query)

   @pytest.mark.asyncio
   async def test_authentication_required():
       async with VNDB() as client:  # No API token           with pytest.raises(AuthenticationError):
               await client.get_authinfo()

Best Practices
--------------

1. **Always Handle Exceptions**: Never let VNDB exceptions bubble up unhandled
2. **Use Specific Exceptions**: Catch specific exception types rather than the base class
3. **Implement Retry Logic**: For transient errors like rate limits and server errors
4. **Validate First**: Use the validation system to catch errors early
5. **Log Appropriately**: Log errors with sufficient context for debugging
6. **Graceful Degradation**: Implement fallback strategies when possible
7. **User-Friendly Messages**: Convert technical errors to user-friendly messages
8. **Don't Retry Non-Transient Errors**: Don't retry authentication or validation errors
9. **Monitor Error Rates**: Track error frequencies to identify patterns
10. **Test Error Paths**: Write tests for error conditions
