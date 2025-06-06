# tests/test_veedb.py
import asyncio
import os
import sys

# This script assumes it's in a 'tests' directory, and the 'veedb' package is in a sibling 'src' directory.
# E.g., /project_root/src/veedb and /project_root/tests/test_veedb.py
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(current_dir), "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
except NameError:
    # __file__ is not defined in some environments (e.g. interactive interpreters)
    # Assume the current working directory is the project root.
    src_dir = os.path.abspath("src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


from veedb import VNDB, QueryRequest
from veedb.exceptions import VNDBAPIError, AuthenticationError
from veedb.apitypes.common import VNDBID
from veedb.apitypes.requests import UlistUpdatePayload


# --- Individual Test Functions ---

async def test_get_stats(vndb: VNDB):
    """Test 1: GET /stats (Unauthenticated)"""
    print("\n[Test 1: GET /stats]")
    try:
        stats = await vndb.get_stats()
        print(
            f"  SUCCESS: Fetched stats. Total VNs: {stats.vn}, Total Chars: {stats.chars}"
        )
        assert stats.vn > 0, "Expected positive number of VNs"
    except VNDBAPIError as e:
        print(f"  ERROR fetching stats: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR fetching stats: {e}")


async def test_get_schema(vndb: VNDB):
    """Test 2: GET /schema (Unauthenticated)"""
    print("\n[Test 2: GET /schema]")
    try:
        schema = await vndb.get_schema()
        print(
            f"  SUCCESS: Fetched schema. Found API fields for /vn: {'/vn' in schema.get('api_fields', {})}"
        )
        assert "/vn" in schema.get(
            "api_fields", {}
        ), "Schema should contain /vn fields"
    except VNDBAPIError as e:
        print(f"  ERROR fetching schema: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR fetching schema: {e}")


async def test_get_user(vndb: VNDB):
    """Test 3: GET /user (Unauthenticated, public user)"""
    USER_ID: VNDBID = "u286975"
    print(f"\n[Test 3: GET /user?q={USER_ID}]")
    try:
        user_info_dict = await vndb.get_user(
            q=USER_ID, fields="lengthvotes,lengthvotes_sum"
        )
        user_info = user_info_dict.get(USER_ID)
        if user_info:
            print(
                f"  SUCCESS: Fetched user '{user_info.username}' (ID: {user_info.id})"
            )
            assert user_info.id == USER_ID
        else:
            print(
                f"  ERROR: User {USER_ID} not found or error in response structure."
            )
    except VNDBAPIError as e:
        print(f"  ERROR fetching user: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR fetching user: {e}")


async def test_query_vn(vndb: VNDB):
    """Test 4: Query VN (Unauthenticated)"""
    VN_ID: VNDBID = "v52702"
    print(f"\n[Test 4: POST /vn (Query for {VN_ID})]")
    try:
        vn_query = QueryRequest(
            filters=["id", "=", VN_ID],
            fields="id,title,released,rating,platforms",
            results=1,
        )
        response = await vndb.vn.query(vn_query)
        if response.results:
            vn = response.results[0]
            print(
                f"  SUCCESS: Fetched VN '{vn.title}' (ID: {vn.id}), Released: {vn.released}, Rating: {vn.rating}, Platforms: {vn.platforms}"
            )
            assert vn.id == VN_ID
        else:
            print(f"  ERROR: VN {VN_ID} not found via query.")
    except VNDBAPIError as e:
        print(f"  ERROR querying VN: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR querying VN: {e}")


async def test_get_authinfo(vndb: VNDB, api_token: str | None):
    """Test 5: GET /authinfo (Authenticated - requires token)"""
    print("\n[Test 5: GET /authinfo (Requires API Token)]")
    if api_token:
        try:
            auth_info = await vndb.get_authinfo()
            print(
                f"  SUCCESS: Fetched auth info for user '{auth_info.username}' (ID: {auth_info.id}). Permissions: {auth_info.permissions}"
            )
            assert auth_info.id is not None
        except AuthenticationError as e:
            print(
                f"  AUTHENTICATION ERROR (as expected if token is invalid/missing permissions): {e}"
            )
        except VNDBAPIError as e:
            print(f"  ERROR fetching authinfo: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR fetching authinfo: {e}")
    else:
        print("  SKIPPED: API_TOKEN not provided.")


async def test_patch_ulist(vndb: VNDB, api_token: str | None):
    """Test 6: Attempting a ulist operation (PATCH) - requires token with listwrite"""
    print("\n[Test 6: PATCH /ulist/v1 (Requires API Token with listwrite)]")
    if api_token:
        print("  NOTE: This test would typically modify data. For this quick test,")
        print(
            "        it primarily checks if the call can be made or fails gracefully."
        )
        payload = UlistUpdatePayload(notes="Quick test entry.")
        try:
            print("  SIMULATING: Call to ulist.update_entry would be made here.")
            print("  If your token has 'listwrite', this would attempt an update.")
            print(
                "  If not, an AuthenticationError or other API error is expected if the call was real."
            )
            # await vndb.ulist.update_entry("v1", payload)
        except AuthenticationError as e:
            print(
                f"  AUTHENTICATION ERROR (as expected if token lacks listwrite): {e}"
            )
        except VNDBAPIError as e:
            print(f"  API ERROR during ulist update attempt: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR during ulist update attempt: {e}")
    else:
        print("  SKIPPED: API_TOKEN not provided for ulist update.")


async def test_query_character_by_id(vndb: VNDB):
    """Test 7a: POST /character (Query for ID)"""
    char_id: VNDBID = "c5"
    print(f"\n[Test 7a: POST /character (Query for ID {char_id})]")
    try:
        char_query = QueryRequest(
            filters=["id", "=", char_id],
            fields="id,name,original,blood_type,birthday,vns{id,title,role}",
            results=1,
        )
        response = await vndb.character.query(char_query)
        if response.results:
            character = response.results[0]
            print(
                f"  SUCCESS: Fetched Character '{character.name}' (ID: {character.id})"
            )
            print(f"    Original Name: {character.original}")
            print(
                f"    Blood Type: {character.blood_type}, Birthday: {character.birthday}"
            )
            if character.vns:
                vn_link = character.vns[0]
                print(f"    Appears in: {vn_link.title} (ID: {vn_link.id}), Role: {vn_link.role}")
            assert character.id == char_id
        else:
            print(f"  ERROR: Character {char_id} not found.")
    except VNDBAPIError as e:
        print(f"  ERROR querying character by ID: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR querying character by ID: {e}")


async def test_search_character_by_name(vndb: VNDB):
    """Test 7b: POST /character (Search for name)"""
    char_search_name = "Okabe"
    print(f"\n[Test 7b: POST /character (Search for name '{char_search_name}')]")
    try:
        char_query = QueryRequest(
            filters=["search", "=", char_search_name],
            fields="id,name,original",
            results=3,
        )
        response = await vndb.character.query(char_query)
        if response.results:
            print(
                f"  SUCCESS: Found {len(response.results)} character(s) for search '{char_search_name}':"
            )
            for char_item in response.results:
                print(
                    f"    - {char_item.name} (Original: {char_item.original}, ID: {char_item.id})"
                )
            assert len(response.results) > 0
        else:
            print(f"  No characters found for search '{char_search_name}'.")
    except VNDBAPIError as e:
        print(f"  ERROR searching characters: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR searching characters: {e}")


async def test_get_characters_from_vn(vndb: VNDB):
    """Test 7c: Get all characters from a specific VN"""
    VN_ID: VNDBID = "v52702"
    print(f"\n[Test 7c: POST /character (Get characters from VN {VN_ID})]")
    try:
        char_query = QueryRequest(
            filters=["vn", "=", ["id", "=", VN_ID]],
            fields="id,name,original,vns{role}",
            results=10,
            sort="id",
        )
        response = await vndb.character.query(char_query)
        if response.results:
            print(
                f"  SUCCESS: Found {len(response.results)} character(s) from VN {VN_ID} (showing up to 10):"
            )
            for char_item in response.results:
                role = "N/A"
                if char_item.vns:
                    for vn_link in char_item.vns:
                        if vn_link.id == VN_ID:
                            role = vn_link.role
                            break
                print(
                    f"    - {char_item.name} | {char_item.original} (ID: {char_item.id}), Role: {role}"
                )
            assert len(response.results) > 0
        else:
            print(f"  No characters found for VN {VN_ID}.")
    except VNDBAPIError as e:
        print(f"  ERROR fetching characters from VN: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR fetching characters from VN: {e}")


async def test_query_ulist(vndb: VNDB):
    """Test 8: Ulist Endpoint Test"""
    ulist_user_id: VNDBID = "u286975"
    print(f"\n[Test 8: POST /ulist (Query for user {ulist_user_id})]")
    try:
        ulist_query = QueryRequest(
            fields="id,vote,vn{id,title,rating},labels{id,label}",
            sort="vote",
            reverse=True,
            results=5,
        )
        response = await vndb.ulist.query(
            user_id=ulist_user_id, query_options=ulist_query
        )

        if response.results:
            print(
                f"  SUCCESS: Fetched {len(response.results)} ulist entries for user {ulist_user_id}."
            )
            for item in response.results:
                vn_details = item.vn or {}
                labels_str = ", ".join([f"{lbl.label}({lbl.id})" for lbl in item.labels]) if item.labels else "None"
                print(
                    f"    - VN: {vn_details.get('title', 'N/A')} (Vote: {item.vote}, Labels: [{labels_str}])"
                )
        else:
            print(
                f"  No ulist entries found for user {ulist_user_id} with the given query."
            )
    except VNDBAPIError as e:
        print(f"  ERROR fetching ulist for {ulist_user_id}: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR fetching ulist for {ulist_user_id}: {e}")


# --- Main Test Runner ---

async def main():
    """
    Main function to initialize the client and run all test functions.
    """
    print("Starting Veedb Quick Test...\n")

    api_token = os.environ.get("VNDB_API_TOKEN")
    use_sandbox = False

    print(f"Using Sandbox: {use_sandbox}")
    if api_token:
        print("API Token found in environment variables.")
    else:
        print("API Token NOT found. Authenticated tests will be skipped or may fail.")
    print("-" * 30)

    async with VNDB(api_token=api_token, use_sandbox=use_sandbox) as vndb:
        await test_get_stats(vndb)
        await test_get_schema(vndb)
        await test_get_user(vndb)
        await test_query_vn(vndb)
        await test_get_authinfo(vndb, api_token)
        await test_patch_ulist(vndb, api_token)

        # Character tests
        await test_query_character_by_id(vndb)
        await test_search_character_by_name(vndb)
        await test_get_characters_from_vn(vndb)

        # Ulist test
        await test_query_ulist(vndb)

    print("\n" + "-" * 30)
    print("Quick Test Finished.")


if __name__ == "__main__":
    asyncio.run(main())