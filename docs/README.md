# VeeDB Documentation

This directory contains the Sphinx documentation for VeeDB, a Python library for interacting with the VNDB API.

## Building the Documentation Locally

### Prerequisites

1. Python 3.8 or higher
2. Install VeeDB in development mode:
   ```bash
   pip install -e .
   ```

### Install Documentation Dependencies

```bash
pip install -r docs/requirements.txt
pip install dacite  # Required for imports
```

### Build the Documentation

```bash
cd docs
sphinx-build -b html . _build/html
```

The built documentation will be available in `docs/_build/html/index.html`.

### Live Reload During Development

For development, you can use sphinx-autobuild for automatic rebuilding:

```bash
pip install sphinx-autobuild
cd docs
sphinx-autobuild . _build/html
```

This will start a local server at `http://localhost:8000` that automatically rebuilds when you make changes.

## Documentation Structure

- `index.rst` - Main documentation page
- `installation.rst` - Installation guide
- `quickstart.rst` - Quick start guide
- `authentication.rst` - Authentication setup
- `examples.rst` - Usage examples
- `filter_validation.rst` - Filter validation guide
- `changelog.rst` - Change log
- `contributing.rst` - Contributing guidelines
- `api/` - API reference documentation
  - `client.rst` - Client classes and methods
  - `exceptions.rst` - Exception handling
  - `types.rst` - Type definitions
  - `validation.rst` - Validation utilities

## Automated Deployment

The documentation is automatically built and deployed via GitHub Actions:

- **On Pull Requests**: Documentation is built to verify it compiles without errors
- **On Push to Main/Master**: Documentation is built and deployed to GitHub Pages
- **On Releases**: Documentation is built and deployed with the latest version

The live documentation is available at: `https://<username>.github.io/veedb/`

## Writing Documentation

### RST Guidelines

- Use proper heading hierarchy:
  ```rst
  Page Title
  ==========
  
  Section
  -------
  
  Subsection
  ~~~~~~~~~~
  
  Subsubsection
  ^^^^^^^^^^^^^
  ```

- Always ensure underlines are at least as long as the title text

### Code Examples

- Include complete, runnable examples
- Show both basic and advanced usage
- Include error handling examples
- Test your examples to ensure they work

### API Documentation

The API documentation is auto-generated from docstrings using Sphinx autodoc. To document new classes or methods:

1. Add comprehensive docstrings to your Python code
2. Add the class/method to the appropriate `.rst` file in the `api/` directory
3. Use autodoc directives like `.. autoclass::` and `.. automethod::`

### Building Without Warnings

The CI builds with the `-W` flag, which treats warnings as errors. Before submitting:

```bash
cd docs
sphinx-build -b html . _build/html -W
```

This ensures your documentation will pass CI checks.

## Troubleshooting

### Import Errors

If you see import errors when building:
1. Ensure VeeDB is installed in development mode: `pip install -e .`
2. Install all required dependencies: `pip install dacite`
3. Check that all imports in the source code are working

### Underline Warnings

If you see "Title underline too short" warnings:
- Ensure the underline is at least as long as the title
- Use consistent underline characters for each heading level

### Duplicate Object Descriptions

If you see duplicate object warnings:
- Add `:no-index:` directive to one of the duplicate autodoc directives
- This is common when documenting the same method in multiple places
