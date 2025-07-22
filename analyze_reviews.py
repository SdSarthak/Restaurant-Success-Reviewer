#!/usr/bin/env python3
"""
Review Analysis Script

This script analyzes the scraped Zomato reviews and provides insights.
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
import numpy as np

class ReviewAnalyzer:
    """Analyzer for scraped reviews"""
    
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        self.df['review_length'] = self.df['review'].str.len()
        
    def basic_statistics(self):
        """Generate basic statistics about the reviews"""
        print("=== Basic Statistics ===")
        print(f"Total reviews: {len(self.df)}")
        print(f"Unique restaurants: {self.df['restaurant_url'].nunique()}")
        print(f"Average reviews per restaurant: {len(self.df) / self.df['restaurant_url'].nunique():.2f}")
        print(f"Average review length: {self.df['review_length'].mean():.2f} characters")
        print(f"Median review length: {self.df['review_length'].median():.2f} characters")
        print()
        
    def top_restaurants_by_reviews(self, n=10):
        """Show restaurants with most reviews"""
        print(f"=== Top {n} Restaurants by Review Count ===")
        top_restaurants = self.df['restaurant_url'].value_counts().head(n)
        for i, (url, count) in enumerate(top_restaurants.items(), 1):
            restaurant_name = url.split('/')[-1].replace('-', ' ').title()
            print(f"{i}. {restaurant_name}: {count} reviews")
        print()
        
    def review_length_distribution(self):
        """Analyze review length distribution"""
        print("=== Review Length Distribution ===")
        print(f"Min length: {self.df['review_length'].min()}")
        print(f"Max length: {self.df['review_length'].max()}")
        print(f"25th percentile: {self.df['review_length'].quantile(0.25):.2f}")
        print(f"75th percentile: {self.df['review_length'].quantile(0.75):.2f}")
        print()
        
    def sentiment_keywords(self):
        """Extract common positive and negative keywords"""
        print("=== Common Keywords Analysis ===")
        
        # Combine all reviews
        all_text = ' '.join(self.df['review'].astype(str).str.lower())
        
        # Remove common stop words and clean text
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        
        # Common positive words
        positive_words = ['good', 'great', 'excellent', 'amazing', 'delicious', 'tasty', 'awesome', 'wonderful', 'fantastic', 'perfect']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'disappointing', 'horrible', 'worst', 'pathetic', 'disgusting']
        
        word_counts = Counter(words)
        
        print("Top positive indicators:")
        for word in positive_words:
            count = word_counts.get(word, 0)
            if count > 0:
                print(f"  {word}: {count} mentions")
        
        print("\nTop negative indicators:")
        for word in negative_words:
            count = word_counts.get(word, 0)
            if count > 0:
                print(f"  {word}: {count} mentions")
        
        print(f"\nMost common words overall:")
        for word, count in word_counts.most_common(20):
            if len(word) > 3:  # Skip very short words
                print(f"  {word}: {count}")
        print()
        
    def generate_wordcloud(self, output_file='wordcloud.png'):
        """Generate a word cloud from reviews"""
        try:
            all_text = ' '.join(self.df['review'].astype(str))
            
            # Clean text
            all_text = re.sub(r'[^a-zA-Z\s]', '', all_text)
            all_text = re.sub(r'\s+', ' ', all_text)
            
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(all_text)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Most Common Words in Reviews')
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"Word cloud saved as {output_file}")
            
        except ImportError:
            print("WordCloud library not installed. Skipping word cloud generation.")
        except Exception as e:
            print(f"Error generating word cloud: {e}")
    
    def plot_review_distribution(self):
        """Plot review count distribution"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Reviews per restaurant
            plt.subplot(2, 2, 1)
            restaurant_counts = self.df['restaurant_url'].value_counts()
            plt.hist(restaurant_counts, bins=20, alpha=0.7, color='skyblue')
            plt.title('Distribution of Reviews per Restaurant')
            plt.xlabel('Number of Reviews')
            plt.ylabel('Number of Restaurants')
            
            # Review length distribution
            plt.subplot(2, 2, 2)
            plt.hist(self.df['review_length'], bins=30, alpha=0.7, color='lightgreen')
            plt.title('Distribution of Review Lengths')
            plt.xlabel('Review Length (characters)')
            plt.ylabel('Number of Reviews')
            
            # Reviews by page
            plt.subplot(2, 2, 3)
            if 'page' in self.df.columns:
                page_counts = self.df['page'].value_counts().sort_index()
                plt.bar(page_counts.index, page_counts.values, color='orange', alpha=0.7)
                plt.title('Reviews by Page Number')
                plt.xlabel('Page Number')
                plt.ylabel('Number of Reviews')
            
            # Review length vs page
            plt.subplot(2, 2, 4)
            if 'page' in self.df.columns:
                plt.boxplot([self.df[self.df['page'] == page]['review_length'] for page in sorted(self.df['page'].unique())])
                plt.title('Review Length by Page')
                plt.xlabel('Page Number')
                plt.ylabel('Review Length (characters)')
            
            plt.tight_layout()
            plt.savefig('review_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("Analysis plots saved as review_analysis.png")
            
        except ImportError:
            print("Matplotlib not installed. Skipping plot generation.")
        except Exception as e:
            print(f"Error generating plots: {e}")
    
    def export_summary_report(self, output_file='analysis_report.json'):
        """Export a summary report"""
        report = {
            'total_reviews': len(self.df),
            'unique_restaurants': self.df['restaurant_url'].nunique(),
            'avg_reviews_per_restaurant': len(self.df) / self.df['restaurant_url'].nunique(),
            'avg_review_length': self.df['review_length'].mean(),
            'median_review_length': self.df['review_length'].median(),
            'min_review_length': self.df['review_length'].min(),
            'max_review_length': self.df['review_length'].max(),
            'top_restaurants': self.df['restaurant_url'].value_counts().head(10).to_dict(),
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Summary report exported to {output_file}")

def main():
    """Main analysis function"""
    import sys
    
    csv_file = 'zomato_reviews_from_urls.csv'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    try:
        analyzer = ReviewAnalyzer(csv_file)
        
        print("Starting review analysis...")
        print("=" * 50)
        
        analyzer.basic_statistics()
        analyzer.top_restaurants_by_reviews()
        analyzer.review_length_distribution()
        analyzer.sentiment_keywords()
        analyzer.plot_review_distribution()
        analyzer.generate_wordcloud()
        analyzer.export_summary_report()
        
        print("=" * 50)
        print("Analysis complete!")
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        print("Make sure you have run the scraper first.")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
