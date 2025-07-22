import json
import re
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Any

class ZomatoJSParser:
    """Parser for extracting review data from Zomato's JavaScript payload"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_reviews_from_js(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract review data from JavaScript payload in HTML"""
        try:
            # Find the JavaScript containing the review data
            js_pattern = r'window\.__PRELOADED_STATE__\s*=\s*JSON\.parse\("([^"]+)"\);'
            match = re.search(js_pattern, html_content, re.DOTALL)
            
            if not match:
                print("No JavaScript state found")
                return []
            
            # Get the JSON string and unescape it
            js_data = match.group(1)
            # Unescape the JSON string
            js_data = js_data.replace('\\"', '"').replace('\\\\', '\\')
            
            # Parse the JSON data
            try:
                data = json.loads(js_data)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return []
            
            # Extract reviews from entities.REVIEWS
            reviews = []
            entities = data.get('entities', {})
            review_entities = entities.get('REVIEWS', {})
            
            for review_id, review_data in review_entities.items():
                if review_data.get('status') == 'success':
                    review_info = {
                        'review_id': review_data.get('reviewId'),
                        'review_text': review_data.get('reviewText', '').strip(),
                        'user_name': review_data.get('userName', ''),
                        'rating': review_data.get('ratingV2', ''),
                        'timestamp': review_data.get('timestamp', ''),
                        'experience': review_data.get('experience', ''),
                        'like_count': review_data.get('likeCount', 0),
                        'comment_count': review_data.get('commentCount', 0),
                        'review_url': review_data.get('reviewUrl', '')
                    }
                    
                    # Only add reviews with actual text content
                    if review_info['review_text']:
                        reviews.append(review_info)
            
            return reviews
            
        except Exception as e:
            print(f"Error extracting reviews from JavaScript: {e}")
            return []
    
    def get_reviews_from_url(self, url: str) -> List[Dict[str, Any]]:
        """Fetch page and extract reviews from JavaScript data"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return self.extract_reviews_from_js(response.text)
            
        except Exception as e:
            print(f"Error fetching reviews from {url}: {e}")
            return []

def test_js_parser():
    """Test the JavaScript parser with our debug HTML"""
    parser = ZomatoJSParser()
    
    # Test with our saved debug HTML
    try:
        with open('debug_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        reviews = parser.extract_reviews_from_js(html_content)
        
        print(f"Found {len(reviews)} reviews from JavaScript data:")
        print("=" * 50)
        
        for i, review in enumerate(reviews, 1):
            print(f"Review {i}:")
            print(f"  User: {review['user_name']}")
            print(f"  Rating: {review['rating']}")
            print(f"  Text: {review['review_text']}")
            print(f"  Time: {review['timestamp']}")
            print(f"  Experience: {review['experience']}")
            print(f"  Likes: {review['like_count']}")
            print(f"  URL: {review['review_url']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error testing JS parser: {e}")

if __name__ == "__main__":
    test_js_parser()
