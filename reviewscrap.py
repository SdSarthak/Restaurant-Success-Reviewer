import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
import json
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zomato_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'input_file': 'zomato.csv',
    'output_file': 'zomato_reviews_from_urls.csv',
    'checkpoint_file': 'scraping_checkpoint.json',
    'max_pages': 5,  # Increased from 3
    'delay_range': (1, 3),  # Random delay between requests
    'max_retries': 3,
    'timeout': 30,
    'chunk_size': 10  # Save progress every 10 restaurants
}

# Enhanced headers to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# STEP 1: Read CSV with error handling
try:
    df = pd.read_csv(CONFIG['input_file'])
    urls = df['url'].dropna().unique().tolist()
    logger.info(f"Successfully loaded {len(urls)} unique URLs from {CONFIG['input_file']}")
except Exception as e:
    logger.error(f"Error reading CSV file: {e}")
    raise

# STEP 2: Enhanced URL processing function
def get_review_url(restaurant_url):
    """Convert restaurant URL to review URL"""
    if restaurant_url.endswith('/'):
        restaurant_url = restaurant_url[:-1]
    return restaurant_url + "/reviews"

# STEP 3: Setup session with retry strategy
def create_session():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=CONFIG['max_retries'],
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

# STEP 4: Progress tracking functions
def save_checkpoint(processed_urls, all_reviews):
    """Save progress to checkpoint file"""
    checkpoint = {
        'processed_urls': processed_urls,
        'total_reviews': len(all_reviews),
        'timestamp': datetime.now().isoformat()
    }
    with open(CONFIG['checkpoint_file'], 'w') as f:
        json.dump(checkpoint, f)
    logger.info(f"Checkpoint saved: {len(processed_urls)} URLs processed, {len(all_reviews)} reviews collected")

def load_checkpoint():
    """Load progress from checkpoint file"""
    if os.path.exists(CONFIG['checkpoint_file']):
        with open(CONFIG['checkpoint_file'], 'r') as f:
            checkpoint = json.load(f)
        logger.info(f"Checkpoint loaded: {len(checkpoint['processed_urls'])} URLs already processed")
        return checkpoint['processed_urls']
    return []

# STEP 5: Enhanced review extraction with multiple selectors
def extract_reviews(soup):
    """Extract reviews using multiple CSS selectors as fallback"""
    review_selectors = [
        'p.sc-1hez2tp-0.sc-hfLElm.hreYiP',  # Current selector
        'div[data-testid="review-text"]',    # Alternative selector
        'div.reviews-text',                  # Another alternative
        'p.review-text',                     # Generic fallback
        'div.review-content p',              # Nested content
        '[class*="review"] p',               # Class contains review
    ]
    
    reviews = []
    for selector in review_selectors:
        try:
            if '.' in selector and not selector.startswith('['):
                # CSS class selector
                review_blocks = soup.select(selector)
            else:
                # Other selector types
                review_blocks = soup.select(selector)
            
            if review_blocks:
                for block in review_blocks:
                    text = block.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out very short text
                        reviews.append(text)
                logger.info(f"Found {len(review_blocks)} reviews using selector: {selector}")
                break
        except Exception as e:
            logger.warning(f"Error with selector {selector}: {e}")
            continue
    
    return reviews

all_reviews = []
processed_urls = load_checkpoint()
session = create_session()

# STEP 6: Main scraping loop with enhanced error handling
for i, res_url in enumerate(urls):
    # Skip if already processed
    if res_url in processed_urls:
        logger.info(f"Skipping already processed URL: {res_url}")
        continue
    
    review_url = get_review_url(res_url)
    logger.info(f"Processing {i+1}/{len(urls)}: {review_url}")
    
    restaurant_reviews = []
    
    try:
        for page in range(1, CONFIG['max_pages'] + 1):
            full_url = f"{review_url}?page={page}"
            
            try:
                # Random delay to be respectful
                delay = random.uniform(*CONFIG['delay_range'])
                time.sleep(delay)
                
                response = session.get(full_url, timeout=CONFIG['timeout'])
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {full_url}, status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_reviews = extract_reviews(soup)
                
                if not page_reviews:
                    logger.info(f"No reviews found on page {page} for {res_url}")
                    break
                
                # Add reviews with metadata
                for review_text in page_reviews:
                    restaurant_reviews.append({
                        'restaurant_url': res_url,
                        'page': page,
                        'review': review_text,
                        'scraped_at': datetime.now().isoformat()
                    })
                
                logger.info(f"Extracted {len(page_reviews)} reviews from page {page}")
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout for {full_url}")
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {full_url}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error processing {full_url}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Error processing restaurant {res_url}: {e}")
        continue
    
    # Add restaurant reviews to main list
    all_reviews.extend(restaurant_reviews)
    processed_urls.append(res_url)
    
    logger.info(f"Completed {res_url}: {len(restaurant_reviews)} reviews collected")
    
    # Save checkpoint periodically
    if (i + 1) % CONFIG['chunk_size'] == 0:
        save_checkpoint(processed_urls, all_reviews)
        
        # Save intermediate results
        if all_reviews:
            temp_df = pd.DataFrame(all_reviews)
            temp_df.to_csv(f"temp_{CONFIG['output_file']}", index=False)
            logger.info(f"Saved intermediate results: {len(all_reviews)} reviews")

# STEP 7: Final save and cleanup
logger.info("Scraping completed. Saving final results...")
save_checkpoint(processed_urls, all_reviews)

if all_reviews:
    result_df = pd.DataFrame(all_reviews)
    result_df.to_csv(CONFIG['output_file'], index=False)
    logger.info(f"✅ Scraping completed! {len(all_reviews)} reviews saved to {CONFIG['output_file']}")
    
    # Clean up temporary files
    temp_file = f"temp_{CONFIG['output_file']}"
    if os.path.exists(temp_file):
        os.remove(temp_file)
else:
    logger.warning("No reviews were collected!")

# STEP 8: Summary statistics
if all_reviews:
    unique_restaurants = len(set(review['restaurant_url'] for review in all_reviews))
    avg_reviews_per_restaurant = len(all_reviews) / unique_restaurants if unique_restaurants > 0 else 0
    
    logger.info(f"""
    Scraping Summary:
    - Total restaurants processed: {len(processed_urls)}
    - Total reviews collected: {len(all_reviews)}
    - Unique restaurants with reviews: {unique_restaurants}
    - Average reviews per restaurant: {avg_reviews_per_restaurant:.2f}
    - Output file: {CONFIG['output_file']}
    """)
