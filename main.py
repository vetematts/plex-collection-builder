"""
This script uses:
- The TMDb API (via TMDbSearch) to fetch movie titles by keyword or collection.
- The PlexAPI to search for movies and create collections in the user's Plex library.
"""

import os
import json
import re

from dotenv import load_dotenv
from colorama import init, Fore
import emojis
from plex_manager import PlexManager
from tmdb_search import TMDbSearch
from styling import print_plex_logo_ascii

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    # Load credentials from config.json, or return empty defaults if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        return {"PLEX_TOKEN": "", "PLEX_URL": "", "TMDB_API_KEY": ""}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    # Save the current credentials to config.json for future use
    # Accepts a dictionary of credentials.
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)


init(autoreset=True)
load_dotenv()

config = load_config()
PLEX_TOKEN = config.get("PLEX_TOKEN")
PLEX_URL = config.get("PLEX_URL")
TMDB_API_KEY = config.get("TMDB_API_KEY")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


def welcome():
    # Display welcome message and Plex logo.
    os.system("clear")  # Optional: clears terminal screen for cleanliness
    print_plex_logo_ascii()
    print(Fore.CYAN + f"\n{emojis.MOVIE} Welcome to the Plex Collection Builder!")
    print(Fore.YELLOW + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


def check_credentials():
    # Check and display the status of the loaded credentials.
    # Shows which credentials are set using color and emoji indicators.
    current_config = load_config()
    print(Fore.GREEN + f"{emojis.KEY} Loaded Credentials:")
    print(
        f"Plex Token: {emojis.CHECK if current_config.get('PLEX_TOKEN', '').strip() else emojis.CROSS}"
    )
    print(
        f"Plex URL: {emojis.CHECK if current_config.get('PLEX_URL', '').strip() else emojis.CROSS}"
    )
    print(
        f"TMDb API Key: {emojis.CHECK if current_config.get('TMDB_API_KEY', '').strip() else emojis.CROSS}\n"
    )


def run_collection_builder():
    # Main function to run the Plex collection builder interface.
    # Handles user interaction, menu navigation, and collection creation.

    def configure_credentials():
        # Interactive menu for setting and viewing Plex/TMDb credentials.
        def pause(msg: str = "Press Enter to return to the credentials menu..."):
            input(msg)

        menu_options = [
            (f"{emojis.KEY} Set Plex Token", "1"),
            (f"{emojis.URL} Set Plex URL", "2"),
            (f"{emojis.CLAPPER} Set TMDb API Key", "3"),
            (f"{emojis.BOOK} Show current values", "4"),
            (f"{emojis.BACK} Return to main menu", "5"),
        ]

        while True:
            os.system("clear")
            print(Fore.CYAN + f"{emojis.CONFIGURE} CONFIGURE CREDENTIALS")
            print(Fore.GREEN + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            for idx, (desc, num) in enumerate(menu_options, 1):
                color = (
                    Fore.YELLOW
                    if num in ("1", "2")
                    else Fore.BLUE
                    if num == "3"
                    else Fore.GREEN
                    if num == "4"
                    else Fore.RED
                )
                print(f"{color}{num}.{Fore.RESET} {desc}\n")
            choice = input("Select an option: ").strip()
            if choice == "1":
                config["PLEX_TOKEN"] = input("Enter new Plex Token: ").strip()
                save_config(config)
                print(Fore.GREEN + f"{emojis.CHECK} Plex Token saved successfully!\n")
                pause()
            elif choice == "2":
                config["PLEX_URL"] = input("Enter new Plex URL: ").strip()
                save_config(config)
                print(Fore.GREEN + f"{emojis.CHECK} Plex URL saved successfully!\n")
                pause()
            elif choice == "3":
                config["TMDB_API_KEY"] = input("Enter new TMDb API Key: ").strip()
                save_config(config)
                print(Fore.GREEN + f"{emojis.CHECK} TMDb API Key saved successfully!\n")
                pause()
            elif choice == "4":
                os.system("clear")
                print(Fore.CYAN + f"{emojis.BOOK} Current Configuration:\n")
                print(json.dumps(config, indent=4))
                pause("\nPress Enter to return to the credentials menu...")
            elif choice == "5":
                break
            else:
                print("Invalid choice. Try again.")
                pause()

    while True:
        welcome()
        check_credentials()
        print(Fore.BLUE + f"{emojis.CLAPPER} MAIN MENU:\n")
        print(Fore.GREEN + "1." + Fore.RESET + f" {emojis.MANUAL} Manual Entry\n")
        print(
            Fore.GREEN
            + "2."
            + Fore.RESET
            + f" {emojis.FRANCHISE}  Known Franchise (e.g. Star Wars, Harry Potter)\n"
        )
        print(
            Fore.GREEN
            + "3."
            + Fore.RESET
            + f" {emojis.STUDIO}  Studio / Keyword (e.g. A24, Pixar)\n"
        )
        print(
            Fore.YELLOW
            + "4."
            + Fore.RESET
            + f" {emojis.SETTINGS}  Configure Credentials (Plex / TMDb)\n"
        )
        print(Fore.RED + "5." + Fore.RESET + f" {emojis.EXIT} Exit\n")
        print(
            Fore.LIGHTBLACK_EX
            + f"{emojis.INFO} You can return to this menu after each collection is created.\n"
        )
        mode = input().strip()

        if mode not in ("1", "2", "3", "4", "5"):
            print("Invalid selection. Please choose a valid menu option (1-5).")
            input("Press Enter to return to the main menu...")
            continue

        if mode == "1":
            # Manual entry mode: user types movie titles for a new collection.
            print("Type 'back' to return to the main menu.")
            print("Enter a name for your new collection:")
            collection_name = input("> ").strip()
            if collection_name.lower() == "back":
                return run_collection_builder()
            plex_token = config.get("PLEX_TOKEN")
            plex_url = config.get("PLEX_URL")
            if not plex_token or not plex_url:
                print(
                    Fore.RED + f"{emojis.CROSS} Missing or invalid Plex Token or URL."
                )
                return

            titles = []
            print("\nEnter movie titles one per line. Leave a blank line to finish:")
            while True:
                title = input()
                if not title.strip():
                    break
                titles.append(title.strip())
        elif mode == "5":
            # Exit the application.
            print(f"{emojis.WAVE} Goodbye!")
            return
        elif mode == "4":
            # Configure credentials menu.
            configure_credentials()
            return run_collection_builder()
        else:
            break

    tmdb = (
        TMDbSearch(config.get("TMDB_API_KEY")) if config.get("TMDB_API_KEY") else None
    )

    studio_map = {
        "a24": {"company": 41077},
        "pixar": {"company": 3},
        "studio ghibli": {"company": 10342},
        "mcu": {"keyword": 180547},
        "dceu": {"keyword": 229266},
    }

    titles = []
    known_collections = {
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
        "The Twilight Saga": 33514,
    }

    if mode == "2":
        # Franchise mode: user selects a known franchise to build a collection.
        fallback_titles_path = os.path.join(
            os.path.dirname(__file__), "fallback_collections.json"
        )
        with open(fallback_titles_path, "r", encoding="utf-8") as f:
            fallback_titles = json.load(f)

        if not tmdb:
            print(
                Fore.RED
                + f"{emojis.CROSS} TMDb API key not provided. Using fallback hardcoded titles.\n"
            )
            print(Fore.CYAN + f"{emojis.FRANCHISE}  Available Franchises:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            franchises_data = fallback_titles.get("Franchises", {})
            for franchise in sorted(franchises_data.keys()):
                print(f"- {franchise}")

            print(
                "\n"
                + Fore.LIGHTBLACK_EX
                + f"{emojis.REPEAT} Type the franchise name (or 'back' to return):"
            )
            collection_key = input("Type one: ").strip().lower()
            if collection_key.lower() == "back":
                return run_collection_builder()
            if collection_key not in [key.lower() for key in franchises_data]:
                print("Unknown collection.")
                return run_collection_builder()
            matched_key = next(
                (key for key in franchises_data if key.lower() == collection_key), None
            )
            titles = franchises_data[matched_key]
        else:

            def print_collection_list(collections, columns=3, padding=28):
                names = sorted(collections)
                rows = [names[i : i + columns] for i in range(0, len(names), columns)]
                for row in rows:
                    print("".join(name.ljust(padding) for name in row))

            print(Fore.CYAN + f"{emojis.FRANCHISE}  Available Collections (TMDb):")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            print_collection_list(known_collections.keys())
            print(
                "\n"
                + Fore.LIGHTBLACK_EX
                + f"{emojis.REPEAT} Type the collection name (or 'back' to return):"
            )
            collection_key = input().strip().lower()
            if collection_key.lower() == "back":
                return run_collection_builder()
            if collection_key in [key.lower() for key in known_collections]:
                matched_key = next(
                    (key for key in known_collections if key.lower() == collection_key),
                    None,
                )
                collection_id = known_collections[matched_key]
                titles = tmdb.get_movies_from_collection(collection_id)
            else:
                print("Unknown collection.\n")
                return run_collection_builder()
    elif mode == "3":
        # Studio/keyword mode: user selects a studio or keyword to build a collection.
        fallback_titles_path = os.path.join(
            os.path.dirname(__file__), "fallback_collections.json"
        )
        with open(fallback_titles_path, "r", encoding="utf-8") as f:
            fallback_data = json.load(f)

        def print_studio_list(studios, columns=3, padding=24):
            names = sorted(studios)
            rows = [names[i : i + columns] for i in range(0, len(names), columns)]
            for row in rows:
                print("".join(name.ljust(padding) for name in row))

        # Print TMDb API fallback warning if needed
        if not tmdb:
            studios_data = load_fallback_data("Studios")
            print(
                Fore.RED
                + f"{emojis.CROSS} TMDb API key not provided. Using fallback hardcoded titles.\n"
            )
            print(Fore.CYAN + f"{emojis.STUDIO}  Available Studios:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            print_list(studios_data.keys(), columns=3, padding=24)
            print(
                "\n"
                + Fore.LIGHTBLACK_EX
                + f"{emojis.REPEAT} Type the studio name (or 'back' to return):"
            )
            print("Type 'back' to return to the main menu.")
            studio_key = input("Choose one: ").strip().lower()
            if studio_key == "back":
                return run_collection_builder()

            if not tmdb:
                if studio_key not in [
                    key.lower() for key in fallback_data.get("Studios", {})
                ]:
                    print("Unknown option.")
                    return run_collection_builder()
                matched_key = next(
                    (
                        key
                        for key in fallback_data.get("Studios", {})
                        if key.lower() == studio_key
                    ),
                    None,
                )
                titles = fallback_data.get("Studios", {}).get(matched_key, [])
            else:
                if studio_key not in studio_map:
                    print("Unknown option.")
                    return run_collection_builder()

                import requests

                def fetch_movies_by_company_or_keyword(
                    api_key, company_id=None, keyword_id=None
                ):
                    url = "https://api.themoviedb.org/3/discover/movie"
                    params = {
                        "api_key": api_key,
                        "language": "en-US",
                        "sort_by": "popularity.desc",
                        "page": 1,
                    }
                    if company_id:
                        params["with_companies"] = company_id
                    if keyword_id:
                        params["with_keywords"] = keyword_id

                    all_titles = []
                    while True:
                        response = requests.get(url, params=params, timeout=10)
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
                titles = fetch_movies_by_company_or_keyword(
                    config.get("TMDB_API_KEY"),
                    company_id=studio_info.get("company"),
                    keyword_id=studio_info.get("keyword"),
                )

    if mode in ("2", "3"):
        # Prompt for collection name after franchise/studio selection.
        collection_name = input("Enter a name for your new collection: ").strip()

    if not titles:
        # No titles were found for the selected franchise/studio/keyword.
        print("No movies found for that input.")
        return

    if MOCK_MODE:
        # If MOCK_MODE is enabled, simulate Plex actions for testing without making changes.
        print("[MOCK MODE ENABLED]")
        print(f"Simulating search in Plex for {len(titles)} titles...")
        for title in titles:
            print(f"- Would add '{title}' to collection.")
        print(f"Finished. Would create collection with {len(titles)} movies.")
        return

    plex_token = config.get("PLEX_TOKEN")
    plex_url = config.get("PLEX_URL")

    if not plex_token or not plex_url:
        # Credentials are missing or invalid; cannot proceed.
        print(Fore.RED + f"{emojis.CROSS} Missing or invalid Plex Token or URL.")
        return

    # Attempt to connect to Plex and get the Movies library.
    try:
        plex = PlexManager(plex_token, plex_url)
        library = plex.plex.library.section("Movies")
    except Exception:
        # Generalized error handling for any Plex connection issues.
        print(Fore.RED + f"{emojis.CROSS} Could not connect to Plex.")
        print("Please make sure your Plex Token and URL are correct.\n")
        return run_collection_builder()

    def extract_title_and_year(raw_title):
        # Helper to extract movie title and optional year from user input.
        # Example: "Inception (2010)" -> ("Inception", 2010)
        match = re.match(r"^(.*?)(?:\s+\((\d{4})\))?$", raw_title.strip())
        return (match.group(1).strip(), int(match.group(2)) if match.group(2) else None)

    found_movies = []
    not_found = []

    for raw_title in titles:
        # Search for each movie in Plex, using year if available.
        title, year = extract_title_and_year(raw_title)

        try:
            if year:
                # Prefer searching with year for more accurate results.
                results = library.search(title, year=year)
            else:
                results = library.search(title)

            if results:
                found_movies.append(results[0])
            else:
                # If not found with year, try searching without year as a fallback.
                if year:
                    fallback_results = library.search(title)
                    if fallback_results:
                        found_movies.append(fallback_results[0])
                        continue
                not_found.append(raw_title)

        except (AttributeError, TypeError, ValueError) as e:
            # Handle unexpected errors during search (e.g., bad data or API issues).
            print(f"Error searching for '{raw_title}': {e}")
            not_found.append(raw_title)

    print(f"\nFound {len(found_movies)} movies in Plex.")
    if not_found:
        print(f"Couldn’t find {len(not_found)}:")
        for nf in not_found:
            print(f"- {nf}")

    if found_movies:
        # Confirm with the user before creating the collection in Plex.
        print("\nMovies to add to collection:")
        for i, movie in enumerate(found_movies, 1):
            print(f"{i}. {movie.title}")
        confirm = (
            input("Proceed to create collection with these movies? (y/n): ")
            .strip()
            .lower()
        )
        if confirm != "y":
            print("Aborted by user.")
            return
        # Actually create the collection in Plex.
        library.createCollection(collection_name, items=found_movies)
        print(
            f"\n{emojis.CHECK} Created collection '{collection_name}' with {len(found_movies)} movies."
        )
        return run_collection_builder()
    else:
        print(f"{emojis.CROSS} No valid matches found — collection not created.")


def load_fallback_data(section):
    # Load fallback data for a given section from fallback_collections.json.
    fallback_path = os.path.join(os.path.dirname(__file__), "fallback_collections.json")
    with open(fallback_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(section, {})


def print_list(items, columns=3, padding=28):
    # Print a list of items in columns.
    names = sorted(items)
    rows = [names[i : i + columns] for i in range(0, len(names), columns)]
    for row in rows:
        print("".join(name.ljust(padding) for name in row))


if __name__ == "__main__":
    # Entry point: start the interactive collection builder.
    run_collection_builder()
