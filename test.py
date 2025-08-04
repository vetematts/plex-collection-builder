from letterboxd_parser import get_letterboxd_titles
import requests
from bs4 import BeautifulSoup

url = "https://letterboxd.com/herman2181/list/a24/"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; PlexCollectionBot/1.0)"
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

poster_items = soup.select('li.poster-container')
print(f"Found {len(poster_items)} poster containers.")
for i, item in enumerate(poster_items[:5], 1):
    tooltip_link = item.select_one('div.tooltip a')
    print(f"{i}: {tooltip_link.get('title') if tooltip_link else 'No title found'}")