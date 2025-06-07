Client API
==========

This section documents the main client classes and their methods.

Main VNDB Client
================

.. autoclass:: veedb.VNDB
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
   
   .. automethod:: __init__
      :no-index:
   
   The main client class for interacting with the VNDB API.
   
   **Parameters:**
   
   - ``api_token`` (Optional[str]): API token for authenticated requests
   - ``use_sandbox`` (bool): Whether to use the sandbox API endpoint (default: False)
   - ``session`` (Optional[aiohttp.ClientSession]): Custom aiohttp session
   - ``local_schema_path`` (Optional[str]): Path to local schema file
   - ``schema_cache_dir`` (str): Directory for schema cache (default: ".veedb_cache")
   - ``schema_cache_ttl_hours`` (float): Cache TTL in hours (default: 24.0)

   **Basic Usage:**
   
   .. code-block:: python
   
      async with VNDB() as client:
          stats = await client.get_stats()
          print(f"Total VNs: {stats.vn}")

   **With Authentication:**
   
   .. code-block:: python
   
      async with VNDB(api_token="your-token") as client:
          auth_info = await client.get_authinfo()
          print(f"Logged in as: {auth_info.username}")

Endpoint-Specific Clients
==========================

Visual Novel Client
~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.client._VNClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.vn``. Provides methods for querying visual novel data.
   
   **Example:**
   
   .. code-block:: python
   
      query = QueryRequest(
          filters=["title", "~", "fate"],
          fields="id, title, rating"
      )
      response = await client.vn.query(query)

Character Client
~~~~~~~~~~~~~~~~

.. autoclass:: veedb.client._CharacterClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.character``. Provides methods for querying character data.

Release Client
~~~~~~~~~~~~~~

.. autoclass:: veedb.client._ReleaseClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.release``. Provides methods for querying release data.

Producer Client
~~~~~~~~~~~~~~~

.. autoclass:: veedb.client._ProducerClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.producer``. Provides methods for querying producer data.

Staff Client
~~~~~~~~~~~~

.. autoclass:: veedb.client._StaffClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.staff``. Provides methods for querying staff data.

Tag Client
~~~~~~~~~~

.. autoclass:: veedb.client._TagClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.tag``. Provides methods for querying tag data.

Trait Client
~~~~~~~~~~~~

.. autoclass:: veedb.client._TraitClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.trait``. Provides methods for querying trait data.

Quote Client
~~~~~~~~~~~~

.. autoclass:: veedb.client._QuoteClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.quote``. Provides methods for querying quote data.

User List Client
~~~~~~~~~~~~~~~~

.. autoclass:: veedb.client._UlistClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.ulist``. Provides methods for managing user visual novel lists.
   
   **Requires authentication** for write operations.
   
   **Example:**
   
   .. code-block:: python
   
      # Query user's list
      query = QueryRequest(
          filters=["uid", "=", user_id],
          fields="id, vote, notes, vn{title}"
      )
      response = await client.ulist.query(query)
      
      # Update list entry
      payload = UlistUpdatePayload(id="v17", vote=85, notes="Great VN!")
      await client.ulist.update("v17", payload)

Release List Client
~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.client._RlistClient
   :members:
   :show-inheritance:
   
   Accessed via ``client.rlist``. Provides methods for managing user release lists.
   
   **Requires authentication** for write operations.

Base Entity Client
------------------

.. autoclass:: veedb.client._BaseEntityClient
   :members:
   :show-inheritance:
   
   Base class for all endpoint-specific clients. Provides common functionality
   like query methods and filter validation.

Client Methods Reference
------------------------

Query Methods
~~~~~~~~~~~~~

All endpoint clients inherit these methods from ``_BaseEntityClient``:

.. automethod:: veedb.client._BaseEntityClient.query
   :no-index:

   Query the endpoint with the given parameters.
   
   **Parameters:**
   
   - ``query_options`` (QueryRequest): Query parameters including filters, fields, sorting, etc.
   
   **Returns:**
   
   - ``QueryResponse[T_QueryItem]``: Response containing results and metadata

.. automethod:: veedb.client._BaseEntityClient.validate_filters
   :no-index:

   Validate filters against the API schema for this endpoint.
   
   **Parameters:**
   
   - ``filters`` (Union[List, str, None]): Filter expression to validate
   
   **Returns:**
   
   - ``Dict[str, Any]``: Validation result with 'valid', 'errors', 'suggestions' keys

.. automethod:: veedb.client._BaseEntityClient.get_available_fields
   :no-index:

   Get all available fields for this endpoint.
   
   **Returns:**
   
   - ``List[str]``: List of available field names

List Management Methods
~~~~~~~~~~~~~~~~~~~~~~~

For ``_UlistClient`` and ``_RlistClient``:

.. note::
   The user list management methods (update, delete) are currently not implemented in the client.
   Please refer to the main VNDB API documentation for direct API usage.

Main Client Methods
~~~~~~~~~~~~~~~~~~~

.. automethod:: veedb.VNDB.get_stats
   :no-index:

   Get database statistics.
   
   **Returns:**
   
   - ``Stats``: Database statistics including VN count, character count, etc.

.. automethod:: veedb.VNDB.get_schema
   :no-index:

   Get the API schema.
   
   **Returns:**
   
   - ``Dict[str, Any]``: Complete API schema

.. automethod:: veedb.VNDB.get_user
   :no-index:

   Get user information by ID.
   
   **Parameters:**
   
   - ``user_id`` (str): User ID to query
   
   **Returns:**
   
   - ``User``: User information

.. automethod:: veedb.VNDB.get_authinfo
   :no-index:

   Get authentication information for the current token.
   
   **Returns:**
   
   - ``AuthInfo``: Authentication details
   
   **Requires:** Authentication

Validation Methods
~~~~~~~~~~~~~~~~~~

.. automethod:: veedb.VNDB.validate_filters
   :no-index:

   Validate filters against the API schema.
   
   **Parameters:**
   
   - ``endpoint`` (str): API endpoint (e.g., "/vn", "/character")
   - ``filters`` (Union[List, str, None]): Filter expression to validate
   
   **Returns:**
   
   - ``Dict[str, Any]``: Validation result

.. automethod:: veedb.VNDB.get_available_fields
   :no-index:

   Get available fields for an endpoint.
   
   **Parameters:**
   
   - ``endpoint`` (str): API endpoint
   
   **Returns:**
   
   - ``List[str]``: Available field names

.. automethod:: veedb.VNDB.list_endpoints
   :no-index:

   Get all available API endpoints.
   
   **Returns:**
   
   - ``List[str]``: Available endpoints

Cache Management
~~~~~~~~~~~~~~~~

.. automethod:: veedb.VNDB.invalidate_schema_cache
   :no-index:

   Invalidate the schema cache, forcing a refresh on next use.

.. automethod:: veedb.VNDB.update_local_schema
   :no-index:

   Force download of the latest schema.
   
   **Returns:**
   
   - ``Dict[str, Any]``: Updated schema data

Context Manager Support
~~~~~~~~~~~~~~~~~~~~~~~

All clients support async context manager protocol:

.. code-block:: python

   async with VNDB() as client:
       # Client is automatically opened and closed
       response = await client.vn.query(query)
   # Session is automatically closed here

This ensures proper cleanup of HTTP sessions and other resources.
