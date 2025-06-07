Type Definitions
================

VeeDB provides comprehensive type definitions for all VNDB API entities and request/response structures.

Common Types
------------

Query and Response Types
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.QueryRequest
   :members:
   :show-inheritance:
   :no-index:
   
   Request structure for querying VNDB endpoints.
   
   **Attributes:**
   
   - ``filters`` (Optional[Union[List, str]]): Filter expression
   - ``fields`` (Optional[str]): Comma-separated list of fields to retrieve
   - ``sort`` (Optional[str]): Field to sort by
   - ``reverse`` (bool): Whether to sort in reverse order (default: False)
   - ``results`` (Optional[int]): Maximum number of results to return
   - ``page`` (Optional[int]): Page number for pagination
   - ``user`` (Optional[str]): User ID for user-specific queries
   - ``count`` (bool): Whether to include result count (default: False)
   - ``compact_filters`` (bool): Whether to use compact filter format (default: False)
   
   **Example:**
   
   .. code-block:: python
   
      query = QueryRequest(
          filters=["title", "~", "fate"],
          fields="id, title, rating",
          sort="rating",
          reverse=True,
          results=10
      )

.. autoclass:: veedb.apitypes.common.QueryResponse
   :members:
   :show-inheritance:
   :no-index:
   
   Response structure from VNDB query endpoints.

Identifier Types
~~~~~~~~~~~~~~~~

.. autoclass:: veedb.VNDBID
   :members:
   :show-inheritance:
   :no-index:
   
   Type alias for VNDB entity IDs (strings starting with specific prefixes).

.. autoclass:: veedb.ReleaseDate
   :members:
   :show-inheritance:
   :no-index:
   
   Type for release dates in VNDB format.

Enumeration Types
~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.LanguageEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of supported languages.

.. autoclass:: veedb.PlatformEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of supported platforms.

.. autoclass:: veedb.StaffRoleEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of staff roles.

.. autoclass:: veedb.TagCategoryEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of tag categories.

.. autoclass:: veedb.ProducerTypeEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of producer types.

.. autoclass:: veedb.DevStatusEnum
   :members:
   :show-inheritance:
   :no-index:
   
   Enumeration of development status values.

Request Types
-------------

List Update Payloads
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: veedb.UlistUpdatePayload
   :members:
   :show-inheritance:
   :no-index:
   
   Payload for updating user visual novel lists.
   
   **Attributes:**
   
   - ``id`` (str): VN ID to update
   - ``vote`` (Optional[int]): User rating (1-100)
   - ``notes`` (Optional[str]): User notes
   - ``started`` (Optional[str]): Date started reading
   - ``finished`` (Optional[str]): Date finished reading
   - ``labels`` (Optional[List[int]]): List label IDs
   
   **Example:**
   
   .. code-block:: python
   
      payload = UlistUpdatePayload(
          id="v17",
          vote=85,
          notes="Excellent sci-fi visual novel",
          finished="2023-06-15"
      )

.. autoclass:: veedb.RlistUpdatePayload
   :members:
   :show-inheritance:
   :no-index:
   
   Payload for updating user release lists.
   
   **Attributes:**
   
   - ``id`` (str): Release ID to update
   - ``status`` (Optional[str]): Release status

Entity Types
------------

Visual Novel Entities
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.vn
   :members:
   :show-inheritance:
   
   Visual novel related entity types.
   
   **Key Classes:**
   
   - ``VN``: Main visual novel entity
   - ``VNQueryItem``: VN data as returned from queries
   - ``VNImage``: VN cover image information
   - ``VNRelation``: VN relationship information
   - ``VNAnime``: Related anime information
   - ``VNLength``: VN length statistics

Character Entities
~~~~~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.character
   :members:
   :show-inheritance:
   
   Character related entity types.
   
   **Key Classes:**
   
   - ``Character``: Main character entity
   - ``CharacterQueryItem``: Character data from queries
   - ``CharacterImage``: Character image information
   - ``CharacterTrait``: Character trait information
   - ``CharacterVN``: Character's VN appearances

