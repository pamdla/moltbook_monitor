# Moltbook Stats Scraper

A Python web scraper that collects statistics from Moltbook.com and saves them to a CSV file for analysis.

## Features

- Scrapes AI agents, submolts, posts, and comments counts from Moltbook
- Saves data to CSV with timestamps
- Robust error handling and retries with multiple fallback selectors
- Runs continuously with monitoring
- Data visualization capabilities
- Scheduled execution via cron
- Comprehensive logging and error reporting

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browsers (required for web scraping):
   ```bash
   playwright install chromium
   # Or for better compatibility:
   playwright install-deps
   playwright install chrome
   ```

## Usage

### Single Run
```bash
python scraper.py
```

### Continuous Monitoring
```bash
python monitor.py --interval 30  # Run every 30 minutes
```

### Visualize Data
```bash
python visualize.py
```

## Scripts

- `scraper.py`: Main scraper class with robust error handling, retry mechanisms, and multiple selector strategies
- `monitor.py`: Continuous monitoring script that runs the scraper on a schedule with graceful shutdown handling
- `visualize.py`: Generates charts and prints summaries from collected data
- `test_scraper.py`: Simple test to verify scraper functionality
- `simple_test.py`: Connectivity test script

## Configuration

The scraper has the following configurable options:
- `HEADLESS`: Set to False to run browser visibly (default: True)
- `BASE_URL`: The target URL (default: "https://www.moltbook.com")
- Interval in `monitor.py`: Time between scrapes in minutes (default: 60)

## Data Collection

The scraper collects the following statistics:
- AI Agents: Number of AI agents
- Submolts: Number of submolts  
- Posts: Number of posts
- Comments: Number of comments
- Timestamp: Unix timestamp
- Datetime: ISO formatted datetime

All data is saved to `data/moltbook_stats.csv`.

## Cron Job Setup

Add the following to your crontab (`crontab -e`) to run the scraper hourly:

```
0 * * * * cd /path/to/project && source venv/bin/activate && python3 scraper.py >> cron.log 2>&1
```

## Troubleshooting

- If you get "Executable doesn't exist" errors, run: `playwright install chromium`
- The scraper includes multiple fallback selectors to handle website changes
- Check `monitor.log` for detailed logging when running the monitoring script
- Large websites may require longer timeouts - adjust accordingly in the code