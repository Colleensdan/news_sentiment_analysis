# scrapers/guardian_scraper.py
import requests
import time
from config import HEADERS
from .base_scraper import BaseScraper

class GuardianScraper(BaseScraper):
    """
    Scraper for Guardian articles using its official Content API.
    """
    def __init__(self, api_key, from_date, to_date, keywords, page_size, max_pages=None):
        # max_pages is not used now – we loop until empty.
        super().__init__(api_key, from_date, to_date, keywords, page_size, max_pages)
        self.base_url = "https://content.guardianapis.com/search"

    def collect_headlines(self):
        all_headlines = []
        for keyword in self.keywords:
            print(f"Searching Guardian API for keyword: '{keyword}'...")
            page = 1
            while True:
                params = {
                    "q": keyword,
                    "from-date": self.from_date.isoformat(),
                    "to-date": self.to_date.isoformat(),
                    "page": page,
                    "api-key": self.api_key
                }
                try:
                    response = requests.get(self.base_url, params=params, headers=HEADERS, timeout=10)
                except Exception as e:
                    print(f"Error on keyword '{keyword}', page {page}: {e}")
                    break

                if response.status_code != 200:
                    print(f"Error: Status code {response.status_code} on keyword '{keyword}', page {page}")
                    print("Response text:", response.text)
                    break

                data = response.json()
                if data.get("response", {}).get("status") != "ok":
                    print(f"Error: API status not ok for keyword '{keyword}'. Message: {data.get('message')}")
                    break

                articles = data.get("response", {}).get("results", [])
                if not articles:
                    break

                for art in articles:
                    headline = art.get("webTitle", "").strip()
                    pub_date = art.get("webPublicationDate", None)
                    all_headlines.append({
                        "source": "The Guardian",
                        "headline": headline,
                        "date": pub_date.split("T")[0] if pub_date else None,
                        "accessible": True
                    })
                print(f"Retrieved {len(articles)} articles on page {page} for keyword '{keyword}'.")
                page += 1
                time.sleep(0.5)
        # Deduplicate headlines.
        deduped = {}
        for item in all_headlines:
            key = (item["source"], item["headline"], item["date"])
            deduped[key] = item
        deduped_headlines = list(deduped.values())
        print(f"Collected {len(deduped_headlines)} deduplicated Guardian headlines.")
        return deduped_headlines
