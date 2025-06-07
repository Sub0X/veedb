Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

Added
~~~~~
- Comprehensive documentation using Sphinx
- API reference documentation for all modules
- User guide with examples and best practices
- Filter validation system with schema caching
- Type-safe API responses using dataclasses

Changed
~~~~~~~
- Updated ``get_stats()`` method to return proper ``UserStats`` dataclass instead of generic dict
- Improved error handling and logging

Fixed
~~~~~
- Fixed missing newlines in client.py file structure
- Corrected type exports in ``__init__.py``

0.1.0 (2024-12-01)
------------------

Added
~~~~~
- Initial release of VeeDB async Python wrapper for VNDB API v2 (Kana)
- Support for all major VNDB API endpoints
- Asynchronous API calls using aiohttp
- Data parsing into Python dataclasses using dacite
- Custom exceptions for API errors
- Support for API token authentication
- Optional sandbox mode for testing
- Filter validation system with automatic schema caching
- User and release list management (CRUD operations)
- Comprehensive type definitions for all API entities
- SSL timeout error filtering for cleaner logs

API Endpoints Supported
~~~~~~~~~~~~~~~~~~~~~~~
- ``/schema`` - Get API schema
- ``/stats`` - Get database statistics  
- ``/user`` - Get user information
- ``/authinfo`` - Get authentication info
- ``/vn`` - Query visual novels
- ``/release`` - Query releases
- ``/producer`` - Query producers
- ``/character`` - Query characters
- ``/staff`` - Query staff
- ``/tag`` - Query tags
- ``/trait`` - Query traits
- ``/quote`` - Query quotes
- ``/ulist`` - User list operations
- ``/rlist`` - Release list operations

Filter Validation Features
~~~~~~~~~~~~~~~~~~~~~~~~~~
- Automatic schema download and caching
- Filter expression validation against API schema
- Field name suggestions for typos
- Nested field support with dot notation
- Configurable cache TTL and directory
- Integration with all endpoint clients

Dependencies
~~~~~~~~~~~~
- Python 3.8+
- aiohttp >=3.8.0,<5.0.0
- dacite >=1.6.0,<2.0.0
