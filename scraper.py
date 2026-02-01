import asyncio
import csv
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import async_playwright
import re


class MoltbookStatsScraper:
    BASE_URL = "https://www.moltbook.com"
    OUTPUT_DIR = "data"
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "moltbook_stats.csv")
    HEADLESS = True
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    def __init__(self):
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.OUTPUT_FILE):
            with open(self.OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=["timestamp", "datetime", "ai_agents", "submolts", "posts", "comments"]
                )
                writer.writeheader()

    async def scrape(self) -> Optional[Dict[str, int]]:
        """
        Scrape statistics from Moltbook with retry mechanism and multiple selector strategies
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                async with async_playwright() as p:
                    # Try different browser channels for robustness
                    browser = None
                    for channel in ["chrome", "msedge"]:
                        try:
                            browser = await p.chromium.launch(
                                headless=self.HEADLESS,
                                channel=channel
                            )
                            break
                        except Exception:
                            continue
                    
                    if not browser:
                        # Fallback to default chromium
                        browser = await p.chromium.launch(headless=self.HEADLESS)
                    
                    page = await browser.new_page()
                    
                    # Set extra HTTP headers to appear more like a real browser
                    await page.set_extra_http_headers({
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    
                    # Navigate to the page with a more realistic timeout
                    await page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                    
                    # Wait for network idle to ensure content loads
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    
                    # Additional wait for dynamic content
                    await page.wait_for_timeout(15000)
                    
                    # Extract stats with multiple fallback selectors
                    stats = await self._extract_stats(page)
                    
                    await browser.close()
                    
                    if stats and len(stats) >= 4:
                        self.logger.info(f"Successfully scraped stats: {stats}")
                        return stats
                    else:
                        self.logger.warning(f"Attempt {attempt + 1}: Could not extract all stats. Got: {stats}")
                        
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(f"All {max_retries} attempts failed. Returning empty stats.")
                    return {"ai_agents": 0, "submolts": 0, "posts": 0, "comments": 0}
                
                # Wait before retry with exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        return {"ai_agents": 0, "submolts": 0, "posts": 0, "comments": 0}

    async def _extract_stats(self, page) -> Dict[str, int]:
        """
        Extract stats using multiple selector strategies with fallbacks
        """
        stats = {}
        
        # Wait a bit more for dynamic content to load
        await page.wait_for_timeout(6000)
        
        # Strategy 1: Primary selectors for stat elements
        primary_selectors = [
            "div.gap-6 div > div.text-2xl",
            "div.stat-card div.text-2xl",
            "div.stats-container div.text-2xl",
            "#stats-section div.text-2xl",
            ".stats-grid .stat-value",
            ".dashboard-stats .count",
            "div.gap-6 span",
            "div.gap-6 strong",
            ".stat-item .value",
            "[data-stat-value]",
            ".MuiBox-root div:textMatches('\\d+')"
        ]
        
        for selector in primary_selectors:
            try:
                # Wait a bit for elements to appear
                try:
                    await page.wait_for_selector(selector, timeout=15000)
                except:
                    continue  # Skip if selector doesn't appear
                
                stat_elements = await page.query_selector_all(selector)
                if len(stat_elements) >= 4:
                    values = []
                    for element in stat_elements:
                        text = await element.inner_text()
                        # Clean and extract numeric values
                        cleaned_text = re.sub(r'[^\d,]', '', text.strip())
                        # Handle commas in numbers (e.g., 1,234)
                        cleaned_text = cleaned_text.replace(',', '')
                        if cleaned_text.isdigit():
                            values.append(int(cleaned_text))
                    
                    if len(values) >= 4:
                        stats = {
                            "ai_agents": values[0] if len(values) > 0 else 0,
                            "submolts": values[1] if len(values) > 1 else 0,
                            "posts": values[2] if len(values) > 2 else 0,
                            "comments": values[3] if len(values) > 3 else 0
                        }
                        return stats
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {str(e)}")
                continue  # Try next selector
        
        # Strategy 2: Alternative approach - look for font-bold classes or similar
        alt_selectors = [
            "div.font-bold",
            ".count",
            ".number",
            "span.font-bold",
            ".stats-number",
            ".MuiTypography-body1",
            ".text-3xl",
            ".text-2xl"
        ]
        
        for selector in alt_selectors:
            try:
                # Wait a bit for elements to appear
                try:
                    await page.wait_for_selector(selector, timeout=15000)
                except:
                    continue  # Skip if selector doesn't appear
                
                elements = await page.query_selector_all(selector)
                extracted_numbers = []
                
                for element in elements:
                    text = await element.inner_text()
                    # Extract digits from the text (handle commas in numbers)
                    numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+', text.replace(' ', ''))
                    for num_str in numbers:
                        # Remove commas and convert to integer
                        clean_num = num_str.replace(',', '').replace('.', '')
                        if clean_num.isdigit():
                            extracted_numbers.append(int(clean_num))
                
                # Take the first 4 significant numbers we find
                if len(extracted_numbers) >= 4:
                    stats = {
                        "ai_agents": extracted_numbers[0],
                        "submolts": extracted_numbers[1], 
                        "posts": extracted_numbers[2],
                        "comments": extracted_numbers[3]
                    }
                    return stats
            except Exception as e:
                self.logger.debug(f"Alt selector {selector} failed: {str(e)}")
                continue  # Try next selector
        
        # Strategy 3: Look for specific textual patterns
        try:
            page_content = await page.content()
            
            # Look for common patterns in web pages for stats
            patterns = [
                r'"ai_agents_count":\s*(\d+)',
                r'"submolts_count":\s*(\d+)',
                r'"posts_count":\s*(\d+)',
                r'"comments_count":\s*(\d+)',
                r'ai_agents["\']?\s*[:=]\s*["\']?(\d+)',
                r'submolts["\']?\s*[:=]\s*["\']?(\d+)',
                r'posts["\']?\s*[:=]\s*["\']?(\d+)',
                r'comments["\']?\s*[:=]\s*["\']?(\d+)',
                r'>\s*(\d+)\s*<[^>]*>AI Agents?',
                r'>\s*(\d+)\s*<[^>]*>Submolts?',
                r'>\s*(\d+)\s*<[^>]*>Posts?',
                r'>\s*(\d+)\s*<[^>]*>Comments?',
                r'(\d+)\D*s*(?:ai\s*agents?)',
                r'(\d+)\D*s*(?:submolts?)',
                r'(\d+)\D*s*(?:posts?)',
                r'(\d+)\D*s*(?:comments?)',
            ]
            
            found_numbers = []
            for pattern in patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    if match.isdigit():
                        found_numbers.append(int(match))
            
            # Look for simple digit groups on the page as well
            all_digits = re.findall(r'"(\d{3,})"|>(\d{3,})<', page_content)
            for match_group in all_digits:
                for num_str in match_group:
                    if num_str.isdigit():
                        found_numbers.append(int(num_str))
            
            # Filter for reasonable stat values (not too small, not too big)
            filtered_numbers = [num for num in found_numbers if 0 <= num < 1000000]
            
            if len(filtered_numbers) >= 4:
                stats = {
                    "ai_agents": filtered_numbers[0] if len(filtered_numbers) > 0 else 0,
                    "submolts": filtered_numbers[1] if len(filtered_numbers) > 1 else 0,
                    "posts": filtered_numbers[2] if len(filtered_numbers) > 2 else 0,
                    "comments": filtered_numbers[3] if len(filtered_numbers) > 3 else 0
                }
                return stats
        except Exception as e:
            self.logger.debug(f"Text pattern extraction failed: {str(e)}")
            pass
        
        return stats

    def save(self, stats: Dict[str, int]):
        now = datetime.now()
        row = {
            "timestamp": int(now.timestamp()),
            "datetime": now.isoformat(),
            "ai_agents": int(stats.get("ai_agents", 0)),
            "submolts": int(stats.get("submolts", 0)),
            "posts": int(stats.get("posts", 0)),
            "comments": int(stats.get("comments", 0))
        }
        
        # Check if file exists and has header; if not, write header first
        file_exists = os.path.isfile(self.OUTPUT_FILE)
        write_header = not file_exists or os.path.getsize(self.OUTPUT_FILE) == 0
        
        with open(self.OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=["timestamp", "datetime", "ai_agents", "submolts", "posts", "comments"]
            )
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        
        # Log what was actually saved
        self.logger.info(f"Saved to CSV: {row}")

    async def run(self):
        stats = await self.scrape()
        if stats is not None:
            self.save(stats)
            print(f"{datetime.now().isoformat()} | {json.dumps(stats)}")
            
            # Log successful completion
            self.logger.info(f"Stats saved: {stats}")
        else:
            # Handle case where scrape returns None
            default_stats = {"ai_agents": 0, "submolts": 0, "posts": 0, "comments": 0}
            self.save(default_stats)
            print(f"{datetime.now().isoformat()} | Error occurred, saved default stats: {json.dumps(default_stats)}")
            self.logger.error("Scrape returned None, saving default values")


if __name__ == "__main__":
    scraper = MoltbookStatsScraper()
    asyncio.run(scraper.run())
