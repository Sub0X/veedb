Contributing
============

Thank you for your interest in contributing to VeeDB! This document provides guidelines for contributing to the project.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.8 or higher
- pip package manager
- Git

Setting up the Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/Sub0X/veedb.git
   cd veedb

2. Create a virtual environment:

.. code-block:: bash

   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/macOS
   source venv/bin/activate

3. Install the package in development mode:

.. code-block:: bash

   pip install -e .

4. Install development dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

Project Structure
-----------------

::

   veedb/
   ├── src/veedb/           # Main package source
   │   ├── __init__.py      # Package initialization and exports
   │   ├── client.py        # Main VNDB client and endpoint clients
   │   ├── schema_validator.py  # Filter validation system
   │   ├── exceptions.py    # Custom exception classes
   │   ├── apitypes/        # Type definitions
   │   │   ├── common.py    # Common types and structures
   │   │   ├── requests.py  # Request payload types
   │   │   └── entities/    # API entity types
   │   └── methods/         # HTTP method implementations
   ├── docs/               # Documentation source
   ├── examples/           # Usage examples
   ├── tests/             # Test suite
   └── assets/            # Assets (schema examples, etc.)

Making Changes
--------------

Code Style
~~~~~~~~~~

- Follow PEP 8 coding standards
- Use type hints for all function parameters and return values
- Use descriptive variable and function names
- Add docstrings to all public methods and classes

Testing
~~~~~~~

Before submitting changes, ensure all tests pass:

.. code-block:: bash

   python -m pytest tests/

To run tests with coverage:

.. code-block:: bash

   python -m pytest tests/ --cov=veedb --cov-report=html

Documentation
~~~~~~~~~~~~~

When making changes that affect the public API:

1. Update docstrings in the code
2. Update relevant documentation in ``docs/``
3. Add examples if introducing new features
4. Update the CHANGELOG.md

To build documentation locally:

.. code-block:: bash

   cd docs
   make html

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

- Your Python version
- VeeDB version
- A minimal code example that reproduces the issue
- The full error traceback
- Expected vs actual behavior

Feature Requests
~~~~~~~~~~~~~~~~

When requesting features:

- Explain the use case and why it would be valuable
- Provide examples of how the feature would be used
- Consider the scope and complexity of the implementation

Code Contributions
~~~~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Create a feature branch** from main:

.. code-block:: bash

   git checkout -b feature/your-feature-name

3. **Make your changes** following the guidelines above
4. **Add or update tests** for your changes
5. **Update documentation** if needed
6. **Commit your changes** with clear, descriptive messages:

.. code-block:: bash

   git commit -m "Add feature: brief description of what you added"

7. **Push to your fork**:

.. code-block:: bash

   git push origin feature/your-feature-name

8. **Create a Pull Request** on GitHub

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation as needed
- Follow the existing code style
- Keep commits focused and atomic

API Design Principles
---------------------

When contributing to VeeDB, keep these principles in mind:

Type Safety
~~~~~~~~~~~
- All public APIs should have proper type hints
- Use dataclasses for structured data
- Prefer strong typing over generic types where possible

Async/Await
~~~~~~~~~~~
- All API calls should be async
- Use proper async context managers where appropriate
- Handle async cleanup properly

Error Handling
~~~~~~~~~~~~~~
- Use specific exception types for different error conditions
- Provide helpful error messages
- Don't silently fail

Performance
~~~~~~~~~~~
- Cache API schemas when possible
- Use connection pooling for HTTP requests
- Avoid blocking operations in async code

Working with the VNDB API
--------------------------

API Documentation
~~~~~~~~~~~~~~~~~
- Reference the `VNDB API v2 documentation <https://vndb.org/d11>`_
- Test against the sandbox API when developing: ``https://beta.vndb.org/api/kana``
- Understand the filter syntax and field structures

Schema Validation
~~~~~~~~~~~~~~~~~
- The validation system downloads and caches the API schema
- New field types should be added to the appropriate entity dataclasses
- Filter validation should handle nested fields properly

Authentication
~~~~~~~~~~~~~~
- Some endpoints require API tokens
- Test both authenticated and unauthenticated scenarios
- Handle permission errors gracefully

Release Process
---------------

Releases are handled by maintainers and follow semantic versioning:

- **Major version** (X.0.0): Breaking changes to public API
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

Getting Help
------------

If you need help with contributing:

- Check existing issues and discussions
- Create an issue for questions or clarification
- Join the project discussions

Code of Conduct
----------------

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and improve
- Follow GitHub's community guidelines

Thank you for contributing to VeeDB!
