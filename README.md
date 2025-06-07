# VeeDB (Async)

An unofficial asynchronous Python wrapper for the [VNDB.org API v2 (Kana)](https://vndb.org/d11). "Vee" for the v-sign pose and starting letter for VNDB, "DB" for database.

This library provides a convenient way to interact with the VNDB API, allowing you to query visual novel data, manage user lists, and more, all asynchronously with comprehensive type safety and filter validation.

[![Documentation Status](https://readthedocs.org/projects/veedb/badge/?version=latest)](https://veedb.readthedocs.io/en/latest/?badge=latest)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg?logo=readthedocs&logoColor=white)](https://veedb.readthedocs.io/en/latest/index.html)

## Features

- **Asynchronous API calls** using `aiohttp`
- **Data parsing** into Python dataclasses using `dacite`
- **Comprehensive filter validation** with schema caching and auto-suggestions
- **Complete type safety** with full type annotations
- **Coverage for all VNDB API v2 endpoints**:
  - Simple GET requests: `/schema`, `/stats`, `/user`, `/authinfo`
  - Database querying (POST): `/vn`, `/release`, `/producer`, `/character`, `/staff`, `/tag`, `/trait`, `/quote`
  - List management: `/ulist` (query, labels), `/rlist`, including PATCH and DELETE operations
- **Intelligent query helpers** for constructing complex filter queries
- **Custom exceptions** for API errors with detailed error handling
- **API token authentication** support
- **Optional sandbox mode** for testing
- **Schema caching** with TTL support for optimal performance
- **Field suggestions** for misspelled or invalid field names

## Installation

```bash
pip install veedb
```

Alternatively, install directly from the repository:
```bash
pip install git+https://github.com/Sub0X/veedb.git
```

## Requirements

- Python 3.8+
- `aiohttp`
- `dacite`

## Documentation

📚 **Complete documentation is available at:** https://veedb.readthedocs.io/en/latest/index.html

[![Read the Docs](https://img.shields.io/badge/Read%20the%20Docs-Documentation-blue?style=for-the-badge&logo=readthedocs&logoColor=white)](https://veedb.readthedocs.io/en/latest/index.html)
[![API Reference](https://img.shields.io/badge/API-Reference-green?style=for-the-badge&logo=gitbook&logoColor=white)](https://veedb.readthedocs.io/en/latest/api/validation.html)
[![Quick Start](https://img.shields.io/badge/Quick-Start-orange?style=for-the-badge&logo=rocket&logoColor=white)](https://veedb.readthedocs.io/en/latest/quickstart.html)

The documentation includes:
- **Installation Guide** - Setup instructions and requirements
- **Quick Start Tutorial** - Get up and running in minutes
- **Authentication Guide** - API token setup and security best practices
- **Complete API Reference** - All classes, methods, and types
- **Examples & Use Cases** - Real-world usage patterns
- **Filter Validation** - Advanced querying and validation features

## Quick Start

### Basic Usage

```python
import asyncio
from veedb import VNDB, QueryRequest

async def main():
    async with VNDB() as client:
        # Get database statistics
        stats = await client.get_stats()
        print(f"Total VNs: {stats.vn}")

        # Query for visual novels
        query = QueryRequest(
            filters=["title", "~", "Fate"],
            fields="id, title, rating, released",
            sort="rating",
            reverse=True,
            results=5
        )
        
        response = await client.vn.query(query)
        
        for vn in response.results:
            print(f"{vn.title} ({vn.released}): {vn.rating}")

asyncio.run(main())
```

### With Authentication

```python
import os
from veedb import VNDB

async def authenticated_example():
    api_token = os.environ.get("VNDB_API_TOKEN")
    
    async with VNDB(api_token=api_token) as client:
        # Get user info
        auth_info = await client.get_authinfo()
        print(f"Logged in as: {auth_info.username}")
        
        # Access user lists and other authenticated features
        # ...

asyncio.run(authenticated_example())
```

### Filter Validation

One of VeeDB's key features is comprehensive filter validation:

```python
async def validation_example():
    async with VNDB() as client:
        # Validate filters before using them
        result = await client.validate_filters("/vn", ["title", "=", "Test"])
        
        if result['valid']:
            print("Filter is valid!")
        else:
            print(f"Errors: {result['errors']}")
            print(f"Suggestions: {result['suggestions']}")
        
        # Get available fields for an endpoint
        fields = await client.get_available_fields("/vn")
        print(f"Available VN fields: {fields[:10]}")

asyncio.run(validation_example())
```

- Python 3.8+
- `aiohttp`
- `dacite`

## Usage

First, you'll need to obtain an API token if you plan to use authenticated endpoints (like list management or accessing private user data). You can get a token from your VNDB profile under "Applications": [https://vndb.org/u/tokens](https://vndb.org/u/tokens)

It's recommended to store your API token as an environment variable (e.g., `VNDB_API_TOKEN`).

```python
import asyncio
import os
from veedb import VNDB, QueryRequest # Updated import
from veedb.exceptions import VNDBAPIError # Updated import

async def main():
    api_token = os.environ.get("VNDB_API_TOKEN")

    # Use use_sandbox=True for testing against the beta API endpoint
    async with VNDB(api_token=api_token, use_sandbox=True) as vndb: # Class name VNDB is kept
        try:
            # Get database statistics
            stats = await vndb.get_stats()
            print(f"Total VNs in database: {stats.vn}")

            # Query for a specific visual novel (e.g., Ever17)
            vn_query = QueryRequest(
                filters=["id", "=", "v17"],
                fields="id, title, released, rating, description, image.url"
            )
            response = await vndb.vn.query(vn_query)

            if response.results:
                ever17 = response.results[0]
                print(f"\nTitle: {ever17.title}")
                print(f"Released: {ever17.released}")
                print(f"Rating: {ever17.rating}")
                if ever17.image:
                    print(f"Image: {ever17.image.url}")
                # print(f"Description: {ever17.description[:200]}...") # Truncated
            else:
                print("VN v17 not found.")

            # Search for VNs
            search_query = QueryRequest(
                filters=["search", "=", "Steins;Gate"],
                fields="id, title, released",
                results=5,
                sort="rating",
                reverse=True # Highest rated first
            )
            search_response = await vndb.vn.query(search_query)
            print("\nTop Steins;Gate related VNs by rating:")
            for vn_item in search_response.results:
                print(f"- {vn_item.title} (ID: {vn_item.id}, Released: {vn_item.released})")

        except VNDBAPIError as e:
            print(f"An API error occurred: {e.status_code} - {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Querying Data

The primary way to fetch data from endpoints like `/vn`, `/release`, etc., is using the `query` method with a `QueryRequest` object.

```python
from veedb import QueryRequest # Updated import

# Fetch VNs released in 2023, sort by vote count, get titles and developer names
query = QueryRequest(
    filters=["released", ">=", "2023-01-01", "and", "released", "<=", "2023-12-31"],
    fields="id, title, votecount, developers{id, name}",
    sort="votecount",
    reverse=True,
    results=10,
    page=1,
    count=True # To get the total count of matching entries
)
response = await vndb.vn.query(query) # Assuming 'vndb' is an initialized VNDB client

print(f"Total VNs released in 2023: {response.count}")
for vn_entry in response.results:
    dev_names = [dev.name for dev in vn_entry.developers] if vn_entry.developers else []
    print(f"- {vn_entry.title} (Votes: {vn_entry.votecount}, Developers: {', '.join(dev_names)})")
```

Refer to the [VNDB API Documentation](https://vndb.org/d11) for details on:
- Available filters for each entity.
- Available fields for each entity (use dot notation for nested fields, e.g., `image.url`, `tags{id,name,rating}`).
- Sorting options.

### List Management

To manage user lists (ulist/rlist), you need an API token with `listwrite` permission.

```python
from veedb.types.requests import UlistUpdatePayload # Updated import

# Add/Update a VN in your ulist
# (Assuming 'vndb' is an initialized VNDB client with a valid token)
try:
    update_payload = UlistUpdatePayload(
        vote=85, # Vote 8.5
        notes="A masterpiece!",
        labels_set=[2] # Add to "Finished" label (assuming ID 2 is 'Finished')
    )
    await vndb.ulist.update_entry(vn_id="v17", payload=update_payload)
    print("Successfully updated v17 in ulist.")

except VNDBAPIError as e:
    print(f"Error managing ulist: {e}")
```

## Documentation

📚 **For comprehensive VeeDB documentation, visit:**

[![VeeDB Documentation](https://img.shields.io/badge/VeeDB-Documentation-blue?style=for-the-badge&logo=readthedocs&logoColor=white)](https://veedb.readthedocs.io/en/latest/index.html)

For detailed information on VNDB API filters, fields, and behavior, please refer to the official [VNDB API v2 (Kana) Documentation](https://vndb.org/d11).

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
