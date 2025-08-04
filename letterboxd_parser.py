# letterboxd_parser.py
import requests
from bs4 import BeautifulSoup

def get_letterboxd_titles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PlexCollectionBot/1.0)"
    }
    titles = set()
    page = 1

    while True:
        page_url = url if page == 1 else f"{url}page/{page}/"
        response = requests.get(page_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.prettify()[:1500])  # Debug: see what HTML we're actually getting

        # Strategy 1: Poster layout – tooltip link title
        for item in soup.select('li.poster-container'):
            tooltip_link = item.select_one('div.tooltip a')
            if tooltip_link:
                title = tooltip_link.get('title')
                if title:
                    titles.add(title.strip())

        # Strategy 2: Text view – headline
        for link in soup.select('h2.headline-2 a'):
            text = link.get_text(strip=True)
            if text:
                titles.add(text)

        # Strategy 3: Poster view tooltip
        for link in soup.select('li.poster-container div.tooltip a'):
            title = link.get('title')
            if title:
                titles.add(title.strip())

        # Check if next page exists
        if not soup.select_one('a.next'):
            break

        page += 1

    if not titles:
        print("No movie titles found on the Letterboxd page. The page layout may have changed or the list is empty.")

    return list(titles)