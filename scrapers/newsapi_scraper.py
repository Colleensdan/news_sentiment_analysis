# scrapers/newsapi_scraper.py
import requests
import time
from config import HEADERS
from .base_scraper import BaseScraper

class NewsAPIScraper(BaseScraper):
    """
    General scraper using NewsAPI's 'everything' endpoint, with debugging output.
    """
    def __init__(self, api_key, from_date, to_date, keywords, page_size, max_pages=None):
        super().__init__(api_key, from_date, to_date, keywords, page_size, max_pages)
        self.base_url = "https://newsapi.org/v2/everything"

    def collect_headlines(self):
        all_headlines = []
        for keyword in self.keywords:
            print(f"Searching NewsAPI for keyword: '{keyword}'...")
            page = 1
            while True:
                params = {
                    "q": keyword,
                    "from": self.from_date.isoformat(),
                    "to": self.to_date.isoformat(),
                    "pageSize": self.page_size,
                    "page": page,
                    "apiKey": self.api_key,
                    "language": "en"
                }
                try:
                    response = requests.get(self.base_url, params=params, timeout=10)
                except Exception as e:
                    print(f"Request error for keyword '{keyword}', page {page}: {e}")
                    break

                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code} for keyword '{keyword}', page {page}")
                    print("Response text:", response.text)
                    break

                data = response.json()
                if data.get("status") != "ok":
                    print(f"Error: API status not ok for keyword '{keyword}'. Message: {data.get('message')}")
                    break

                articles = data.get("articles", [])
                if not articles:
                    print(f"No more articles found for '{keyword}' on page {page}.")
                    break

                for art in articles:
                    headline = art.get("title", "").strip()
                    published_at = art.get("publishedAt")
                    source_name = art.get("source", {}).get("name", "Unknown")
                    all_headlines.append({
                        "source": source_name,
                        "headline": headline,
                        "date": published_at.split("T")[0] if published_at else None,
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
        print(f"Collected {len(deduped_headlines)} deduplicated headlines across {len(self.keywords)} keywords.")
        return deduped_headlines
