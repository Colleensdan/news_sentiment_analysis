# config.py
import datetime

# Static current date: 14 April 2025
CURRENT_DATE = datetime.date(2025, 4, 14)

INCLUSION_KEYWORDS = [
    "*phone*", "screens", "telephones", "smartphones",
    "social media", "TikTok", "Instagram", "Facebook",
    "reels", "scrolling", "doomscrolling", "brainrot",
    "mobile", "cellphone", "Snapchat", "Twitter", "apps", "WhatsApp"
]

NEWSAPI_API_KEY = "ebe149e99aaf412e8369c354467455d0"
GUARDIAN_API_KEY = "256058c7-a1e5-4837-a3df-69ccaf188e3a"

# Configuration for NewsAPI scraper.
NEWSAPI_CONFIG = {
    "base_url": "https://newsapi.org/v2/everything",
    "page_size": 100,
    # Remove the fixed max_pages limit—instead, we'll loop until no articles are returned.
    # "max_pages": 3,
    "days_range": 5 * 365  # Last 5 years in days.
}

# Configuration for Guardian scraper.
# (This mode uses the official Guardian API exclusively—not web scraping.)
GUARDIAN_CONFIG = {
    "base_url": "https://content.guardianapis.com/search",
    # "max_pages": 3,
    "days_range": 5 * 365
}

# Database configuration.
DB_NAME = "headlines.db"

# HTTP Headers for requests.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Helper function to compute date range (last 5 years)
def get_date_range():
    today = CURRENT_DATE  # Use our fixed current date.
    start_date = today - datetime.timedelta(days=5 * 365)
    return start_date, today