Producer Entities
~~~~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.producer
   :members:
   :show-inheritance:
   
   Producer/developer related entity types.
   
   **Key Classes:**
   
   - ``Producer``: Main producer entity
   - ``ProducerQueryItem``: Producer data from queries
   - ``ProducerRelation``: Producer relationship information

Release Entities
~~~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.release
   :members:
   :show-inheritance:
   
   Release related entity types.
   
   **Key Classes:**
   
   - ``Release``: Main release entity
   - ``ReleaseQueryItem``: Release data from queries
   - ``ReleaseMedia``: Release media information
   - ``ReleaseProducer``: Release producer information

Staff Entities
~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.staff
   :members:
   :show-inheritance:
   
   Staff related entity types.
   
   **Key Classes:**
   
   - ``Staff``: Main staff entity
   - ``StaffQueryItem``: Staff data from queries
   - ``StaffAlias``: Staff alias information

Tag Entities
~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.tag
   :members:
   :show-inheritance:
   
   Tag related entity types.
   
   **Key Classes:**
   
   - ``Tag``: Main tag entity
   - ``TagQueryItem``: Tag data from queries

Trait Entities
~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.trait
   :members:
   :show-inheritance:
   
   Character trait related entity types.
   
   **Key Classes:**
   
   - ``Trait``: Main trait entity
   - ``TraitQueryItem``: Trait data from queries

Quote Entities
~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.quote
   :members:
   :show-inheritance:
   
   Quote related entity types.
   
   **Key Classes:**
   
   - ``Quote``: Main quote entity
   - ``QuoteQueryItem``: Quote data from queries

User List Entities
~~~~~~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.ulist
   :members:
   :show-inheritance:
   
   User list related entity types.
   
   **Key Classes:**
   
   - ``Ulist``: User VN list entry
   - ``UlistQueryItem``: User list data from queries
   - ``UlistLabels``: User list label information

User Entities
~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.entities.user
   :members:
   :show-inheritance:
   
   User related entity types.
   
   **Key Classes:**
   
   - ``User``: Main user entity
   - ``UserQueryItem``: User data from queries
   - ``AuthInfo``: Authentication information
   - ``Stats``: Database statistics

Type Usage Examples
-------------------

Creating Query Requests
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import QueryRequest

   # Basic query
   basic_query = QueryRequest(
       filters=["id", "=", "v17"],
       fields="title, rating"
   )

   # Complex query with sorting and pagination
   complex_query = QueryRequest(
       filters=["and", ["rating", ">", 8.0], ["released", ">", "2020-01-01"]],
       fields="id, title, rating, released, description",
       sort="rating",
       reverse=True,
       results=25,
       page=1
   )

   # User-specific query
   user_query = QueryRequest(
       filters=["uid", "=", "u12345"],
       fields="id, vote, notes, vn{title}",
       user="u12345"
   )

Working with Response Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Query visual novels
   response = await client.vn.query(query)

   # Response is typed as QueryResponse[VNQueryItem]
   for vn in response.results:
       print(f"Title: {vn.title}")
       print(f"Rating: {vn.rating}")
       print(f"Released: {vn.released}")
       
       # Access nested data
       if vn.image:
           print(f"Cover: {vn.image.url}")
       
       if vn.developers:
           for dev in vn.developers:
               print(f"Developer: {dev.name}")

Updating User Lists
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import UlistUpdatePayload

   # Create update payload
   payload = UlistUpdatePayload(
       id="v17",
       vote=90,
       notes="Amazing storyline!",
       started="2023-06-01",
       finished="2023-06-15",
       labels=[1, 3]  # Label IDs
   )

   # Update user list
   await client.ulist.update("v17", payload)

Working with Enums
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import LanguageEnum, PlatformEnum

   # Query releases for specific language and platform
   query = QueryRequest(
       filters=[
           "and",
           ["languages", "=", [LanguageEnum.EN]],
           ["platforms", "=", [PlatformEnum.WIN]]
       ],
       fields="title, languages, platforms"
   )

   response = await client.release.query(query)

