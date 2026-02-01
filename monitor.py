#!/usr/bin/env python3
"""
Continuous monitoring script for Moltbook stats scraper.
Runs the scraper periodically and logs results.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from scraper import MoltbookStatsScraper


class MoltbookMonitor:
    def __init__(self, interval_minutes=5):
        self.interval = interval_minutes * 60  # Convert to seconds
        self.running = True
        self.scraper = MoltbookStatsScraper()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def run_single_scrape(self):
        """Run a single scrape operation with error handling."""
        try:
            await self.scraper.run()
        except Exception as e:
            self.logger.error(f"Error during scrape: {str(e)}")
            # Save a default entry to maintain data continuity
            default_stats = {"ai_agents": 0, "submolts": 0, "posts": 0, "comments": 0}
            self.scraper.save(default_stats)
            self.logger.info(f"Saved default stats due to error: {datetime.now().isoformat()}")

    async def start_monitoring(self):
        """Start the continuous monitoring loop."""
        self.logger.info(f"Starting Moltbook stats monitoring (interval: {self.interval}s)")
        
        while self.running:
            start_time = datetime.now()
            self.logger.info(f"Starting scrape at {start_time.isoformat()}")
            
            await self.run_single_scrape()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.logger.info(f"Scrape completed in {duration:.2f}s")
            
            # Wait for the specified interval, checking for shutdown signal
            sleep_interval = max(1, self.interval - duration)  # Don't sleep negative time
            
            for _ in range(int(sleep_interval)):
                if not self.running:
                    break
                await asyncio.sleep(1)
        
        self.logger.info("Monitoring stopped")


async def main():
    """Main function to run the monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Moltbook Stats Monitor')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Interval between scrapes in minutes (default: 60)')
    
    args = parser.parse_args()
    
    monitor = MoltbookMonitor(interval_minutes=args.interval)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down monitor...")


if __name__ == "__main__":
    asyncio.run(main())
