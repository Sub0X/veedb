# VeeDB Documentation

Welcome to VeeDB's documentation!
======================================

VeeDB is an unofficial asynchronous Python wrapper for the VNDB.org API v2 (Kana). 
"Vee" represents the v-sign pose and starting letter for VNDB, while "DB" stands for database.

This library provides a convenient way to interact with the VNDB API, allowing you to query 
visual novel data, manage user lists, and more, all asynchronously with full type safety.

Key Features
============

- **Asynchronous API**: Built with aiohttp for high-performance async operations
- **Type Safety**: Full type annotations and dataclass parsing with dacite
- **Filter Validation**: Comprehensive filter validation system with schema caching
- **Complete Coverage**: Support for all major VNDB API v2 endpoints
- **List Management**: Full CRUD operations for user and release lists
- **Authentication**: Support for API token authentication
- **Testing Support**: Optional sandbox mode for development

Quick Start
===========

.. code-block:: python

   import asyncio
   from veedb import VNDB, QueryRequest

   async def main():
       async with VNDB() as client:
           # Get database stats
           stats = await client.get_stats()
           print(f"Total VNs: {stats.vn}")
           
           # Query visual novels
           query = QueryRequest(
               filters=["title", "~", "Fate"],
               fields="id, title, rating"
           )
           response = await client.vn.query(query)
           
           for vn in response.results:
               print(f"{vn.title}: {vn.rating}")

   asyncio.run(main())

.. toctree::
   :maxdepth: 2
   :caption: User Guide:
   
   installation
   quickstart
   filter_validation
   authentication
   examples

.. toctree::
   :maxdepth: 2
   :caption: Development:
   
   contributing
   changelog

.. toctree::
   :maxdepth: 2
   :caption: API Reference:
   
   api/client
   api/validation
   api/types
   api/exceptions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
   :members:
   :show-inheritance:

.. autoclass:: veedb.SchemaCache
   :members:
   :show-inheritance:

Exception Classes
-----------------

.. automodule:: veedb.exceptions
   :members:
   :show-inheritance:
   :no-index:

Type Definitions
----------------

Common Types
~~~~~~~~~~~~

.. automodule:: veedb.apitypes.common
   :members:
   :show-inheritance:
   :no-index:

Request Types
~~~~~~~~~~~~~

.. automodule:: veedb.apitypes.requests
   :members:
   :show-inheritance:
   :no-index:

Entity Types
~~~~~~~~~~~~

Visual Novel Entities
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.vn
   :members:
   :show-inheritance:
   :no-index:

Character Entities
^^^^^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.character
   :members:
   :show-inheritance:
   :no-index:

Producer Entities
^^^^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.producer
   :members:
   :show-inheritance:
   :no-index:

Release Entities
^^^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.release
   :members:
   :show-inheritance:
   :no-index:

Staff Entities
^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.staff
   :members:
   :show-inheritance:
   :no-index:

Tag Entities
^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.tag
   :members:
   :show-inheritance:
   :no-index:

Trait Entities
^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.trait
   :members:
   :show-inheritance:
   :no-index:

Quote Entities
^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.quote
   :members:
   :show-inheritance:
   :no-index:

User List Entities
^^^^^^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.ulist
   :members:
   :show-inheritance:
   :no-index:

User Entities
^^^^^^^^^^^^^

.. automodule:: veedb.apitypes.entities.user
   :members:
   :show-inheritance:
   :no-index:
