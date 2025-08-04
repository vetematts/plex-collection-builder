import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from pyfiglet import Figlet
from styling import print_plex_logo_ascii
import emojis
from plex_manager import PlexManager
from tmdb_search import TMDbSearch
from plexapi.exceptions import NotFound
import re
import json
from pyfiglet import Figlet

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"PLEX_TOKEN": "", "PLEX_URL": "", "TMDB_API_KEY": ""}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

"""
This script uses:
- The TMDb API (via TMDbSearch) to fetch movie titles by keyword or collection.
- The PlexAPI to search for movies and create collections in the user's Plex library.
- Optionally, scrapes Letterboxd lists for user-curated movie lists.
"""

init(autoreset=True)
load_dotenv()

config = load_config()
PLEX_TOKEN = config.get("PLEX_TOKEN")
PLEX_URL = config.get("PLEX_URL")
TMDB_API_KEY = config.get("TMDB_API_KEY")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

def welcome():
    from styling import print_plex_logo_ascii
    os.system("clear")  # Optional: clears terminal screen for cleanliness
    print_plex_logo_ascii()
    print(Fore.CYAN + "\n🎥 Welcome to the Plex Collection Builder!")
    print(Fore.YELLOW + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def check_credentials():
    print(Fore.GREEN + f"{emojis.KEY} Loaded environment variables:")
    print(f"Plex Token: {emojis.CHECK if PLEX_TOKEN else emojis.CROSS}")
    print(f"Plex URL: {PLEX_URL}")
    print(f"TMDb API Key: {emojis.CHECK if TMDB_API_KEY else emojis.CROSS}\n")

def run_collection_builder():

    def configure_credentials():
        while True:
            print("\nConfigure Credentials\n")
            print("1. Set Plex Token")
            print("2. Set Plex URL")
            print("3. Set TMDb API Key")
            print("4. Show current values")
            print("5. Return to main menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                config["PLEX_TOKEN"] = input("Enter new Plex Token: ").strip()
                save_config(config)
                print("Plex Token updated.")
            elif choice == "2":
                config["PLEX_URL"] = input("Enter new Plex URL: ").strip()
                save_config(config)
                print("Plex URL updated.")
            elif choice == "3":
                config["TMDB_API_KEY"] = input("Enter new TMDb API Key: ").strip()
                save_config(config)
                print("TMDb API Key updated.")
            elif choice == "4":
                print(json.dumps(config, indent=4))
            elif choice == "5":
                break
            else:
                print("Invalid choice. Try again.")

    while True:
        welcome()
        check_credentials()
        print(Fore.BLUE + "🎬 MENU OPTIONS:\n")
        print("1. 🎛️  Configure Credentials (Plex / TMDb)")
        print("2. 🎞️  Known Collection (e.g. Star Wars, Harry Potter)")
        print("3. 🏷️  Studio / Keyword Collection (e.g. A24, Pixar)")
        print("4. 📝 Manual Title Entry")
        print(Fore.RED + "5. ❌ Exit\n")
        print("Enter a number (1-5) to continue:")
        mode = input().strip()

        if mode == "1":
            configure_credentials()
            continue
        elif mode == "5":
            print("👋 Goodbye!")
            return
        else:
            break

    tmdb = TMDbSearch(config.get("TMDB_API_KEY")) if config.get("TMDB_API_KEY") else None

    titles = []
    KNOWN_COLLECTIONS = {
        "Alien": 8091,
        "Back to the Future": 264,
        "Despicable Me": 86066,
        "Evil Dead": 1960,
        "Fast & Furious": 9485,
        "Harry Potter": 1241,
        "The Hunger Games": 131635,
        "Indiana Jones": 84,
        "James Bond": 645,
        "John Wick": 404609,
        "Jurassic Park": 328,
        "The Lord of the Rings": 119,
        "The Matrix": 2344,
        "Mission: Impossible": 87359,
        "Ocean's": 304,
        "Pirates of the Caribbean": 295,
        "Planet of the Apes": 173710,
        "Scream": 2602,
        "Shrek": 2150,
        "Sonic the Hedgehog": 720879,
        "Star Trek": 115575,
        "Star Wars": 10,
        "The Dark Knight": 263,
        "The Twilight Saga": 33514
    }

    if mode == "2":
        fallback_titles = {
            "\nStar Wars\n": [
                "Star Wars",
                "Star Wars: Episode V - The Empire Strikes Back",
                "Star Wars: Episode VI - Return of the Jedi",
                "Star Wars: Episode I - The Phantom Menace",
                "Star Wars: Episode II - Attack of the Clones",
                "Star Wars: Episode III - Revenge of the Sith",
                "Star Wars: Episode VII - The Force Awakens",
                "Star Wars: Episode VIII - The Last Jedi"
                "Star Wars: The Rise Of Skywalker"
            ],
            "Harry Potter\n": [
                "Harry Potter and the Philosopher's Stone",
                "Harry Potter and the Chamber of Secrets",
                "Harry Potter and the Prisoner of Azkaban",
                "Harry Potter and the Goblet of Fire",
                "Harry Potter and the Order of the Phoenix",
                "Harry Potter and the Half-Blood Prince",
                "Harry Potter and the Deathly Hallows: Part 1",
                "Harry Potter and the Deathly Hallows: Part 2"
            ],
            "The Dark Knight\n": [
                "Batman Begins",
                "The Dark Knight",
                "The Dark Knight Rises"
            ],
            "The Lord of the Rings\n": [
                "The Lord of the Rings: The Fellowship of the Ring",
                "The Lord of the Rings: The Two Towers",
                "The Lord of the Rings: The Return of the King"
            ]
            # Add more collections here as needed...
        }

        if not tmdb:
            print("TMDb API key not provided. Using fallback hardcoded titles.")
            print("Available fallback collections:", ", ".join(fallback_titles.keys()))
            print("Type 'back' to return to the main menu.")
            collection_key = input("Type one: ").strip()
            if collection_key.lower() == "back":
                return run_collection_builder()
            titles = fallback_titles.get(collection_key, [])
            if not titles:
                print("Unknown collection.")
                return
        else:
            print("Available collections:")
            for collection in KNOWN_COLLECTIONS:
                print(f"- {collection}")
            print("Type 'back' to return to the main menu.")
            collection_key = input("Type one: ").strip()
            if collection_key.lower() == "back":
                return run_collection_builder()
            if collection_key in KNOWN_COLLECTIONS:
                collection_id = KNOWN_COLLECTIONS[collection_key]
                titles = tmdb.get_movies_from_collection(collection_id)
            else:
                print("Unknown collection.")
                return
    elif mode == "3":
        if not tmdb:
            print("TMDb API key not provided. Using fallback hardcoded titles.")
        print("Available options: \nA24\n, Pixar\n, Studio Ghibli\n, MCU\n, DCEU\n")
        print("Type 'back' to return to the main menu.")
        studio_key = input("Choose one: ").strip().lower()
        if studio_key == "back":
            return run_collection_builder()
        studio_map = {
            "a24": {"company": 41077},
            "pixar": {"company": 3},
            "studio ghibli": {"company": 10342},
            "mcu": {"keyword": 180547},
            "dceu": {"keyword": 229266}
        }

        if studio_key not in studio_map:
            print("Unknown option.")
            return

        import requests
        from urllib.parse import quote

        def fetch_movies_by_company_or_keyword(api_key, company_id=None, keyword_id=None):
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": api_key,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": 1
            }
            if company_id:
                params["with_companies"] = company_id
            if keyword_id:
                params["with_keywords"] = keyword_id

            all_titles = []
            while True:
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print("Failed to fetch movies.")
                    break
                data = response.json()
                all_titles.extend([movie["title"] for movie in data["results"]])
                if data["page"] >= data["total_pages"]:
                    break
                params["page"] += 1
            return all_titles

        studio_info = studio_map[studio_key]
        if tmdb:
            titles = fetch_movies_by_company_or_keyword(
                config.get("TMDB_API_KEY"),
                company_id=studio_info.get("company"),
                keyword_id=studio_info.get("keyword")
            )
        else:
            fallback_studios = {
                "a24": [
                    "Hereditary", "Midsommar", "The Lighthouse", "Uncut Gems",
                    "Lady Bird", "Moonlight", "The Green Knight", "X",
                    "Everything Everywhere All at Once", "Aftersun"
                ],
                "pixar": [
                    "Toy Story", "Finding Nemo", "The Incredibles", "Ratatouille",
                    "Up", "Inside Out", "Coco", "Soul", "Luca", "Turning Red"
                ],
                "studio ghibli": [
                    "My Neighbor Totoro", "Spirited Away", "Princess Mononoke",
                    "Howl's Moving Castle", "Nausicaä of the Valley of the Wind",
                    "Kiki's Delivery Service", "Ponyo", "The Wind Rises",
                    "The Tale of the Princess Kaguya", "Earwig and the Witch"
                ],
                "mcu": [
                    "Iron Man", "The Avengers", "Captain America: The Winter Soldier",
                    "Guardians of the Galaxy", "Avengers: Age of Ultron", "Doctor Strange",
                    "Black Panther", "Avengers: Infinity War", "Avengers: Endgame", "Spider-Man: No Way Home"
                ],
                "dceu": [
                    "Man of Steel", "Batman v Superman: Dawn of Justice",
                    "Suicide Squad", "Wonder Woman", "Justice League",
                    "Aquaman", "Shazam!", "Birds of Prey", "The Suicide Squad", "Black Adam"
                ]
            }
            titles = fallback_studios.get(studio_key, [])
    elif mode == "4":
        print("Type 'back' to return to the main menu.")
        print("Enter a name for your new collection:")
        collection_name = input("> ").strip()
        if collection_name.lower() == "back":
            return run_collection_builder()

        print("\nEnter movie titles one per line. Leave a blank line to finish:")
        while True:
            title = input()
            if not title.strip():
                break
            titles.append(title.strip())

    if mode in ("2", "3"):
        collection_name = input("Enter a name for your new collection: ").strip()

    if not titles:
        print("No movies found for that input.")
        return

    if MOCK_MODE:
        print("[MOCK MODE ENABLED]")
        print(f"Simulating search in Plex for {len(titles)} titles...")
        for title in titles:
            print(f"- Would add '{title}' to collection.")
        print(f"Finished. Would create collection with {len(titles)} movies.")
        return

    plex = PlexManager(config.get("PLEX_TOKEN"), config.get("PLEX_URL"))
    library = plex.plex.library.section("Movies")

    import re

    def extract_title_and_year(raw_title):
        match = re.match(r"^(.*?)(?:\s+\((\d{4})\))?$", raw_title.strip())
        return (match.group(1).strip(), int(match.group(2)) if match.group(2) else None)

    found_movies = []
    not_found = []

    for raw_title in titles:
        title, year = extract_title_and_year(raw_title)

        try:
            if year:
                results = library.search(title, year=year)
            else:
                results = library.search(title)

            if results:
                found_movies.append(results[0])
            else:
                if year:
                    fallback_results = library.search(title)
                    if fallback_results:
                        found_movies.append(fallback_results[0])
                        continue
                not_found.append(raw_title)

        except Exception as e:
            print(f"Error searching for '{raw_title}': {e}")
            not_found.append(raw_title)

    print(f"\nFound {len(found_movies)} movies in Plex.")
    if not_found:
        print(f"Couldn’t find {len(not_found)}:")
        for nf in not_found:
            print(f"- {nf}")

    if found_movies:
        print("\nMovies to add to collection:")
        for i, movie in enumerate(found_movies, 1):
            print(f"{i}. {movie.title}")
        confirm = input("Proceed to create collection with these movies? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Aborted by user.")
            return
        library.createCollection(collection_name, items=found_movies)
        print(f"\n{emojis.CHECK} Created collection '{collection_name}' with {len(found_movies)} movies.")
        return run_collection_builder()
    else:
        print(f"{emojis.CROSS} No valid matches found — collection not created.")

if __name__ == "__main__":
    run_collection_builder()