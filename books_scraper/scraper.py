"""
Scraper: books.toscrape.com (BeautifulSoup)

Demonstrates:
- Pagination by following the "next" link until it's absent (no hardcoded page count)
- Absolute URL resolution via urljoin (handles relative links safely)
- Polite scraping: custom User-Agent + delay between requests
- Clean separation: fetch/parse -> orchestrate -> save
"""

import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_FILE = Path(__file__).parent / "output" / "books.csv"

# Map the star-rating CSS class word to a number, since the site encodes
# rating as text ("Three") rather than a number.
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (portfolio-scraper learning project)"
}


def scrape_page(url):
    """Fetch one listing page and return (list of book dicts, next_page_url or None)."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    books = []
    for article in soup.find_all("article", class_="product_pod"):
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").get_text(strip=True)
        availability = article.find("p", class_="instock availability").get_text(strip=True)

        rating_class = article.find("p", class_="star-rating")["class"]
        rating_word = rating_class[1]  # e.g. ['star-rating', 'Three']
        rating = RATING_WORDS.get(rating_word)

        relative_link = article.h3.a["href"]
        product_url = requests.compat.urljoin(BASE_URL, relative_link)

        books.append({
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "product_url": product_url,
        })

    # Pagination: look for the "next" link; if it's not there, we're done.
    next_link = soup.find("li", class_="next")
    if next_link:
        next_href = next_link.a["href"]
        next_url = requests.compat.urljoin(url, next_href)
    else:
        next_url = None

    return books, next_url


def scrape_all_books():
    all_books = []
    url = START_URL
    page_num = 1

    while url:
        print(f"Scraping page {page_num}: {url}")
        books, next_url = scrape_page(url)
        all_books.extend(books)
        url = next_url
        page_num += 1
        time.sleep(0.5)  # polite delay between requests

    return all_books


def save_to_csv(books, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "availability", "rating", "product_url"])
        writer.writeheader()
        writer.writerows(books)


if __name__ == "__main__":
    books = scrape_all_books()
    save_to_csv(books, OUTPUT_FILE)
    print(f"\nDone. Scraped {len(books)} books -> {OUTPUT_FILE}")