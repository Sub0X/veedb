from veedb import VNDB, QueryRequest

async def test_vndb_search():
    async with VNDB() as vndb:
        title = "v12984"
        FILTER = ["search", "=", title]
        searchReq = QueryRequest(
            filters=FILTER,
            results=3,
            fields="id, title, released, olang, languages, titles.title, titles.lang, " +\
                "image.id, image.url, image.thumbnail, image.dims, image.sexual, image.violence, image.votecount"
        )
        
        try:
            results = await vndb.vn.query(searchReq)
            
            if not results.results:
                print("No visual novels found with that title.")
                return
            
            for vn in results.results:
                print(f"{vn.id}: {vn.title} ({vn.released}) - {vn.olang} - {', '.join(vn.languages)}")
                print(vn.titles)
                for title in vn.titles:
                    print(title)
            
            validator = vndb._get_filter_validator()
            schema = await validator.schema_cache.get_schema(vndb)
            
            enums = await vndb.get_enums()
            languages = enums.get("language", [])

            # print("Available enums:", enums)
            # print("Available countries:", languages)
            
            current_lang = ""
            
            if len(current_lang) == 0:
                choices = [
                    (language["id"], language["label"])
                    for language in languages
                ][:25]
            else:
                choices = [
                    (language["id"], language["label"])
                    for language in languages if current_lang.lower() in language["label"].lower() or language["id"].startswith(current_lang.lower())
                ][:25]
            print("Autocomplete choices for languages:", choices)
            
            # Get images for the VN
            results_with_images = [
                (vn.id, vn.title, vn.image.thumbnail) for vn in results.results if vn.image and vn.image.thumbnail
            ]
            if results_with_images:
                print("Visual Novels with images:")
                for vn_id, title, thumbnail in results_with_images:
                    print(f"{vn_id}: {title} - {thumbnail}")
            else:
                print("No visual novels with images found.")
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vndb_search())