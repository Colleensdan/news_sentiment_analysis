# scrapers/base_scraper.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, api_key, from_date, to_date, keywords, page_size, max_pages):
        self.api_key = api_key
        self.from_date = from_date
        self.to_date = to_date
        self.keywords = keywords
        self.page_size = page_size
        self.max_pages = max_pages

    @abstractmethod
    def collect_headlines(self):
        """Scrape headlines given the parameters."""
        pass
