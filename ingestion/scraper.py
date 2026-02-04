import requests
from bs4 import BeautifulSoup
import time
import json
import os
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.daiict.ac.in"
SOURCE_URLS = [
    "https://www.daiict.ac.in/faculty",
    "https://www.daiict.ac.in/professor-practice",
    "https://www.daiict.ac.in/adjunct-faculty",
    "https://www.daiict.ac.in/adjunct-faculty-international",
    "https://www.daiict.ac.in/distinguished-professor"
]
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_faculty.json")

PROFILE_PREFIXES = [
    "/faculty/",
    "/professor-practice/",
    "/adjunct-faculty/",
    "/adjunct-faculty-international/",
    "/distinguished-professor/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_soup(url, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logger.warning(f"Attempt {i+1} failed for {url}: {e}")
            time.sleep(random.uniform(1, 3))
    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return None

def get_faculty_links():
    all_links = set()
    for source_url in SOURCE_URLS:
        logger.info(f"Scanning {source_url}...")
        soup = get_soup(source_url)
        if not soup:
            continue
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')
            if any(prefix in href for prefix in PROFILE_PREFIXES):
                if href.strip("/") in [p.strip("/") for p in PROFILE_PREFIXES]:
                    continue
                if not href.startswith("http"):
                    href = BASE_URL + href if href.startswith("/") else BASE_URL + "/" + href
                all_links.add(href)
    unique_links = list(all_links)
    logger.info(f"Found {len(unique_links)} unique faculty profiles across {len(SOURCE_URLS)} categories.")
    return unique_links

def scrape_profile(url):
    soup = get_soup(url)
    if not soup:
        return None
    profile_data = {"url": url}
    name_tag = None
    for h1 in soup.find_all("h1"):
        if "logo" not in h1.get_text(strip=True).lower():
            name_tag = h1
            break
    if not name_tag:
        name_tag = soup.find("h2")
    profile_data["name"] = name_tag.get_text(strip=True) if name_tag else "Unknown"
    content_blocks = {}
    headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
    for header in headers:
        header_text = header.get_text(strip=True).lower()
        content = []
        curr = header.next_sibling
        while curr:
            if getattr(curr, 'name', None) in ['h2', 'h3', 'h4']:
                break
            if getattr(curr, 'name', None):
                text = curr.get_text(strip=True)
                if text:
                    content.append(text)
            elif isinstance(curr, str):
                text = curr.strip()
                if text:
                    content.append(text)
            curr = getattr(curr, 'next_sibling', None)
        if content:
            content_blocks[header_text] = " ".join(content)
        else:
            if header.parent:
                curr_parent = header.parent.next_sibling
                while curr_parent:
                    if getattr(curr_parent, 'name', None):
                         text = curr_parent.get_text(strip=True)
                         if text:
                             content_blocks[header_text] = text
                             break
                    curr_parent = getattr(curr_parent, 'next_sibling', None)
    profile_data["sections"] = content_blocks
    profile_data["full_text"] = soup.get_text(separator=" ", strip=True)
    return profile_data

def main():
    logger.info("Starting Ingestion Pipeline...")
    links = get_faculty_links()
    results = []
    for idx, link in enumerate(links):
        logger.info(f"[{idx+1}/{len(links)}] Scraping {link}...")
        data = scrape_profile(link)
        if data:
            results.append(data)
        time.sleep(random.uniform(0.5, 1.5))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    logger.info(f"Ingestion complete. Saved {len(results)} profiles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
