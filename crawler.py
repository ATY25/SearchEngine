"""
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import time

# ----------------------------
# CONFIG
# ----------------------------
BASE_URL = "https://pureportal.coventry.ac.uk"
START_PAGE = BASE_URL + "/en/publications/"
HEADERS = {"User-Agent": "ST7071CEM-IIR-Crawler"}
DELAY = 2


# ----------------------------
# CRAWLER FUNCTION
# ----------------------------
def crawl_publications(max_pages=5):
    visited = set()
    queue = deque([START_PAGE])
    publications = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        print("🔍 Crawling:", url)
        visited.add(url)
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for pub in soup.select("h3.title a"):
            title = pub.get_text(strip=True)
            pub_url = urljoin(BASE_URL, pub["href"])

            publications.append({
                "title": title,
                "year": "Unknown",
                "authors": [],
                "publication_url": pub_url
            })

        # ✅ Pagination (Next button)
        next_btn = soup.select_one("a.nextLink")
        if next_btn:
            next_url = urljoin(BASE_URL, next_btn["href"])
            queue.append(next_url)

        time.sleep(DELAY)

    return publications


# ----------------------------
# SAVE TO JSON FILE
# ----------------------------
def save_publications(publications, filename="docs.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(publications)} publications into {filename}")


# ----------------------------
# READ AUTHORS FROM JSON FILE
# ----------------------------
def get_all_authors(json_file="docs.json"):
 #   """
    #Reads docs.json and returns a unique sorted list of all authors.##################
  #  """
"""
    with open(json_file, "r", encoding="utf-8") as f:
        publications = json.load(f)

    authors_set = set()

    for pub in publications:
        for author in pub.get("authors", []):
            authors_set.add(author)

    return sorted(authors_set)


# ----------------------------
# MAIN PROGRAM
# ----------------------------
if __name__ == "__main__":

    # ✅ Step 1: Crawl publications
    pubs = crawl_publications(max_pages=5)

    # ✅ Step 2: Save results to publications.json
    save_publications(pubs)

    # ✅ Step 3: Load all authors from publications.json
    authors = get_all_authors()

    print("\n✅ Unique Authors Found:\n")
    if authors:
        for a in authors:
            print(" -", a)
    else:
        print("⚠ No authors found (authors list is empty in JSON)")
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://pureportal.coventry.ac.uk"

# -----------------------------
# ✅ Step 1: Extract Abstract + Fingerprints from Publication Page
# -----------------------------
def extract_pub_details(pub_url):
    try:
        response = requests.get(pub_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Extract Abstract
        abstract_tag = soup.select_one("div.textblock")
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else "No abstract found"

        # ✅ Extract Fingerprint Categories
        fingerprints = []
        fingerprint_tags = soup.select("a.fingerprint__link")

        for tag in fingerprint_tags:
            fingerprints.append(tag.get_text(strip=True))

        return abstract, fingerprints

    except Exception as e:
        print("Error extracting details:", e)
        return None, []


# -----------------------------
# ✅ Step 2: Crawl Publications List Page
# -----------------------------
def crawl_publications(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    publications = []

    # ✅ Find publications
    for pub in soup.select("h3.title a"):
        title = pub.get_text(strip=True)
        pub_url = urljoin(BASE_URL, pub["href"])

        print(f" Crawling publication: {title}")

        # ✅ Crawl publication page for abstract + fingerprints
        abstract, fingerprints = extract_pub_details(pub_url)

        publications.append({
            "title": title,
            "publication_url": pub_url,
            "abstract": abstract,
            "fingerprints": fingerprints
        })

        # polite delay
        time.sleep(1)

    return publications


# -----------------------------
# ✅ Step 3: Main Runner
# -----------------------------
if __name__ == "__main__":

    start_url = "https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-mathematics/publications/"

    print(" Starting full crawler...\n")

    data = crawl_publications(start_url)

    # ✅ Save Output JSON
    with open("publications_with_details.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("\n Done! Saved as publications_with_details.json")
