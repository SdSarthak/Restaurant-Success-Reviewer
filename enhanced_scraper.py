#!/usr/bin/env python3
"""
Enhanced Zomato Review Scraper

This script scrapes restaurant reviews from Zomato URLs provided in a CSV file.
It includes robust error handling, progress tracking, and data validation.

Features:
- Resume capability with checkpoint system
- Multiple CSS selector fallbacks
- Proper logging and error handling
- Data validation and deduplication
- Progress tracking and statistics
- Configurable parameters
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
import os
import sys
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
from typing import List, Dict, Any

# Import local modules
try:
    from config import *
    from utils import DataProcessor, CheckpointManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure config.py and utils.py are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZomatoReviewScraper:
    """Main scraper class for Zomato reviews"""
    
    def __init__(self):
        self.session = self._create_session()
        self.checkpoint_manager = CheckpointManager(CHECKPOINT_FILE)
        self.data_processor = DataProcessor()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(HEADERS)
        return session
    
    def _get_review_url(self, restaurant_url: str) -> str:
        """Convert restaurant URL to review URL"""
        if restaurant_url.endswith('/'):
            restaurant_url = restaurant_url[:-1]
        return restaurant_url + "/reviews"
    
    def _extract_reviews(self, soup: BeautifulSoup) -> List[str]:
        """Extract reviews using multiple CSS selectors as fallback"""
        reviews = []
        
        for selector in REVIEW_SELECTORS:
            try:
                review_blocks = soup.select(selector)
                
                if review_blocks:
                    for block in review_blocks:
                        text = block.get_text(strip=True)
                        if text and len(text) > MIN_REVIEW_LENGTH:
                            reviews.append(text)
                    
                    logger.info(f"Found {len(review_blocks)} reviews using selector: {selector}")
                    break
                    
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
                continue
        
        return reviews
    
    def _scrape_restaurant_reviews(self, restaurant_url: str) -> List[Dict[str, Any]]:
        """Scrape reviews for a single restaurant"""
        review_url = self._get_review_url(restaurant_url)
        restaurant_reviews = []
        
        try:
            for page in range(1, MAX_PAGES + 1):
                full_url = f"{review_url}?page={page}"
                
                try:
                    # Random delay to be respectful
                    delay = random.uniform(*DELAY_RANGE)
                    time.sleep(delay)
                    
                    response = self.session.get(full_url, timeout=TIMEOUT)
                    
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch {full_url}, status code: {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_reviews = self._extract_reviews(soup)
                    
                    if not page_reviews:
                        logger.info(f"No reviews found on page {page} for {restaurant_url}")
                        break
                    
                    # Add reviews with metadata
                    for review_text in page_reviews:
                        restaurant_reviews.append({
                            'restaurant_url': restaurant_url,
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
            logger.error(f"Error processing restaurant {restaurant_url}: {e}")
        
        return restaurant_reviews
    
    def scrape_all_reviews(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape reviews from all restaurant URLs"""
        all_reviews = []
        processed_urls = self.checkpoint_manager.load_checkpoint()
        
        logger.info(f"Starting to scrape {len(urls)} restaurants")
        
        for i, res_url in enumerate(urls):
            # Skip if already processed
            if res_url in processed_urls:
                logger.info(f"Skipping already processed URL: {res_url}")
                continue
            
            logger.info(f"Processing {i+1}/{len(urls)}: {res_url}")
            
            # Scrape restaurant reviews
            restaurant_reviews = self._scrape_restaurant_reviews(res_url)
            all_reviews.extend(restaurant_reviews)
            processed_urls.append(res_url)
            
            logger.info(f"Completed {res_url}: {len(restaurant_reviews)} reviews collected")
            
            # Save checkpoint periodically
            if (i + 1) % CHUNK_SIZE == 0:
                self.checkpoint_manager.save_checkpoint(processed_urls, all_reviews)
                
                # Save intermediate results
                if all_reviews:
                    temp_df = pd.DataFrame(all_reviews)
                    temp_file = f"temp_{OUTPUT_FILE}"
                    temp_df.to_csv(temp_file, index=False)
                    logger.info(f"Saved intermediate results: {len(all_reviews)} reviews")
        
        # Final checkpoint save
        self.checkpoint_manager.save_checkpoint(processed_urls, all_reviews)
        
        return all_reviews
    
    def run(self):
        """Main execution method"""
        logger.info("Starting Zomato Review Scraper")
        
        # Read input CSV
        try:
            df = pd.read_csv(INPUT_FILE)
            urls = df['url'].dropna().unique().tolist()
            logger.info(f"Successfully loaded {len(urls)} unique URLs from {INPUT_FILE}")
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return
        
        # Scrape all reviews
        all_reviews = self.scrape_all_reviews(urls)
        
        if not all_reviews:
            logger.warning("No reviews were collected!")
            return
        
        # Process and validate data
        logger.info("Processing and validating scraped data...")
        all_reviews = self.data_processor.validate_reviews(all_reviews, MIN_REVIEW_LENGTH)
        all_reviews = self.data_processor.deduplicate_reviews(all_reviews)
        
        # Save final results
        self.data_processor.save_processed_data(all_reviews, OUTPUT_FILE)
        
        # Generate and display summary
        stats = self.data_processor.generate_summary_stats(all_reviews)
        logger.info(f"""
        ✅ Scraping completed successfully!
        
        Summary Statistics:
        - Total restaurants processed: {stats.get('total_restaurants', 0)}
        - Total reviews collected: {stats.get('total_reviews', 0)}
        - Average reviews per restaurant: {stats.get('avg_reviews_per_restaurant', 0)}
        - Average review length: {stats.get('avg_review_length', 0)} characters
        - Output file: {OUTPUT_FILE}
        - Log file: {LOG_FILE}
        """)
        
        # Clean up temporary files
        temp_file = f"temp_{OUTPUT_FILE}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info("Cleaned up temporary files")

def main():
    """Main entry point"""
    scraper = ZomatoReviewScraper()
    scraper.run()

if __name__ == "__main__":
    main()
