# plex_manager.py

from plexapi.server import PlexServer

class PlexManager:
    def __init__(self, token, base_url):
        self.plex = PlexServer(base_url, token)

    def get_movie_library(self, library_name):
        try:
            return self.plex.library.section(library_name)
        except Exception as e:
            print(f"❌ Error: Could not find library '{library_name}'")
            print(e)
            return None

    def find_movies(self, library, titles):
        matched = []
        for title in titles:
            results = library.search(title)
            if results:
                matched.append((title, results[0]))
        return matched

    def add_to_collection(self, items, collection_name):
        for title, media in items:
            media.addCollection(collection_name)
            media.reload()
            print(f"✅ Added '{title}' to collection: {collection_name}")