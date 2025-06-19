#!/usr/bin/env python3
"""
Test script to verify the recursion fix for schema caching.
This script tests all the schema-related functionality to ensure no recursion occurs.
"""

import asyncio
import sys
import traceback
from veedb import VNDB, QueryRequest

async def test_comprehensive_schema():
    """Test all schema-related functionality to ensure no recursion."""
    print("🧪 Testing comprehensive schema functionality...")
    
    try:
        async with VNDB(use_sandbox=False) as vndb:
            print("\n1. Testing get_schema()...")
            schema = await vndb.get_schema()
            print(f"   ✅ Schema retrieved with keys: {list(schema.keys())}")
            
            print("\n2. Testing get_enums()...")
            enums = await vndb.get_enums()
            print(f"   ✅ Found {len(enums)} enum types: {list(enums.keys())}")
            
            print("\n3. Testing filter validation (uses schema)...")
            validation = await vndb.validate_filters('/vn', ['title', '=', 'test'])
            print(f"   ✅ Filter validation successful: {validation.get('valid', False)}")
            
            print("\n4. Testing get_available_fields (uses schema)...")
            fields = await vndb.get_available_fields('/vn')
            print(f"   ✅ Found {len(fields)} available fields for /vn")
            
            print("\n5. Testing VN query (autocomplete scenario)...")
            search_req = QueryRequest(
                filters=['search', '=', 'fate'],
                results=3,
                fields='id, title, released, olang'
            )
            results = await vndb.vn.query(search_req)
            print(f"   ✅ VN search successful: {len(results.results)} results")
            
            print("\n6. Testing language enum (Discord autocomplete scenario)...")
            languages = enums.get('language', [])
            filtered_langs = [
                lang for lang in languages 
                if 'en' in lang['label'].lower() or lang['id'].startswith('en')
            ][:5]
            print(f"   ✅ Language filtering successful: {len(filtered_langs)} matching languages")
            
            print("\n🎉 All tests passed! No recursion detected.")
            return True
            
    except RecursionError as e:
        print(f"\n❌ RECURSION ERROR DETECTED!")
        print(f"Error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ OTHER ERROR: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("VeeDB Schema Recursion Fix Test")
    print("=" * 40)
    
    success = await test_comprehensive_schema()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Schema caching works correctly!")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED - Check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
