#!/usr/bin/env python3
"""
Example demonstrating how to use the filter validation system in veedb.

This example shows how to:
1. Validate filters before making API calls
2. Get available fields for an endpoint
3. Handle validation errors and suggestions
4. Use the validation system to improve your queries
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from veedb import VNDB, FilterValidator, SchemaCache


async def main():
    # Initialize the VNDB client
    client = VNDB()
    
    print("=== VNDB Filter Validation Example ===\n")
    
    # Example 1: Basic filter validation
    print("1. Basic Filter Validation")
    print("-" * 30)
    
    # Valid filter
    valid_filter = ["id", "=", "v123"]
    result = await client.validate_filters("/vn", valid_filter)
    print(f"Valid filter {valid_filter}: {result['valid']}")
    
    # Invalid filter with typo
    invalid_filter = ["titl", "=", "Test"]  # 'titl' should be 'title'
    result = await client.validate_filters("/vn", invalid_filter)
    print(f"Invalid filter {invalid_filter}: {result['valid']}")
    if not result['valid']:
        print(f"  Errors: {result['errors']}")
        print(f"  Suggestions: {result['suggestions']}")
    print()
    
    # Example 2: Get available fields for an endpoint
    print("2. Available Fields")
    print("-" * 18)
    
    fields = await client.get_available_fields("/vn")
    print(f"Available fields for /vn (first 10): {fields[:10]}")
    print(f"Total fields available: {len(fields)}")
    print()
    
    # Example 3: Complex filter validation
    print("3. Complex Filter Validation")
    print("-" * 27)
    
    complex_filter = [
        "and",
        ["title", "~", "fate"],
        ["or", 
         ["released", ">", "2020-01-01"],
         ["tags.name", "=", "Romance"]
        ]
    ]
    result = await client.validate_filters("/vn", complex_filter)
    print(f"Complex filter validation: {result['valid']}")
    if not result['valid']:
        print(f"  Errors: {result['errors']}")
        print(f"  Suggestions: {result['suggestions']}")
    print()
    
    # Example 4: Using validation in individual endpoint clients
    print("4. Endpoint-Specific Validation")
    print("-" * 29)
    
    # Validate filters for VN endpoint specifically
    vn_filter = ["original", "~", "visual novel"]
    vn_result = await client.vn.validate_filters(vn_filter)
    print(f"VN filter {vn_filter}: {vn_result['valid']}")
    
    # Get available fields for character endpoint
    char_fields = await client.character.get_available_fields()
    print(f"Character endpoint fields (first 5): {char_fields[:5]}")
    print()
    
    # Example 5: List all available endpoints
    print("5. Available Endpoints")
    print("-" * 20)
    
    endpoints = await client.list_endpoints()
    print(f"Available API endpoints: {endpoints}")
    print()
    
    # Example 6: Direct validator usage
    print("6. Direct Validator Usage")
    print("-" * 24)
    
    # You can also use the validator directly
    validator = FilterValidator()
    
    # Validate without a client (will download schema if needed)
    direct_result = await validator.validate_filters("/release", ["id", "=", "r123"], client)
    print(f"Direct validation result: {direct_result['valid']}")
    
    # Get suggestions for a misspelled field
    suggestions = validator.suggest_fields("titl", ["title", "original", "aliases"])
    print(f"Suggestions for 'titl': {suggestions}")
    print()
    
    # Example 7: Schema cache management
    print("7. Schema Cache Management")
    print("-" * 25)
    
    schema_cache = SchemaCache()
    print(f"Schema cache file: {schema_cache.cache_file}")
    print(f"Schema cached: {schema_cache.is_cached()}")
    
    if schema_cache.is_cached():
        print(f"Cache age: {schema_cache.get_cache_age():.2f} hours")
        print(f"Cache expired: {schema_cache.is_cache_expired()}")
      # Invalidate cache if needed
    # schema_cache.invalidate_cache()
    # print("Cache invalidated")
    print()
    
    print("=== Validation Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
