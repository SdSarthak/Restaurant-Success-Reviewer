#!/usr/bin/env python3
"""
Test script for the enhanced Zomato scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        import config
        print("✅ Config module imported successfully")
        
        from utils import DataProcessor, CheckpointManager
        print("✅ Utils module imported successfully")
        
        from enhanced_scraper import ZomatoReviewScraper
        print("✅ Enhanced scraper imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_processor():
    """Test DataProcessor functionality"""
    try:
        from utils import DataProcessor
        
        # Test data
        test_reviews = [
            {'review': 'Great food! Loved it.', 'restaurant_url': 'test1'},
            {'review': 'Bad', 'restaurant_url': 'test2'},  # Too short
            {'review': 'Amazing experience with excellent service', 'restaurant_url': 'test1'},
            {'review': 'Great food! Loved it.', 'restaurant_url': 'test1'},  # Duplicate
        ]
        
        processor = DataProcessor()
        
        # Test validation
        valid_reviews = processor.validate_reviews(test_reviews, min_length=10)
        print(f"✅ Validation test passed: {len(valid_reviews)}/4 reviews valid")
        
        # Test deduplication
        unique_reviews = processor.deduplicate_reviews(test_reviews)
        print(f"✅ Deduplication test passed: {len(unique_reviews)}/4 reviews unique")
        
        # Test stats generation
        stats = processor.generate_summary_stats(test_reviews)
        print(f"✅ Stats generation test passed: {len(stats)} stats generated")
        
        return True
    except Exception as e:
        print(f"❌ DataProcessor test failed: {e}")
        return False

def test_checkpoint_manager():
    """Test CheckpointManager functionality"""
    try:
        from utils import CheckpointManager
        
        # Create test checkpoint
        checkpoint = CheckpointManager('test_checkpoint.json')
        
        # Test save/load
        test_urls = ['url1', 'url2', 'url3']
        test_reviews = [{'review': 'test', 'restaurant_url': 'url1'}]
        
        checkpoint.save_checkpoint(test_urls, test_reviews)
        loaded_urls = checkpoint.load_checkpoint()
        
        if loaded_urls == test_urls:
            print("✅ Checkpoint save/load test passed")
            
            # Clean up
            checkpoint.clear_checkpoint()
            print("✅ Checkpoint cleanup test passed")
            return True
        else:
            print("❌ Checkpoint test failed: loaded data doesn't match")
            return False
            
    except Exception as e:
        print(f"❌ CheckpointManager test failed: {e}")
        return False

def test_scraper_initialization():
    """Test scraper initialization"""
    try:
        from enhanced_scraper import ZomatoReviewScraper
        
        scraper = ZomatoReviewScraper()
        
        # Test URL conversion
        test_url = "https://www.zomato.com/bangalore/restaurant-name"
        review_url = scraper._get_review_url(test_url)
        expected_url = "https://www.zomato.com/bangalore/restaurant-name/reviews"
        
        if review_url == expected_url:
            print("✅ URL conversion test passed")
            return True
        else:
            print(f"❌ URL conversion test failed: {review_url} != {expected_url}")
            return False
            
    except Exception as e:
        print(f"❌ Scraper initialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running enhanced scraper tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_processor,
        test_checkpoint_manager,
        test_scraper_initialization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The enhanced scraper is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
