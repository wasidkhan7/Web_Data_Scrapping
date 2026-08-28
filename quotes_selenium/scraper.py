"""
Scraper: quotes.toscrape.com/js (Selenium)

WHY SELENIUM HERE (not requests/BeautifulSoup):
    The /js version of this site renders its quotes via JavaScript after
    the initial page load. A plain requests.get() returns an almost-empty
    HTML shell -- there is nothing for BeautifulSoup to parse until a real
    browser engine executes that JS. Selenium drives an actual Chrome
    instance, so it sees the page the same way a human visitor would.

WHAT THIS SCRIPT DEMONSTRATES:
    1. Launching a headless Chrome browser via Selenium
    2. Explicit waits (WebDriverWait) for elements to appear -- this is
       the correct way to handle JS-rendered content. A naive time.sleep()
       guesses how long rendering takes; an explicit wait polls until the
       element is actually there (or times out), which is both faster on
       average and more reliable.
    3. Clicking a "Next" button and re-scraping after each click, instead
       of following a link's href like we did with requests/BeautifulSoup
    4. Detecting "no more pages" by checking whether the Next button still
       exists, rather than knowing the page count in advance
"""

import csv
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

START_URL = "https://quotes.toscrape.com/js/"
OUTPUT_FILE = Path(__file__).parent / "output" / "quotes.csv"
WAIT_TIMEOUT = 10  # max seconds to wait for an element before giving up


def build_driver():
    """Configure and launch a headless Chrome instance."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1024") 
    # Selenium 4.6+ auto-downloads/manages the matching chromedriver --
    # no manual driver path needed.
    return webdriver.Chrome(options=options)


def scrape_current_page(driver):
    """Extract all quotes visible on the currently loaded page."""
    quote_elements = driver.find_elements(By.CSS_SELECTOR, "div.quote")

    quotes = []
    for el in quote_elements:
        text = el.find_element(By.CSS_SELECTOR, "span.text").text
        author = el.find_element(By.CSS_SELECTOR, "small.author").text
        tags = [tag.text for tag in el.find_elements(By.CSS_SELECTOR, "div.tags a.tag")]

        quotes.append({
            "text": text,
            "author": author,
            "tags": ", ".join(tags),
        })

    return quotes


def go_to_next_page(driver):
    """
    Try to click the 'Next' button. Returns True if it clicked (i.e. there
    was a next page), False if no Next button exists (we're on the last page).
    """
    try:
        next_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > a"))
        )
    except TimeoutException:
        return False

    next_button.click()

    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote"))
    )
    return True


def scrape_all_quotes():
    driver = build_driver()
    all_quotes = []

    try:
        driver.get(START_URL)

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote"))
        )

        page_num = 1
        while True:
            print(f"Scraping page {page_num}...")
            all_quotes.extend(scrape_current_page(driver))

            has_next = go_to_next_page(driver)
            if not has_next:
                print(f"No 'Next' button found on page {page_num} -- stopping.")
                break

            page_num += 1
            time.sleep(0.5)

    finally:
        driver.quit()

    return all_quotes


def save_to_csv(quotes, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(quotes)


if __name__ == "__main__":
    quotes = scrape_all_quotes()
    save_to_csv(quotes, OUTPUT_FILE)
    print(f"\nDone. Scraped {len(quotes)} quotes -> {OUTPUT_FILE}")