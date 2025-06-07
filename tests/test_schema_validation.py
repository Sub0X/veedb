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
        self.cache_file = os.path.join(self.test_dir, "schema.json")
        self.cache = SchemaCache(cache_file=self.cache_file, ttl_hours=24)
        
        # Sample schema data
        self.sample_schema = {
            "endpoints": {
                "/vn": {
                    "fields": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "original": {"type": "string"},
                        "released": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "/character": {
                    "fields": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "original": {"type": "string"}
                    }
                }
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.test_dir)
    
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
    
    def test_cache_expiration(self):
        """Test cache expiration logic."""
        # Save schema
        self.cache.save_schema(self.sample_schema)
        
        # Should not be expired immediately
        self.assertFalse(self.cache.is_cache_expired())
        
        # Test with very short TTL
        short_ttl_cache = SchemaCache(cache_file=self.cache_file, ttl_hours=0.0001)  # ~0.36 seconds
        self.assertTrue(short_ttl_cache.is_cache_expired())
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # Save schema
        self.cache.save_schema(self.sample_schema)
        self.assertTrue(self.cache.is_cached())
        
        # Invalidate cache
        self.cache.invalidate_cache()
        self.assertFalse(self.cache.is_cached())
        self.assertFalse(os.path.exists(self.cache_file))
    
    @patch('aiohttp.ClientSession.get')
    async def test_download_schema(self, mock_get):
        """Test downloading schema from API."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=self.sample_schema)
        mock_response.raise_for_status = Mock()
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Create a mock client
        mock_client = Mock()
        mock_client._get_session.return_value = Mock()
        mock_client.base_url = "https://api.vndb.org/kana"
        
        # Download schema
        schema = await self.cache.get_schema(mock_client)
        
        self.assertEqual(schema, self.sample_schema)
        self.assertTrue(self.cache.is_cached())


class TestFilterValidator(unittest.TestCase):
    """Test cases for FilterValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.test_dir, "schema.json")
        self.validator = FilterValidator(SchemaCache(cache_file=self.cache_file))
        
        # Sample schema
        self.sample_schema = {
            "endpoints": {
                "/vn": {
                    "fields": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "original": {"type": "string"},
                        "released": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Save schema to cache
        self.validator.schema_cache.save_schema(self.sample_schema)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.test_dir)
    
    def test_extract_fields_simple(self):
        """Test extracting fields from simple schema."""
        fields = self.validator._extract_fields(self.sample_schema["endpoints"]["/vn"]["fields"])
        expected_fields = ["id", "title", "original", "released", "tags.name", "tags.category"]
        self.assertEqual(sorted(fields), sorted(expected_fields))
    
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
    
    def test_validate_field_reference(self):
        """Test field reference validation."""
        available_fields = ["id", "title", "original", "tags.name"]
        
        # Valid field
        errors, suggestions = self.validator._validate_field_reference("title", available_fields)
        self.assertEqual(errors, [])
        self.assertEqual(suggestions, [])
        
        # Invalid field
        errors, suggestions = self.validator._validate_field_reference("titl", available_fields)
        self.assertEqual(len(errors), 1)
        self.assertIn("title", suggestions)
        
        # Nested field
        errors, suggestions = self.validator._validate_field_reference("tags.name", available_fields)
        self.assertEqual(errors, [])
        self.assertEqual(suggestions, [])
    
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
        self.cache_file = os.path.join(self.test_dir, "schema.json")
        
        # Create client with test cache file
        self.client = VNDB()
        self.client._filter_validator = FilterValidator(SchemaCache(cache_file=self.cache_file))
        
        # Sample schema
        self.sample_schema = {
            "endpoints": {
                "/vn": {
                    "fields": {
                        "id": {"type": "string"},
                        "title": {"type": "string"}
                    }
                }
            }
        }
        
        # Save schema to cache
        self.client._filter_validator.schema_cache.save_schema(self.sample_schema)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.test_dir)
    
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
    
    async def test_entity_client_validation(self):
        """Test entity client validation methods."""
        # Test VN client validation
        result = await self.client.vn.validate_filters(["title", "=", "Test"])
        self.assertTrue(result['valid'])
        
        fields = await self.client.vn.get_available_fields()
        self.assertIn("title", fields)
    
    def test_cache_invalidation(self):
        """Test cache invalidation through client."""
        # Cache should exist
        self.assertTrue(self.client._filter_validator.schema_cache.is_cached())
        
        # Invalidate cache
        self.client.invalidate_schema_cache()
        
        # Cache should be gone
        self.assertFalse(self.client._filter_validator.schema_cache.is_cached())


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
