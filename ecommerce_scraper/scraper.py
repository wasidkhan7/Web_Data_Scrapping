"""
Scraper: webscraper.io/test-sites/e-commerce/static (BeautifulSoup)

Demonstrates:
- Query-parameter pagination (?page=N), stopping when a page returns
  zero products, instead of following a "next" link
- Parsing nested/compound fields (star rating counted from icon elements,
  not read as plain text)
- Polite scraping: custom User-Agent + delay between requests
"""

import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
OUTPUT_FILE = Path(__file__).parent / "output" / "laptops.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (portfolio-scraper learning project)"
}


def scrape_page(page_num):
    """Fetch one page of results. Returns a list of product dicts (empty if no products found)."""
    url = f"{BASE_URL}?page={page_num}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    products = []
    for thumb in soup.find_all("div", class_="thumbnail"):
        title_tag = thumb.find("a", class_="title")
        title = title_tag["title"] if title_tag else None

        price_tag = thumb.find("h4", class_="price")
        price = price_tag.get_text(strip=True) if price_tag else None

        desc_tag = thumb.find("p", class_="description")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        # Star rating is encoded as repeated <span class="glyphicon-star">
        # icons, not a number in the text -- so we count elements instead
        # of parsing text.
        ratings_div = thumb.find("div", class_="ratings")
        star_count = len(ratings_div.find_all("span", class_="glyphicon-star")) if ratings_div else 0

        review_tag = thumb.find("p", class_="pull-right")
        review_count = review_tag.get_text(strip=True) if review_tag else None

        products.append({
            "title": title,
            "price": price,
            "description": description,
            "stars": star_count,
            "reviews": review_count,
            "page": page_num,
        })

    return products


def scrape_all_pages(max_pages=50):
    """Keep incrementing page=N until a page comes back with no products."""
    all_products = []
    page_num = 1

    while page_num <= max_pages:
        print(f"Scraping page {page_num}: {BASE_URL}?page={page_num}")
        products = scrape_page(page_num)

        if not products:
            print(f"No products found on page {page_num} -- stopping.")
            break

        all_products.extend(products)
        page_num += 1
        time.sleep(0.5)  # polite delay between requests

    return all_products


def save_to_csv(products, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "description", "stars", "reviews", "page"])
        writer.writeheader()
        writer.writerows(products)


if __name__ == "__main__":
    products = scrape_all_pages()
    save_to_csv(products, OUTPUT_FILE)
    print(f"\nDone. Scraped {len(products)} products -> {OUTPUT_FILE}")