#!/usr/bin/env python3
"""
Tests for the schema validation system in veedb.

These tests cover:
- SchemaCache functionality
- FilterValidator functionality 
- Integration with VNDB client
- Edge cases and error handling
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from veedb.schema_validator import SchemaCache, FilterValidator
from veedb.client import VNDB


class TestSchemaCache(unittest.TestCase):
    """Test cases for SchemaCache class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_filename = "schema.json"  # Define cache_filename
        self.cache_file = os.path.join(self.test_dir, self.cache_filename) # Keep for tearDown
        self.cache = SchemaCache(cache_dir=self.test_dir, cache_filename=self.cache_filename, ttl_hours=24)
          # Sample schema data
        self.sample_schema = {
            "api_fields": {
                "/vn": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "original": {"type": "string"},
                    "released": {"type": "string"},
                    "tags": {
                        "name": {"type": "string"},
                        "category": {"type": "string"}
                    }
                },
                "/character": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "original": {"type": "string"}
                }
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_cache_file_creation(self):
        """Test that cache file is created correctly."""
        self.assertFalse(self.cache.is_cached())
        
        # Save schema
        self.cache.save_schema(self.sample_schema)
        self.assertTrue(self.cache.is_cached())
        self.assertTrue(os.path.exists(self.cache_file))
    
    def test_schema_save_and_load(self):
        """Test saving and loading schema."""
        # Save schema
        self.cache.save_schema(self.sample_schema)
        
        # Load schema
        loaded_schema = self.cache.load_schema()
        self.assertEqual(loaded_schema, self.sample_schema)
    
    @patch('os.path.getmtime')
    @patch('time.time')
    def test_cache_expiration(self, mock_time, mock_getmtime):
        """Test cache expiration logic."""
        initial_time = 1700000000.0
        
        # This map will store the "mocked" modification times for specific file paths
        mtime_map = {}

        def side_effect_getmtime(path_arg):
            # Return the mocked mtime if the path is in our map, otherwise fallback (e.g., to initial_time or raise error)
            # For this test, we expect queries only for files we explicitly save.
            if path_arg in mtime_map:
                return mtime_map[path_arg]
            # Fallback for unexpected paths, can be made stricter if needed
            # print(f"Warning: os.path.getmtime called for unexpected path: {path_arg} in test_cache_expiration")
            return initial_time 

        mock_getmtime.side_effect = side_effect_getmtime

        # --- Part 1: Main cache instance (self.cache) ---
        mock_time.return_value = initial_time
        
        # Ensure the cache file for this specific test instance is clean before starting
        cache_file_path_str = str(self.cache.cache_file)
        if os.path.exists(cache_file_path_str):
            os.remove(cache_file_path_str)

        # When save_schema is called, its mtime should be initial_time
        mtime_map[cache_file_path_str] = initial_time
        self.cache.save_schema(self.sample_schema)
        
        self.assertFalse(self.cache.is_cache_expired(), "Cache should not be expired immediately after saving")
        
        mock_time.return_value = initial_time + (self.cache.ttl_seconds / 2)
        self.assertFalse(self.cache.is_cache_expired(), "Cache should not be expired when half of TTL has passed")
        
        mock_time.return_value = initial_time + self.cache.ttl_seconds + 1
        self.assertTrue(self.cache.is_cache_expired(), "Cache should be expired when TTL has passed")

        # --- Part 2: Short TTL cache instance ---
        short_ttl_cache_filename = "short_lived_schema.json"
        short_ttl_cache = SchemaCache(cache_dir=self.test_dir, cache_filename=short_ttl_cache_filename, ttl_hours=0.0001)
        short_ttl_cache_file_path_str = str(short_ttl_cache.cache_file)
        
        if os.path.exists(short_ttl_cache_file_path_str):
            os.remove(short_ttl_cache_file_path_str)
            
        mock_time.return_value = initial_time # Reset time for this new cache instance's save operation
        mtime_map[short_ttl_cache_file_path_str] = initial_time # Its mtime should be initial_time upon saving
        short_ttl_cache.save_schema(self.sample_schema)
        
        mock_time.return_value = initial_time + short_ttl_cache.ttl_seconds + 1 
        self.assertTrue(short_ttl_cache.is_cache_expired(), "Short TTL cache should be expired after its TTL + 1s")
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # Save schema
        self.cache.save_schema(self.sample_schema)
        self.assertTrue(self.cache.is_cached())
        
        # Invalidate cache
        self.cache.invalidate_cache()
        self.assertFalse(self.cache.is_cached())
        self.assertFalse(os.path.exists(self.cache_file))
    
    @patch('veedb.methods.fetch._fetch_api')
    async def test_download_schema(self, mock_fetch_api):
        """Test downloading schema from API."""
        # Mock the fetch API call
        mock_fetch_api.return_value = self.sample_schema
        
        # Create a mock client
        mock_client = Mock()
        mock_client.base_url = "https://api.vndb.org/kana"
        mock_client.api_token = None
        
        # Download schema
        schema = await self.cache.get_schema(mock_client)
        
        self.assertEqual(schema, self.sample_schema)
        self.assertTrue(self.cache.is_cached())


