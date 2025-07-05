import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import asyncio
import json
from src.veedb import QueryRequest, VNDB

async def main():
    vn_id = "v17"  # Ever 17

    # Fetch real VN data from VNDB
    async with VNDB() as vndb:
        req = QueryRequest(
            filters=["id", "=", vn_id],
            fields=(
                "id, title, released, length, rating, description, "
                "length_minutes, length_votes, languages, platforms, olang, devstatus, "
                "titles{title, lang, official, main}, aliases, "
                "image{id, url, thumbnail, dims, sexual, violence, votecount}, "
                "tags{id, name, rating, spoiler, lie, description, category, aliases, searchable, applicable, vn_count}, "
                "developers{id, name, lang, type, description, extlinks{url, label, name, id}, aliases, original}, "
                "relations{id, relation, title, relation_official, languages, platforms, olang}, "
                "screenshots{id, url, thumbnail, release{id, title}}, "
                "editions{eid, lang, name, official}, "
                "staff{id, aid, role, name, original, lang, gender, description, eid}, "
                "va{note, staff{id, aid, name, original, lang, gender, description}, character{id, name, original, aliases, description, image{id, url, dims, sexual, violence, votecount}, height, weight, blood_type, hips, bust, waist, cup, age, birthday, sex, gender, vns{spoiler, role, id}, traits{spoiler, lie}}}, "
                "extlinks{url, label, name, id}"

            )
        )
        result = await vndb.vn.query(req)
        if not result.results:
            print("VN not found!")
            return
        vndb_data = result.results[0]

    print(json.dumps(vndb_data.__dict__, default=str, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
