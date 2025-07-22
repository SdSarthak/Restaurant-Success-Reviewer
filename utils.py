import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    """Utility class for data processing and analysis"""
    
    @staticmethod
    def clean_review_text(text: str) -> str:
        """Clean and normalize review text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common patterns that aren't useful
        patterns_to_remove = [
            'RATED\n',
            'Rated ',
            '\n',
            '\r',
            '\t'
        ]
        
        for pattern in patterns_to_remove:
            text = text.replace(pattern, ' ')
        
        # Remove extra spaces again
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def deduplicate_reviews(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate reviews based on text content"""
        seen_reviews = set()
        unique_reviews = []
        
        for review in reviews:
            review_text = review.get('review', '').strip()
            if review_text and review_text not in seen_reviews:
                seen_reviews.add(review_text)
                # Clean the review text
                review['review'] = DataProcessor.clean_review_text(review_text)
                unique_reviews.append(review)
        
        logger.info(f"Removed {len(reviews) - len(unique_reviews)} duplicate reviews")
        return unique_reviews
    
    @staticmethod
    def validate_reviews(reviews: List[Dict[str, Any]], min_length: int = 20) -> List[Dict[str, Any]]:
        """Validate and filter reviews based on quality criteria"""
        valid_reviews = []
        
        for review in reviews:
            review_text = review.get('review', '').strip()
            
            # Check minimum length
            if len(review_text) < min_length:
                continue
            
            # Check if it's not just whitespace or special characters
            if not review_text.replace(' ', '').replace('\n', '').replace('\t', ''):
                continue
            
            # Check if it contains actual words (not just punctuation)
            if not any(c.isalpha() for c in review_text):
                continue
            
            valid_reviews.append(review)
        
        logger.info(f"Filtered {len(reviews) - len(valid_reviews)} invalid reviews")
        return valid_reviews
    
    @staticmethod
    def generate_summary_stats(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for scraped reviews"""
        if not reviews:
            return {}
        
        # Count reviews per restaurant
        restaurant_counts = {}
        for review in reviews:
            url = review.get('restaurant_url', '')
            restaurant_counts[url] = restaurant_counts.get(url, 0) + 1
        
        # Calculate statistics
        total_restaurants = len(restaurant_counts)
        total_reviews = len(reviews)
        avg_reviews_per_restaurant = total_reviews / total_restaurants if total_restaurants > 0 else 0
        
        # Review length statistics
        review_lengths = [len(review.get('review', '')) for review in reviews]
        avg_review_length = sum(review_lengths) / len(review_lengths) if review_lengths else 0
        
        return {
            'total_restaurants': total_restaurants,
            'total_reviews': total_reviews,
            'avg_reviews_per_restaurant': round(avg_reviews_per_restaurant, 2),
            'avg_review_length': round(avg_review_length, 2),
            'min_review_length': min(review_lengths) if review_lengths else 0,
            'max_review_length': max(review_lengths) if review_lengths else 0,
            'restaurants_with_most_reviews': max(restaurant_counts.items(), key=lambda x: x[1]) if restaurant_counts else None
        }
    
    @staticmethod
    def save_processed_data(reviews: List[Dict[str, Any]], output_file: str) -> None:
        """Save processed reviews to CSV with additional metadata"""
        if not reviews:
            logger.warning("No reviews to save")
            return
        
        df = pd.DataFrame(reviews)
        
        # Add processing metadata
        df['processed_at'] = datetime.now().isoformat()
        df['review_length'] = df['review'].str.len()
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(reviews)} processed reviews to {output_file}")
        
        # Save summary statistics
        stats = DataProcessor.generate_summary_stats(reviews)
        stats_file = output_file.replace('.csv', '_stats.json')
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved summary statistics to {stats_file}")

class CheckpointManager:
    """Manages scraping progress and checkpoints"""
    
    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
    
    def save_checkpoint(self, processed_urls: List[str], all_reviews: List[Dict[str, Any]]) -> None:
        """Save progress to checkpoint file"""
        checkpoint = {
            'processed_urls': processed_urls,
            'total_reviews': len(all_reviews),
            'timestamp': datetime.now().isoformat(),
            'last_processed': processed_urls[-1] if processed_urls else None
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        logger.info(f"Checkpoint saved: {len(processed_urls)} URLs processed, {len(all_reviews)} reviews collected")
    
    def load_checkpoint(self) -> List[str]:
        """Load progress from checkpoint file"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                processed_urls = checkpoint.get('processed_urls', [])
                logger.info(f"Checkpoint loaded: {len(processed_urls)} URLs already processed")
                return processed_urls
            except Exception as e:
                logger.error(f"Error loading checkpoint: {e}")
                return []
        return []
    
    def clear_checkpoint(self) -> None:
        """Clear the checkpoint file"""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            logger.info("Checkpoint cleared")