Type Annotations
----------------

VeeDB is fully typed and supports type checking with mypy:

.. code-block:: python

   from typing import List
   from veedb import VNDB, QueryRequest, QueryResponse
   from veedb.apitypes.entities.vn import VNQueryItem

   async def get_top_vns(client: VNDB, limit: int = 10) -> List[VNQueryItem]:
       query = QueryRequest(
           filters=["rating", ">", 8.0],
           fields="title, rating",
           sort="rating",
           reverse=True,
           results=limit
       )
       
       response: QueryResponse[VNQueryItem] = await client.vn.query(query)
       return response.results

   # Usage with type checking
   async def main() -> None:
       async with VNDB() as client:
           top_vns = await get_top_vns(client, 20)
           for vn in top_vns:
               # Type checker knows vn is VNQueryItem
               print(f"{vn.title}: {vn.rating}")

Optional Fields
---------------

Many entity fields are optional and may be ``None``:

.. code-block:: python

   async def safe_field_access():
       response = await client.vn.query(query)
       
       for vn in response.results:
           # Always check optional fields
           if vn.rating is not None:
               print(f"Rating: {vn.rating}")
           else:
               print("No rating available")
           
           # Safe access with default
           description = vn.description or "No description available"
           print(f"Description: {description}")
           
           # Check nested optional fields
           if vn.image and vn.image.url:
               print(f"Cover image: {vn.image.url}")

Union Types
-----------

Some fields accept multiple types:

.. code-block:: python

   from typing import Union

   # Filters can be various types
   def create_filter(value: Union[str, int, List[str]]) -> List:
       if isinstance(value, list):
           return ["id", "=", value]
       else:
           return ["title", "~", str(value)]

   # Use with different types
   string_filter = create_filter("fate")
   list_filter = create_filter(["v17", "v18"])

Generic Types
-------------

VeeDB uses generics for type safety:

.. code-block:: python

   from typing import TypeVar, Generic
   from veedb.client import _BaseEntityClient

   # Entity clients are generic
   T_Entity = TypeVar('T_Entity')
   T_QueryItem = TypeVar('T_QueryItem')

   # This ensures type safety across different endpoints
   vn_client: _BaseEntityClient[VN, VNQueryItem] = client.vn
   char_client: _BaseEntityClient[Character, CharacterQueryItem] = client.character

Dataclass Features
------------------

All entity types are dataclasses with additional features:

.. code-block:: python

   from dataclasses import asdict, astuple

   # Convert to dictionary
   vn_dict = asdict(vn)
   print(f"VN as dict: {vn_dict}")

   # Convert to tuple
   vn_tuple = astuple(vn)

   # Create with partial data
   from veedb.apitypes.entities.vn import VN
   
   partial_vn = VN(
       id="v17",
       title="Ever17",
       # Other fields will be None
   )

Type Validation
---------------

VeeDB uses dacite for runtime type validation:

.. code-block:: python

   # Data from API is automatically validated
   response = await client.vn.query(query)
   
   # If API returns invalid data, dacite will raise an error
   # This ensures type safety at runtime

Best Practices
--------------

1. **Use Type Hints**: Always use type hints for better IDE support
2. **Check Optional Fields**: Always check if optional fields are None
3. **Use Enums**: Use provided enums instead of string literals
4. **Type Guards**: Use isinstance() for union type checking
5. **Dataclass Methods**: Take advantage of dataclass features
6. **Generic Awareness**: Understand generic type parameters
7. **Runtime Validation**: Trust that VeeDB validates API responses

IDE Support
-----------

VeeDB provides excellent IDE support through:

- **Autocomplete**: Full autocompletion for all fields and methods
- **Type Checking**: Static type checking with mypy
- **Documentation**: Docstrings for all public APIs
- **Error Detection**: Catch type errors before runtime
