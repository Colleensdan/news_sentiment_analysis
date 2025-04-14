import requests
import time
import os
import json
from config import HEADERS
from .base_scraper import BaseScraper

# File that stores the resume state.
RESUME_STATE_FILE = "resume_state.json"

def load_resume_state():
    """Load a dictionary mapping keywords to the next page number."""
    if os.path.exists(RESUME_STATE_FILE):
        with open(RESUME_STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_resume_state(state):
    """Save the resume state dictionary to a JSON file."""
    with open(RESUME_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

class GuardianScraper(BaseScraper):
    """
    Scraper for Guardian articles using its official Content API.
    This version resumes from the last reached page for each keyword and
    updates the resume_state.json even if errors occur (e.g., connection loss).
    """
    def __init__(self, api_key, from_date, to_date, keywords, page_size, max_pages=None):
        # max_pages is not used – we loop until no more articles are returned.
        super().__init__(api_key, from_date, to_date, keywords, page_size, max_pages)
        self.base_url = "https://content.guardianapis.com/search"

    def collect_headlines(self):
        # Load any saved resume state.
        resume_state = load_resume_state()
        all_headlines = []

        for keyword in self.keywords:
            print(f"Searching Guardian API for keyword: '{keyword}'...")
            # Start from a saved page if available; otherwise, start at 1.
            page = resume_state.get(keyword, 1)

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
                    if response.status_code == 429:
                        # Rate limit reached; save progress and exit the loop for this keyword.
                        print(f"Rate limit exceeded on keyword '{keyword}', page {page}.")
                        resume_state[keyword] = page
                        save_resume_state(resume_state)
                        break

                    if response.status_code != 200:
                        print(f"Error: Status code {response.status_code} on keyword '{keyword}', page {page}")
                        print("Response text:", response.text)
                        # Update resume state and exit on non-429 errors.
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
                        print(f"No more articles for '{keyword}' at page {page}.")
                        # Mark keyword as complete by resetting its resume value.
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
                    # Save progress after each successfully processed page.
                    resume_state[keyword] = page
                    save_resume_state(resume_state)
                    time.sleep(0.5)

                except Exception as e:
                    print(f"Exception on keyword '{keyword}', page {page}: {e}")
                    # In case of an unexpected error, save the current progress.
                    resume_state[keyword] = page
                    save_resume_state(resume_state)
                    break

        return self._deduplicate(all_headlines)

    def _deduplicate(self, headlines):
        deduped = {}
        for item in headlines:
            key = (item["source"], item["headline"], item["date"])
            deduped[key] = item
        deduped_headlines = list(deduped.values())
        print(f"Collected {len(deduped_headlines)} deduplicated Guardian headlines.")
        return deduped_headlines
