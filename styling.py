


import os

def print_plex_logo_ascii():
    file_path = os.path.join(os.path.dirname(__file__), "plex_ascii.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        print(f.read())