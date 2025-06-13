#!/usr/bin/env python3
"""
Example demonstrating how to get schema enums with caching.
The schema is cached for 15 days to avoid unnecessary API calls.
"""

import asyncio
from veedb import VNDB

async def main():
    async with VNDB() as client:
        print("Fetching VNDB schema enums (cached for 15 days)...")
        
        # Get all enums from the schema
        enums = await client.get_enums()
        
        print(f"\nFound {len(enums)} enum types:")
        for enum_name in enums.keys():
            print(f"  - {enum_name}")
        
        # Example: Show language enum values
        if 'language' in enums:
            languages = enums['language']
            print(f"\nLanguage enum has {len(languages)} values:")
            for lang in languages[:5]:  # Show first 5
                print(f"  {lang['id']}: {lang['label']}")
            if len(languages) > 5:
                print(f"  ... and {len(languages) - 5} more")
        
        # Example: Show platform enum values
        if 'platform' in enums:
            platforms = enums['platform']
            print(f"\nPlatform enum has {len(platforms)} values:")
            for platform in platforms[:5]:  # Show first 5
                print(f"  {platform['id']}: {platform['label']}")
            if len(platforms) > 5:
                print(f"  ... and {len(platforms) - 5} more")

if __name__ == "__main__":
    asyncio.run(main())
