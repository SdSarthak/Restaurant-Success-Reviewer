# Zomato Restaurant Review Scraper

A robust and efficient web scraper for extracting restaurant reviews from Zomato URLs. This project includes comprehensive error handling, progress tracking, data validation, and analysis capabilities.

## Features

### Core Scraping Features
- ✅ **Resume Capability**: Automatically resumes from where it left off if interrupted
- ✅ **Multiple CSS Selectors**: Fallback selectors to handle Zomato layout changes
- ✅ **Robust Error Handling**: Comprehensive error handling for network issues
- ✅ **Progress Tracking**: Real-time progress monitoring with checkpoints
- ✅ **Data Validation**: Filters out invalid or duplicate reviews
- ✅ **Configurable Parameters**: Easy configuration through separate config file
- ✅ **Proper Logging**: Detailed logging for debugging and monitoring
- ✅ **Rate Limiting**: Respectful delays between requests

### Data Processing Features
- ✅ **Deduplication**: Removes duplicate reviews automatically
- ✅ **Text Cleaning**: Normalizes and cleans review text
- ✅ **Quality Filtering**: Filters out low-quality reviews
- ✅ **Statistics Generation**: Comprehensive statistics about scraped data
- ✅ **Multiple Output Formats**: CSV output with metadata

### Analysis Features
- ✅ **Basic Statistics**: Review counts, lengths, distributions
- ✅ **Sentiment Analysis**: Keyword-based sentiment indicators
- ✅ **Data Visualization**: Charts and plots for data insights
- ✅ **Word Cloud Generation**: Visual representation of common words
- ✅ **Export Reports**: JSON reports for further analysis

## Project Structure

```
├── reviewscrap.py          # Original scraper (legacy)
├── enhanced_scraper.py     # New enhanced scraper
├── config.py              # Configuration settings
├── utils.py               # Utility functions and classes
├── analyze_reviews.py     # Analysis and visualization tools
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── zomato.csv            # Input CSV file with restaurant URLs
└── output files:
    ├── zomato_reviews_from_urls.csv      # Main output file
    ├── zomato_reviews_from_urls_stats.json # Statistics file
    ├── zomato_scraper.log                # Log file
    └── scraping_checkpoint.json          # Progress checkpoint
```

## Installation

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your input CSV file**:
   - Name it `zomato.csv`
   - Ensure it has a column named `url` with Zomato restaurant URLs
   - Example format:
   ```csv
   url,name,location
   https://www.zomato.com/bangalore/restaurant-name,Restaurant Name,Bangalore
   ```

## Usage

### Basic Usage

1. **Run the enhanced scraper**:
   ```bash
   python enhanced_scraper.py
   ```

2. **Monitor progress**:
   - Check the console output for real-time progress
   - View detailed logs in `zomato_scraper.log`
   - Progress is automatically saved, so you can stop and resume anytime

3. **Analyze results**:
   ```bash
   python analyze_reviews.py
   ```

### Advanced Configuration

Edit `config.py` to customize scraping behavior:

```python
# Maximum pages to scrape per restaurant
MAX_PAGES = 5

# Delay between requests (min, max seconds)
DELAY_RANGE = (1, 3)

# Maximum retries for failed requests
MAX_RETRIES = 3

# Save progress every N restaurants
CHUNK_SIZE = 10
```

### Resume Interrupted Scraping

If scraping is interrupted, simply run the script again:
```bash
python enhanced_scraper.py
```

The scraper will automatically resume from where it left off using the checkpoint file.

### Clear Progress and Start Fresh

To start scraping from the beginning:
```python
from utils import CheckpointManager
checkpoint = CheckpointManager('scraping_checkpoint.json')
checkpoint.clear_checkpoint()
```

## Output Files

### Main Output (`zomato_reviews_from_urls.csv`)
Contains all scraped reviews with metadata:
- `restaurant_url`: Original restaurant URL
- `page`: Page number where review was found
- `review`: Cleaned review text
- `scraped_at`: Timestamp of when review was scraped
- `processed_at`: Timestamp of when data was processed
- `review_length`: Length of review in characters

### Statistics File (`zomato_reviews_from_urls_stats.json`)
Contains summary statistics:
- Total number of reviews and restaurants
- Average reviews per restaurant
- Review length statistics
- Restaurant with most reviews

### Log File (`zomato_scraper.log`)
Contains detailed execution logs:
- Progress updates
- Error messages
- Performance metrics
- Debugging information

## Error Handling

The scraper includes comprehensive error handling:

- **Network Errors**: Automatic retries with exponential backoff
- **Rate Limiting**: Respectful delays and 429 error handling
- **Invalid URLs**: Graceful handling of malformed URLs
- **Missing Data**: Continues processing if some reviews are missing
- **Server Errors**: Automatic retry for temporary server issues

## Best Practices

1. **Be Respectful**: The scraper includes delays to avoid overwhelming servers
2. **Monitor Logs**: Check logs regularly for any issues
3. **Backup Data**: Regularly backup your scraped data
4. **Update Selectors**: If scraping fails, CSS selectors may need updating
5. **Test Small Batches**: Test with a small CSV file first

## Troubleshooting

### Common Issues

1. **No Reviews Found**:
   - Check if Zomato has changed their HTML structure
   - Update CSS selectors in `config.py`
   - Verify URLs are correct and accessible

2. **Scraping Stops**:
   - Check network connection
   - Review error logs
   - Restart the scraper (it will resume automatically)

3. **Low Review Count**:
   - Increase `MAX_PAGES` in config
   - Check if restaurants actually have reviews
   - Verify review selectors are working

### Getting Help

1. Check the log file for detailed error messages
2. Verify your input CSV format matches requirements
3. Test with a small sample first
4. Update dependencies if needed

## Performance Tips

- **Batch Processing**: Process restaurants in batches using `CHUNK_SIZE`
- **Optimize Delays**: Adjust `DELAY_RANGE` based on your needs
- **Monitor Memory**: Large datasets may require memory optimization
- **Use Checkpoints**: Enable frequent checkpointing for long runs

## Analysis Features

The included analysis script provides:

- **Basic Statistics**: Review counts, averages, distributions
- **Top Restaurants**: Restaurants with most reviews
- **Sentiment Indicators**: Common positive/negative words
- **Visualizations**: Charts and word clouds
- **Export Reports**: JSON summaries for further analysis

## Dependencies

- `pandas`: Data manipulation and analysis
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `urllib3`: HTTP client
- `lxml`: XML and HTML parser

Optional for analysis:
- `matplotlib`: Plotting and visualization
- `seaborn`: Statistical data visualization
- `wordcloud`: Word cloud generation

## License

This project is for educational and research purposes. Please respect Zomato's terms of service and robots.txt file.

## Contributing

Feel free to submit issues and enhancement requests!

## Changelog

### v2.0 (Enhanced Version)
- Added comprehensive error handling
- Implemented checkpoint system for resume capability
- Added data validation and deduplication
- Included analysis and visualization tools
- Improved configuration management
- Enhanced logging and monitoring

### v1.0 (Original Version)
- Basic scraping functionality
- Simple CSV output
- Basic error handling
