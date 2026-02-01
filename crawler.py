import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://pureportal.coventry.ac.uk"

# -----------------------------
#Extracting Abstract + Fingerprints from Publication Page
# -----------------------------
def extract_pub_details(pub_url):
    try:
        response = requests.get(pub_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extracting Abstract
        abstract_tag = soup.select_one("div.textblock")
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else "No abstract found"

        # Extracting Fingerprint Categories
        fingerprints = []
        fingerprint_tags = soup.select("a.fingerprint__link")

        for tag in fingerprint_tags:
            fingerprints.append(tag.get_text(strip=True))

        return abstract, fingerprints

    except Exception as e:
        print("Error extracting details:", e)
        return None, []


# -----------------------------
# Crawl Publications List Page
# -----------------------------
def crawl_publications(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    publications = []

    # Find publications
    for pub in soup.select("h3.title a"):
        title = pub.get_text(strip=True)
        pub_url = urljoin(BASE_URL, pub["href"])

        print(f" Crawling publication: {title}")

        #Crawl publication page for abstract + fingerprints
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
# Main Runner
# -----------------------------
if __name__ == "__main__":

    start_url = "https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-electronics-and-mathematics/publications/"

    print(" Starting full crawler...\n")

    data = crawl_publications(start_url)

    #Save Output JSON
    with open("publications_with_details.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("\n Done! Saved as publications_with_details.json")