class TestFilterValidator(unittest.TestCase):
    """Test cases for FilterValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.test_dir, "schema_cache.json")
        # Pass cache_dir and cache_filename to SchemaCache constructor
        self.schema_cache = SchemaCache(cache_dir=self.test_dir, cache_filename="schema_cache.json")
        self.validator = FilterValidator(schema_cache=self.schema_cache)
          # Updated sample_schema structure to match schema.example.json (using 'api_fields')
        self.sample_schema = {
            "api_fields": {
                "/vn": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "original": {"type": "string"},
                    "released": {"type": "string"},
                    "tags": {
                        "name": {"type": "string"},
                        "category": {"type": "string"}
                    }
                }            }
        }
        
        # Save schema to cache
        self.validator.schema_cache.save_schema(self.sample_schema)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_extract_fields_simple(self):
        """Test extracting fields from simple schema."""
        # _extract_fields now expects the schema to contain 'api_fields' at the top level.
        fields = self.validator._extract_fields(self.sample_schema, "/vn")
        expected_fields = sorted([
            "id", "id.type", 
            "title", "title.type",
            "original", "original.type", 
            "released", "released.type", 
            "tags", "tags.name", "tags.name.type", "tags.category", "tags.category.type"
        ])
        self.assertEqual(sorted(fields), expected_fields)
    
    def test_suggest_fields(self):
        """Test field suggestion functionality."""
        available_fields = ["title", "original", "released"]
        
        # Test exact match
        suggestions = self.validator.suggest_fields("title", available_fields)
        self.assertEqual(suggestions, ["title"])
        
        # Test similar field
        suggestions = self.validator.suggest_fields("titl", available_fields)
        self.assertIn("title", suggestions)
        
        # Test no matches
        suggestions = self.validator.suggest_fields("xyz", available_fields)
        self.assertEqual(suggestions, [])
    
    # def test_validate_field_reference(self):
    #     """Test field reference validation."""
    #     available_fields = ["id", "title", "original", "tags.name"]
    #     
    #     # Valid field
    #     # The _validate_field_reference method was internal and has been refactored.
    #     # This logic is now part of the main validate_filters method.
    #     # Consider testing this through validate_filters if specific unit tests are needed.
    #     # For now, commenting out as it will fail due to AttributeError.
    #     # errors, suggestions = self.validator._validate_field_reference("title", available_fields)
    #     # self.assertEqual(errors, [])
    #     # self.assertEqual(suggestions, [])
    #     # 
    #     # # Invalid field
    #     # errors, suggestions = self.validator._validate_field_reference("titl", available_fields)
    #     # self.assertEqual(len(errors), 1)
    #     # self.assertIn("title", suggestions)
    #     # 
    #     # # Nested field
    #     # errors, suggestions = self.validator._validate_field_reference("tags.name", available_fields)
    #     # self.assertEqual(errors, [])
    #     # self.assertEqual(suggestions, [])
    
    async def test_get_available_fields(self):
        """Test getting available fields for an endpoint."""
        mock_client = Mock()
        mock_client._get_session.return_value = Mock()
        mock_client.base_url = "https://api.vndb.org/kana"
        
        fields = await self.validator.get_available_fields("/vn", mock_client)
        expected_fields = ["id", "title", "original", "released", "tags.name", "tags.category"]
        self.assertEqual(sorted(fields), sorted(expected_fields))
    
    async def test_validate_filters_simple(self):
        """Test validating simple filters."""
        mock_client = Mock()
        mock_client._get_session.return_value = Mock()
        mock_client.base_url = "https://api.vndb.org/kana"
        
        # Valid filter
        result = await self.validator.validate_filters("/vn", ["title", "=", "Test"], mock_client)
        self.assertTrue(result['valid'])
        self.assertEqual(result['errors'], [])
        
        # Invalid filter
        result = await self.validator.validate_filters("/vn", ["titl", "=", "Test"], mock_client)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("title", result['suggestions'])
    
    async def test_validate_filters_complex(self):
        """Test validating complex nested filters."""
        mock_client = Mock()
        mock_client._get_session.return_value = Mock()
        mock_client.base_url = "https://api.vndb.org/kana"
        
        # Valid complex filter
        complex_filter = [
            "and",
            ["title", "~", "test"],
            ["or", ["id", "=", "v123"], ["original", "~", "original"]]
        ]
        result = await self.validator.validate_filters("/vn", complex_filter, mock_client)
        self.assertTrue(result['valid'])
        
        # Invalid complex filter
        invalid_complex_filter = [
            "and",
            ["titl", "~", "test"],  # typo
            ["invalid_field", "=", "value"]  # invalid field
        ]
        result = await self.validator.validate_filters("/vn", invalid_complex_filter, mock_client)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 1)  # Should have multiple errors


class TestVNDBClientIntegration(unittest.TestCase):
    """Test integration with VNDB client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_filename = "schema.json" # Define cache_filename
        self.cache_file = os.path.join(self.test_dir, self.cache_filename) # Keep for tearDown
        
        # Create client with test cache file
        self.client = VNDB()
        schema_cache = SchemaCache(cache_dir=self.test_dir, cache_filename=self.cache_filename)
        self.client._filter_validator = FilterValidator(schema_cache)
        self.client._schema_cache_instance = schema_cache  # Ensure both use the same cache instance
        
        # Sample schema
        self.sample_schema = {
            "api_fields": {
                "/vn": {
                    "id": {"type": "string"},
                    "title": {"type": "string"}
                }
            }
        }
        
        # Save schema to cache
        self.client._filter_validator.schema_cache.save_schema(self.sample_schema)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    async def test_client_validate_filters(self):
        """Test client filter validation methods."""
        # Valid filter
        result = await self.client.validate_filters("/vn", ["title", "=", "Test"])
        self.assertTrue(result['valid'])
        
        # Invalid filter
        result = await self.client.validate_filters("/vn", ["titl", "=", "Test"])
        self.assertFalse(result['valid'])
    
    async def test_client_get_available_fields(self):
        """Test client get available fields method."""
        fields = await self.client.get_available_fields("/vn")
        self.assertIn("id", fields)
        self.assertIn("title", fields)
    
    @patch('time.time') # Add patch for time.time here as well for consistency if client actions involve time checks
    def test_cache_invalidation(self, mock_time):
        """Test cache invalidation through client."""
        # Ensure a known state for time, in case any underlying cache logic uses it implicitly
        mock_time.return_value = 1700000000.0

        # Ensure the cache file exists before invalidation by saving it if it doesn't
        # This makes the test more robust to the order of execution or previous states.
        if not self.client._filter_validator.schema_cache.is_cached():
            self.client._filter_validator.schema_cache.save_schema(self.sample_schema)

        # Cache should exist
        self.assertTrue(self.client._filter_validator.schema_cache.is_cached(), "Cache should exist before invalidation")
        
        # Invalidate cache
        self.client.invalidate_schema_cache()
        
        # Cache should be gone
        self.assertFalse(self.client._filter_validator.schema_cache.is_cached(), "Cache should not exist after invalidation")


def run_async_test(test_func):
    """Helper function to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()


if __name__ == "__main__":
    # Convert async tests to sync for unittest
    test_cases = [
        TestSchemaCache,
        TestFilterValidator, 
        TestVNDBClientIntegration
    ]
    
    for test_case in test_cases:
        # Convert async test methods to sync
        for attr_name in dir(test_case):
            attr = getattr(test_case, attr_name)
            if (attr_name.startswith('test_') and 
                asyncio.iscoroutinefunction(attr)):
                setattr(test_case, attr_name, 
                       lambda self, func=attr: run_async_test(lambda: func(self)))
    
    unittest.main()
