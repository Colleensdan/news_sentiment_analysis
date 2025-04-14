import requests
import time
import os
import json
from config import HEADERS
from .base_scraper import BaseScraper
from resume_state import load_resume_state, save_resume_state

class GuardianScraper(BaseScraper):
    """
    Scraper for Guardian articles using its official Content API.
    This version accepts a list of API keys and rotates to the next key
    if one reaches its rate limit. It also updates the resume_state.json
    file so that on subsequent runs it resumes where it left off.
    """
    def __init__(self, api_keys, from_date, to_date, keywords, page_size, max_pages=None):
        # max_pages is not used – we loop until no more articles are returned.
        self.api_keys = api_keys
        self.current_key_index = 0  # Start with the first key.
        super().__init__(self.current_api_key(), from_date, to_date, keywords, page_size, max_pages)
        self.base_url = "https://content.guardianapis.com/search"

    def current_api_key(self):
        if self.api_keys:
            return self.api_keys[self.current_key_index]
        return None

    def rotate_api_key(self):
        """
        Rotate to the next API key if available. Returns True if successful, or False if no keys remain.
        """
        if self.current_key_index < len(self.api_keys) - 1:
            self.current_key_index += 1
            print(f"Rotating to API key: {self.current_api_key()}")
            return True
        print("No more API keys available.")
        return False

    def collect_headlines(self):
        resume_state = load_resume_state()
        all_headlines = []
        for keyword in self.keywords:
            print(f"Searching Guardian API for keyword: '{keyword}'...")
            # Start at the page stored for this keyword, or at page 1 if no state exists.
            page = resume_state.get(keyword, 1)
            while True:
                params = {
                    "q": keyword,
                    "from-date": self.from_date.isoformat(),
                    "to-date": self.to_date.isoformat(),
                    "page": page,
                    "api-key": self.current_api_key()
                }
                try:
                    response = requests.get(self.base_url, params=params, headers=HEADERS, timeout=10)
                except Exception as e:
                    print(f"Error on keyword '{keyword}', page {page}: {e}")
                    resume_state[keyword] = page
                    save_resume_state(resume_state)
                    break

                if response.status_code == 429:
                    print(f"Rate limit exceeded on keyword '{keyword}', page {page} using key {self.current_api_key()}.")
                    if self.rotate_api_key():
                        # Retry the same page with the new key.
                        continue
                    else:
                        # If no API keys remain, save progress and return collected headlines.
                        resume_state[keyword] = page
                        save_resume_state(resume_state)
                        break

                if response.status_code != 200:
                    print(f"Error: Status code {response.status_code} on keyword '{keyword}', page {page}")
                    print("Response text:", response.text)
                    resume_state[keyword] = page
                    save_resume_state(resume_state)
                    break

                data = response.json()
                if data.get("response", {}).get("status") != "ok":
                    print(f"Error: Guardian API status not ok for keyword '{keyword}'.")
                    print("Message:", data.get("response", {}).get("message"))
                    resume_state[keyword] = page
                    save_resume_state(resume_state)
                    break

                articles = data.get("response", {}).get("results", [])
                if not articles:
                    print(f"No more articles found for '{keyword}' at page {page}.")
                    # Reset state for this keyword, indicating it's complete.
                    resume_state[keyword] = 1
                    save_resume_state(resume_state)
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
                resume_state[keyword] = page
                save_resume_state(resume_state)
                time.sleep(0.5)

        return self._deduplicate(all_headlines)

    def _deduplicate(self, headlines):
        deduped = {(item["source"], item["headline"], item["date"]): item for item in headlines}
        deduped_headlines = list(deduped.values())
        print(f"Collected {len(deduped_headlines)} deduplicated Guardian headlines.")
        return deduped_headlines
