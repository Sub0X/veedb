Installation
============

Requirements
------------

VeeDB requires Python 3.8 or higher and has the following dependencies:

- ``aiohttp`` (>=3.8.0, <5.0.0) - For asynchronous HTTP requests
- ``dacite`` (>=1.6.0, <2.0.0) - For dataclass creation and type conversion

Installation Methods
--------------------

From PyPI
~~~~~~~~~

.. code-block:: bash

   pip install veedb

From Source
~~~~~~~~~~~

You can install directly from the GitHub repository:

.. code-block:: bash

   pip install git+https://github.com/Sub0X/veedb.git

For development, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/Sub0X/veedb.git
   cd veedb
   pip install -e .

Development Installation
------------------------

For development work, you'll want to install additional dependencies:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Sub0X/veedb.git
   cd veedb
   
   # Install in development mode with test dependencies
   pip install -e ".[dev]"
   
   # Or install test dependencies manually
   pip install -e .
   pip install pytest pytest-asyncio

Virtual Environment
-------------------

It's recommended to use a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv veedb-env
   
   # Activate (Linux/Mac)
   source veedb-env/bin/activate
   
   # Activate (Windows)
   veedb-env\Scripts\activate
   
   # Install veedb
   pip install veedb

Verification
------------

To verify your installation:

.. code-block:: python

   import veedb
   print(veedb.__version__)

   # Test basic functionality
   import asyncio
   from veedb import VNDB

   async def test():
       async with VNDB() as client:
           stats = await client.get_stats()
           print(f"VNDB has {stats.vn} visual novels")

   asyncio.run(test())

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error**: If you get import errors, make sure you're using Python 3.8+:

.. code-block:: bash

   python --version
   pip --version

**Dependencies**: If you have dependency conflicts, try using a fresh virtual environment.

**Network Issues**: VeeDB requires internet access to connect to the VNDB API. Make sure your firewall/proxy settings allow connections to ``api.vndb.org``.

Platform-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~~

**Windows**: If you encounter SSL certificate issues, you may need to update your certificates or use ``pip install --trusted-host pypi.org --trusted-host pypi.python.org veedb``

**Linux**: Some distributions require the ``python3-dev`` package for building certain dependencies.

**macOS**: Ensure you have the latest Xcode command line tools if building from source.
