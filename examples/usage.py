# examples/basic_usage.py
import asyncio
import os
from veedb import VNDB, QueryRequest # Updated import
from veedb.exceptions import VNDBAPIError # Updated import

async def main():
    # You can get a token from https://vndb.org/u/tokens
    # It's recommended to use an environment variable for the token
    api_token = os.environ.get("VNDB_API_TOKEN") # Keep env var name or change if you prefer

    # Using sandbox for this example, set use_sandbox=False for the real API
    async with VNDB(api_token=api_token, use_sandbox=False) as vndb:
        try:
            print("Fetching VNDB Stats:")
            stats = await vndb.get_stats()
            print(f"  Total VNs: {stats.vn}")
            print(f"  Total Characters: {stats.chars}\n")

            if api_token:
                print("Fetching Auth Info (requires token):")
                try:
                    auth_info = await vndb.get_authinfo()
                    print(f"  Authenticated as: {auth_info.username} (ID: {auth_info.id})")
                    print(f"  Permissions: {auth_info.permissions}\n")
                except VNDBAPIError as e:
                    print(f"  Error fetching auth info: {e}\n")
            else:
                print("Skipping Auth Info fetch as no API token is provided.\n")


            print("Fetching VN 'v17' (Ever17):")
            vn_query = QueryRequest(
                filters=["id", "=", "v17"],
                fields="id, title, olang, released, rating, image.url, developers{id,name}",
                results=1
            )
            vn_response = await vndb.vn.query(vn_query)

            if vn_response.results:
                ever17 = vn_response.results[0]
                print(f"  ID: {ever17.id}")
                print(f"  Title: {ever17.title}")
                print(f"  Original Language: {ever17.olang}")
                print(f"  Released: {ever17.released}")
                print(f"  Rating: {ever17.rating}")
                if ever17.image:
                    print(f"  Image URL: {ever17.image.url}")
                if ever17.developers:
                    print(f"  Developers: {[(dev.id, dev.name) for dev in ever17.developers]}")
            else:
                print("  VN v17 not found.")
            print("\n")


            print("Searching for VNs with 'Clannad' in the title (first 3 results):")
            clannad_search_query = QueryRequest(
                filters=["search", "=", "Clannad"],
                fields="id, title, released",
                results=3,
                sort="released"
            )
            clannad_response = await vndb.vn.query(clannad_search_query)

            if clannad_response.results:
                for vn_item in clannad_response.results:
                    print(f"  - {vn_item.title} (ID: {vn_item.id}, Released: {vn_item.released})")
            else:
                print("  No VNs found for 'Clannad'.")
            print(f"  More results available: {clannad_response.more}")
            if clannad_response.count is not None:
                 print(f"  Total matching VNs: {clannad_response.count}")
            print("\n")


            print("Fetching a random quote:")
            quote_query = QueryRequest(
                filters=["random", "=", 1],
                fields="id, quote, vn{id, title}, character{id, name}",
                results=1
            )
            try:
                quote_response = await vndb.quote.query(quote_query)
                if quote_response.results:
                    random_quote = quote_response.results[0]
                    print(f"  Quote ID: {random_quote.id}")
                    print(f"  Quote: \"{random_quote.quote}\"")
                    if random_quote.vn:
                        print(f"  From VN: {random_quote.vn.get('title', 'N/A')} (ID: {random_quote.vn.get('id')})")
                    if random_quote.character:
                         print(f"  By Character: {random_quote.character.get('name', 'N/A')} (ID: {random_quote.character.get('id')})")
                else:
                    print("  Could not fetch a random quote.")
            except VNDBAPIError as e:
                print(f"  Error fetching random quote: {e}")
            print("\n")


            # Added code to demonstrate fetching schema
            print("Fetching VNDB schema:")
            try:
                schema = await vndb.get_schema()
                print(f"  Found /vn fields in schema? {'/vn' in schema.get('api_fields', {})}")
            except VNDBAPIError as e:
                print(f"  Error fetching schema: {e}")
            print("\n")

            # Added code to demonstrate fetching a public user's info
            public_user_id = "u286975"
            print(f"Fetching public user info for '{public_user_id}':")
            try:
                user_info_dict = await vndb.get_user(q=public_user_id, fields="lengthvotes,lengthvotes_sum")
                user_info = user_info_dict.get(public_user_id)
                if user_info:
                    print(f"  Found user {user_info.username} (ID: {user_info.id})")
                else:
                    print("  No user info found or user is not public.")
            except VNDBAPIError as e:
                print(f"  Error fetching user info: {e}")
            print("\n")

            # Added code to demonstrate querying a character
            print("Querying character 'c5' (Takeshi Kuranari from Ever17):")
            char_query = QueryRequest(
                filters=["id", "=", "c5"],
                fields="id,name,original,blood_type,birthday,vns{id,title,role}",
                results=1
            )
            try:
                char_response = await vndb.character.query(char_query)
                if char_response.results:
                    char_data = char_response.results[0]
                    print(f"  Name: {char_data.name} (ID: {char_data.id})")
                    print(f"  Original: {char_data.original}")
                    print(f"  Blood Type: {char_data.blood_type}, Birthday: {char_data.birthday}")
                    if char_data.vns:
                        first_vn = char_data.vns[0]
                        print(f"  Appears in: {first_vn.title} (ID: {first_vn.id}), Role: {first_vn.role}")
                else:
                    print("  No data returned for character c5.")
            except VNDBAPIError as e:
                print(f"  Error fetching character 'c5': {e}")
            print("\n")


            target_user_id = "u2"
            print(f"Fetching ulist for user '{target_user_id}' (first 5 VNs, sorted by vote desc):")
            try:
                ulist_query = QueryRequest(
                    filters=["label", "=", 7],
                    fields="id, vote, vn{title, rating}, labels{id, label}",
                    sort="vote",
                    reverse=True,
                    results=5
                )
                ulist_response = await vndb.ulist.query(user_id=target_user_id, query_options=ulist_query)
                if ulist_response.results:
                    for item in ulist_response.results:
                        vn_details = item.vn or {}
                        labels_str = ", ".join([f"{lbl.label}({lbl.id})" for lbl in item.labels])
                        print(f"  - VN: {vn_details.get('title', 'N/A')} (ID: {item.id}), Vote: {item.vote}, Rating: {vn_details.get('rating', 'N/A')}")
                        print(f"    Labels: [{labels_str}]")
                else:
                    print(f"  No VNs found on user {target_user_id}'s voted list or list is private.")
            except VNDBAPIError as e:
                print(f"  Error fetching ulist for {target_user_id}: {e}")


        except VNDBAPIError as e:
            print(f"An API error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
