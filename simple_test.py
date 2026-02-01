#!/usr/bin/env python3
"""
Simple connectivity test
"""

import asyncio
from playwright.async_api import async_playwright
import re


async def simple_connectivity_test():
    """Test if we can connect to moltbook.com"""
    print("Testing connection to moltbook.com...")
    
    async with async_playwright() as p:
        # Launch browser with minimal options
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Go to the site with a shorter timeout
            await page.goto("https://www.moltbook.com", timeout=20000)
            print("Connected to moltbook.com successfully!")
            
            # Get page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Get page content
            content = await page.content()
            print(f"Page content length: {len(content)} characters")
            
            # Look for numbers in the content
            numbers = re.findall(r'[\d,]+', content)
            print(f"Some numbers found in page: {numbers[:10]}")  # Show first 10 numbers
            
        except Exception as e:
            print(f"Error connecting to moltbook.com: {str(e)}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(simple_connectivity_test())