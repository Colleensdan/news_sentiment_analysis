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

GUARDIAN_API_KEYS = [
    "e1fb2aa1-9bd9-4040-87c2-adca1ec50d90",
    "256058c7-a1e5-4837-a3df-69ccaf188e3a",
    "a6e87b73-600f-4568-8b1a-3a8d94c8018e",
    "c34a54b9-ed12-461e-a0ac-bd405c6a7901",
    "8d29adb8-b600-47a9-acaa-d01173fa67d1",
    "c2fe8fb7-b745-4306-b98c-ae6423225ea3",
    "a6c40808-9165-4144-bbf7-b919082fb1ea",
    "50d04fd6-2b9b-40d0-a768-61c6c8c88e84",
    "13092b99-417f-4e21-ba5a-7f45832262bf",
    "b0607095-23ef-4eb8-bb1c-5168074b1def",
    "5734d153-36fe-492e-99e9-7722d25d542a",
    "be656869-fdc3-4121-b462-145e8abde561",
    "1b797eb5-1f4b-4226-a515-6687ad1570f0",
    "504f1f13-fc21-448c-a243-9c598b7b3f3a",
    "27ce3dee-2e57-454c-b059-62bf7b636227",
    "d045e29a-179e-480c-a904-e9546d8346ce",
    "b3fd1b14-f404-49c3-b83a-6b9c437f2342",
    "c2dd35e6-c518-46b1-914c-5e884f28fb34",
    "e0d52e36-c479-4458-8ec1-e636471800b2",
    "18cb2e7f-8dfa-4bbb-8ec4-e25cb0b918d8",
    "0b7c756d-88a8-4874-996c-c55f6d1f4d9d",
    "45b4ece0-24b4-44a8-aaec-49382c9dbcae",
    "e0357903-c241-4a96-a7dc-23e76b1ddf41",
    "9270dc2f-3b29-429b-a2d9-2d6b34d22b89",
    "57f0ea63-20a8-4e9e-be0e-c64a07fdbd2e",
    "2771f3a7-d62a-445e-a641-d66366f037fe",
    "66915e9a-0629-49df-9fa4-94adf1f42b26",
    "e5ccf11a-7aeb-4100-ab51-6993e5ce4141",
    "3fc88ce4-082c-40ad-9f52-9b7477558ecc",
    "bedf3be9-d647-478e-96b2-36d48cd19a46",
    "79f8f9f1-3a42-4ac5-b178-07b42c0b34bf",
    "2898a3e0-2df9-4504-8536-67cc94815d18",
    "667d197a-5f9e-4a11-9891-df2775819d25",
    "91a21a6f-573a-47a4-a9ee-d2fde65895c0",
    "f578f6ff-dc3e-423f-b17b-181e7fefb931",
    "d9b829ab-9f6a-43ab-8d35-019f61c98dbd",
    "0efc3a25-ad9b-4e23-ab19-a49f49010f6f",
    "8025dcef-d6dd-4138-aaa8-d4567723908c",
    "841f38ea-c22d-44ae-9cdd-0daeea6d9c47",
    "3c24e395-aa2f-4b94-b62d-f2841989f1eb",
    "f7a8b646-7e8a-4aab-90bc-bc7e25f42e8e",
    "181e9c71-e3b6-48f2-bc11-95d3cb7effc9",
    "07018bce-410d-4cf4-992a-32197e95127e",
    "f0a39c1f-410b-4e0f-b2c9-b6fa6d1b4a33",
    "69ec5a4b-3365-4281-be5f-05e9da3a6aea",
    "82ec5893-2b2c-4916-9226-24c748f6a2f3",
    "9a9efced-4b53-4c37-9ac8-e4e9cda42cb8",
    "911e45c8-d42c-4689-af32-c3f422c866c3",
    "6a98b76f-525a-4709-b975-79384d012df2",
    "65c49eee-760c-416f-80be-0931b1814422",
    "bbbce202-236c-4152-9168-e9bf91868211",
    "00090a97-ed8d-4f76-894e-53288708ed99",
    "7147a944-cc5a-4a96-ae2e-533503bec242",
    "f9f92036-273d-4994-aa1b-d5a59814adff"
]


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
