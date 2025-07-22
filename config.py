# Configuration file for Zomato Review Scraper

# File paths
INPUT_FILE = 'zomato.csv'
OUTPUT_FILE = 'zomato_reviews_from_urls.csv'
CHECKPOINT_FILE = 'scraping_checkpoint.json'
LOG_FILE = 'zomato_scraper.log'

# Scraping parameters
MAX_PAGES = 5  # Maximum pages to scrape per restaurant
DELAY_RANGE = (1, 3)  # Random delay between requests (min, max seconds)
MAX_RETRIES = 3  # Maximum retries for failed requests
TIMEOUT = 30  # Request timeout in seconds
CHUNK_SIZE = 10  # Save progress every N restaurants

# Headers to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Multiple CSS selectors for review extraction (fallback options)
REVIEW_SELECTORS = [
    'p.sc-1hez2tp-0.sc-hfLElm.hreYiP',  # Primary selector from HTML structure
    'p.sc-1hez2tp-0.hreYiP',             # Simplified version
    'p.hreYiP',                          # Even more simplified
    'div.sc-dgAbBl.ceFzZe p',            # Review container paragraph
    'section.sc-jOnSTu.cfrSOJ p',        # Review section paragraph
    'div[data-testid="review-text"]',    # Alternative selector
    'div.reviews-text',                  # Another alternative
    'p.review-text',                     # Generic fallback
    'div.review-content p',              # Nested content
    '[class*="review"] p',               # Class contains review
    'div[class*="review-text"]',         # More generic
    'p[class*="review"]',                # Paragraph with review in class
]

# Minimum review text length to filter out noise
MIN_REVIEW_LENGTH = 20

# Retry strategy for requests
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
RETRY_BACKOFF_FACTOR = 1
