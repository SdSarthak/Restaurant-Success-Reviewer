#!/usr/bin/env python3
"""
Debug script to test review extraction selectors
"""

import requests
from bs4 import BeautifulSoup
import time
from config import REVIEW_SELECTORS, HEADERS

def debug_review_extraction(url):
    """Debug review extraction for a specific URL"""
    print(f"Testing URL: {url}")
    print("=" * 80)
    
    # Create session
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        # Get the review page
        if not url.endswith('/reviews'):
            if url.endswith('/'):
                url = url[:-1]
            url = url + "/reviews"
        
        print(f"Fetching: {url}")
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch URL, status code: {response.status_code}")
            return
        
        print(f"✅ Successfully fetched URL (status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"\nTesting {len(REVIEW_SELECTORS)} selectors:")
        print("-" * 50)
        
        # Test each selector
        for i, selector in enumerate(REVIEW_SELECTORS, 1):
            print(f"\n{i}. Selector: {selector}")
            
            try:
                elements = soup.select(selector)
                print(f"   Found {len(elements)} elements")
                
                if elements:
                    # Show first few review texts
                    for j, element in enumerate(elements[:3]):
                        text = element.get_text(strip=True)
                        if text:
                            print(f"   Review {j+1}: {text[:100]}{'...' if len(text) > 100 else ''}")
                        else:
                            print(f"   Review {j+1}: [EMPTY]")
                    
                    if len(elements) > 3:
                        print(f"   ... and {len(elements) - 3} more")
                    
                    # This selector worked, so we can stop here
                    print(f"\n✅ SUCCESS: Selector {i} found {len(elements)} reviews!")
                    break
                else:
                    print("   No elements found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Also check for common review container patterns
        print(f"\nChecking for common review containers:")
        print("-" * 50)
        
        # Look for elements that might contain reviews
        potential_containers = [
            'div[class*="review"]',
            'section[class*="review"]',
            'p[class*="review"]',
            'div[class*="comment"]',
            'p[class*="comment"]',
            'div[class*="content"]',
            'p[class*="content"]'
        ]
        
        for container in potential_containers:
            try:
                elements = soup.select(container)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {container}")
                    
                    # Show some sample content
                    for element in elements[:2]:
                        text = element.get_text(strip=True)
                        if text and len(text) > 10:
                            print(f"  Sample: {text[:80]}{'...' if len(text) > 80 else ''}")
            except:
                pass
        
        # Save HTML for manual inspection
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n📄 Full HTML saved to 'debug_page.html' for manual inspection")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")

def main():
    """Main debug function"""
    # Test with a specific URL from the logs
    test_url = "https://www.zomato.com/bangalore/smacznego-banashankari"
    
    print("🔍 Debugging Zomato Review Extraction")
    print("=" * 80)
    
    debug_review_extraction(test_url)
    
    print("\n" + "=" * 80)
    print("Debug completed!")

if __name__ == "__main__":
    main()
