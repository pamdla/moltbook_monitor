#!/usr/bin/env python3
"""
Simple test script to verify the scraper functionality
"""

import asyncio
import os
import csv
from datetime import datetime
from scraper import MoltbookStatsScraper


async def test_scraper():
    """Test the scraper functionality."""
    print("Testing Moltbook Stats Scraper...")
    
    # Create scraper instance
    scraper = MoltbookStatsScraper()
    
    # Test scraping
    print("Running scrape...")
    stats = await scraper.scrape()
    
    print(f"Scraped stats: {stats}")
    
    # Verify data was saved
    csv_file = scraper.OUTPUT_FILE
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                latest_row = rows[-1]
                print(f"Latest saved data: {latest_row}")
            else:
                print("CSV file exists but is empty")
    else:
        print(f"CSV file does not exist: {csv_file}")
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_scraper())