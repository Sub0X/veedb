# src/veedb/quick_test.py
import asyncio
import os
import sys

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)  # src dir
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


from veedb import VNDB, QueryRequest
from veedb.exceptions import VNDBAPIError, AuthenticationError
from veedb.apitypes.common import VNDBID


async def run_tests():
    """
    Runs a series of quick tests for the Veedb.
    """
    print("Starting Veedb Quick Test...\n")

    api_token = os.environ.get("VNDB_API_TOKEN")
    use_sandbox = False  # Always use sandbox for automated/quick tests unless specifically testing live

    print(f"Using Sandbox: {use_sandbox}")
    if api_token:
        print("API Token found in environment variables.")
    else:
        print("API Token NOT found. Authenticated tests will be skipped or may fail.")
    print("-" * 30)

    async with VNDB(api_token=api_token, use_sandbox=use_sandbox) as vndb:
        # Test 1: Get Stats (Unauthenticated)
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

        # Test 2: Get Schema (Unauthenticated)
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

        # Test 3: Get User (Unauthenticated, public user)
        USER = f"u{286975}"
        print(f"\n[Test 3: GET /user?q={USER}]")
        try:
            user_id_to_query: VNDBID = USER  # User 'Multi'
            user_info_dict = await vndb.get_user(
                q=user_id_to_query, fields="lengthvotes,lengthvotes_sum"
            )
            user_info = user_info_dict.get(user_id_to_query)
            if user_info:
                print(
                    f"  SUCCESS: Fetched user '{user_info.username}' (ID: {user_info.id})"
                )
                assert user_info.id == user_id_to_query
            else:
                print(
                    f"  ERROR: User {user_id_to_query} not found or error in response structure."
                )
        except VNDBAPIError as e:
            print(f"  ERROR fetching user: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR fetching user: {e}")

        # Test 4: Query VN (Unauthenticated)
        VN_ID = "52702"
        print(f"\n[Test 4: POST /vn (Query for v{VN_ID})]")
        try:
            vn_query = QueryRequest(
                filters=["id", "=", f"v{VN_ID}"],
                fields="id,title,released,rating,platforms",
                results=1,
            )
            response = await vndb.vn.query(vn_query)
            if response.results:
                VN = response.results[0]
                print(
                    f"  SUCCESS: Fetched VN '{VN.title}' (ID: {VN.id}), Released: {VN.released}, Rating: {VN.rating}, Platforms: {VN.platforms}"
                )
                assert VN.id == f"v{VN_ID}"
            else:
                print(f"  ERROR: VN v{VN_ID} not found via query.")
        except VNDBAPIError as e:
            print(f"  ERROR querying VN: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR querying VN: {e}")

        # Test 5: Get AuthInfo (Authenticated - requires token)
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

        # Test 6: Attempting a ulist operation (PATCH) - requires token with listwrite
        # This is more of a placeholder as it modifies data and needs careful handling
        # For a quick test, we'll just see if it raises AuthenticationError if no token
        print("\n[Test 6: PATCH /ulist/v1 (Requires API Token with listwrite)]")
        if api_token:
            # This test would ideally mock the API or use a dedicated test user/VN
            # For now, we're just checking the call structure and auth handling
            print("  NOTE: This test would typically modify data. For this quick test,")
            print(
                "        it primarily checks if the call can be made or fails gracefully."
            )
            from veedb.apitypes.requests import UlistUpdatePayload

            payload = UlistUpdatePayload(notes="Quick test entry.")
            try:
                # Using a non-critical VN ID like 'v1' for a test.
                # BE CAREFUL if running against the live API with a real token.
                # await vndb.ulist.update_entry("v1", payload)
                # print(f"  SUCCESS (or operation attempted) for ulist update on v1.")
                # For safety in a quick test, we'll just simulate the call or expect it to fail without listwrite
                print("  SIMULATING: Call to ulist.update_entry would be made here.")
                print("  If your token has 'listwrite', this would attempt an update.")
                print(
                    "  If not, an AuthenticationError or other API error is expected if the call was real."
                )

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

            # Test 7: Character Endpoint Tests
        char_id_for_test_7a: VNDBID = "c5"  # Takeshi Kuranari from Ever17 (v17)
        print(f"\n[Test 7a: POST /character (Query for ID {char_id_for_test_7a})]")
        try:
            char_query_by_id = QueryRequest(
                filters=["id", "=", char_id_for_test_7a],
                fields="id,name,original,blood_type,birthday,vns{id,title,role}",  # Request some VN info
                results=1,
            )
            response = await vndb.character.query(char_query_by_id)
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
                    print(f"    Appears in (showing first if multiple):")
                    for vn_link in character.vns[:1]:  # Show details for one VN link
                        # vn_link.id is the VN's ID from the CharacterVNLink
                        # vn_link.title and vn_link.role are fields populated if requested in vns{...}
                        print(
                            f"      - VN '{vn_link.title if vn_link.title else 'N/A'}' (ID: {vn_link.id}), Role: {vn_link.role}"
                        )
                assert character.id == char_id_for_test_7a
            else:
                print(f"  ERROR: Character {char_id_for_test_7a} not found.")
        except VNDBAPIError as e:
            print(f"  ERROR querying character by ID: {e}")
        except AssertionError as e:
            print(f"  ASSERTION ERROR querying character by ID: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR querying character by ID: {e}")

        char_search_name = "Okabe"
        print(f"\n[Test 7b: POST /character (Search for name '{char_search_name}')]")
        try:
            char_query_by_search = QueryRequest(
                filters=["search", "=", char_search_name],
                fields="id,name,original",
                results=3,  # Get a few results
            )
            response = await vndb.character.query(char_query_by_search)
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
            print(f"  More results available for search: {response.more}")
        except VNDBAPIError as e:
            print(f"  ERROR searching characters: {e}")
        except AssertionError as e:
            print(f"  ASSERTION ERROR searching characters: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR searching characters: {e}")

        # Test 7c: Get all characters from a specific VN
        print(f"\n[Test 7c: POST /character (Get characters from VN {VN_ID})]")
        try:
            # The 'vn' filter for characters takes VN filters.
            # Here, we filter for characters linked to VN with id vn_id_for_chars.
            char_from_vn_query = QueryRequest(
                filters=["vn", "=", ["id", "=", VN_ID]],
                fields="id,name,original,age,description,vns{role},sex,gender,description",  # Get role in this specific VN
                results=10,  # Fetch up to 10 characters for the test
                sort="id",  # Sort by character ID for consistent results
            )
            response = await vndb.character.query(char_from_vn_query)
            if response.results:
                print(
                    f"  SUCCESS: Found {len(response.results)} character(s) from VN {VN_ID} (showing up to 10):"
                )
                for char_item in response.results:
                    role_in_vn = "N/A"
                    # The 'vns' field on the character will contain info about their link to vn_id_for_chars
                    if char_item.vns:
                        # Find the entry for the specific VN we queried for, though it should be the only one
                        # if the filter worked as expected for a single VN ID.
                        for vn_link in char_item.vns:
                            if vn_link.id == VN_ID:  # vn_link.id is the ID of the VN
                                role_in_vn = (
                                    vn_link.role if vn_link.role else "Unknown Role"
                                )
                                break
                    print(
                        f"    - {char_item.name} | {char_item.original} (ID: {char_item.id}), Gender: {char_item.gender}, Age: {char_item.age}, Role in {VN_ID}: {role_in_vn}, Description: {char_item.description}"
                    )
                    # print(f"      Description (first 50 chars): {char_item.description[:50] if char_item.description else 'N/A'}...")
                assert len(response.results) > 0, f"Expected characters from VN {VN_ID}"
                if response.more:
                    print(f"  ...and more characters available for VN {VN_ID}.")
            else:
                print(f"  No characters found for VN {VN_ID} (or VN itself not found).")
        except VNDBAPIError as e:
            print(f"  ERROR fetching characters from VN: {e}")
        except AssertionError as e:
            print(f"  ASSERTION ERROR fetching characters from VN: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR fetching characters from VN: {e}")

        # Test 8: Ulist Endpoint Test
        # Using a known public user like "u2" (Yorhel) for reliability.
        # The user "u286975" from the image can also be used if their list is public.
        ulist_user_id: VNDBID = "u286975"
        print(f"\n[Test 8: POST /ulist (Query for user {ulist_user_id})]")
        try:
            ulist_query = QueryRequest(
                # user field in QueryRequest is set by vndb.ulist.query method
                fields="id, vote, vn{id, title, rating}, labels{id,label}",  # vn.title is good, vn.id and vn.rating for more info
                sort="vote",  # Sort by user's vote
                reverse=True,  # Highest votes first
                results=5,  # Get a few results for the test
                page=1,  # Default page is 1
                # filters=["label","=",7] # Example: filter by 'Voted' label (id 7)
            )
            # The user_id is passed directly to the ulist.query method
            response = await vndb.ulist.query(
                user_id=ulist_user_id, query_options=ulist_query
            )

            if response.results:
                print(
                    f"  SUCCESS: Fetched {len(response.results)} ulist entries for user {ulist_user_id} (sorted by vote desc, showing up to 5):"
                )
                for item in response.results:
                    vn_details = (
                        item.vn or {}
                    )  # item.vn is a dict of selected vn fields
                    labels_str = (
                        ", ".join([f"{lbl.label}({lbl.id})" for lbl in item.labels])
                        if item.labels
                        else "No Labels"
                    )
                    print(
                        f"    - VN: {vn_details.get('title', 'N/A')} (ID: {item.id}, VN Rating: {vn_details.get('rating', 'N/A')}), User Vote: {item.vote}"
                    )
                    print(f"      Labels: [{labels_str}]")
                while response.more:
                    ulist_query.page += 1  # Increment page to get more results
                    response = await vndb.ulist.query(
                        user_id=ulist_user_id, query_options=ulist_query
                    )
                    for item in response.results:
                        vn_details = item.vn or {}
                        labels_str = (
                            ", ".join([f"{lbl.label}({lbl.id})" for lbl in item.labels])
                            if item.labels
                            else "No Labels"
                        )
                        print(
                            f"    - VN: {vn_details.get('title', 'N/A')} (ID: {item.id}, VN Rating: {vn_details.get('rating', 'N/A')}), User Vote: {item.vote}"
                        )
                        print(f"      Labels: [{labels_str}]")
            else:
                print(
                    f"  No ulist entries found for user {ulist_user_id} with the given query (or list is private/empty)."
                )
        except VNDBAPIError as e:
            print(f"  ERROR fetching ulist for {ulist_user_id}: {e}")
        except AssertionError as e:
            print(f"  ASSERTION ERROR fetching ulist for {ulist_user_id}: {e}")
        except Exception as e:
            print(f"  UNEXPECTED ERROR fetching ulist for {ulist_user_id}: {e}")

    print("\n" + "-" * 30)
    print("Quick Test Finished.")


if __name__ == "__main__":
    # To run this script directly from src/veedb:
    # Ensure your VNDB_API_TOKEN environment variable is set if you want to test authenticated parts.
    # Example: VNDB_API_TOKEN="your-token-here" python quick_test.py
    asyncio.run(run_tests())
