#!/usr/bin/env python3
"""
Data visualization script for Moltbook stats.
Generates charts from the collected CSV data.
"""

import os
import sys


def load_data(csv_file="data/moltbook_stats.csv"):
    """Load the collected data from CSV file."""
    try:
        import pandas as pd
    except ImportError:
        print("pandas is required but not installed. Install with: pip install pandas matplotlib")
        return None
        
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return None
    
    df = pd.read_csv(csv_file)
    
    # Handle potential datetime parsing issues - fix malformed datetime strings
    def safe_parse_datetime(dt_str):
        try:
            # Handle the specific error case: "second must be in 0..59: 2026-02-01T23:20:47854"
            # This appears to be a malformed timestamp with milliseconds in wrong position
            if isinstance(dt_str, str) and 'T' in dt_str:
                # Check if the format looks like "2026-02-01T23:20:47854" (wrong millisecond placement)
                parts = dt_str.split('T')
                if len(parts) == 2:
                    date_part = parts[0]
                    time_part = parts[1]
                    # If time part has more than expected digits after colon, it's malformed
                    if '.' not in time_part and ':' in time_part:
                        # Try to fix formats like "23:20:47854" by assuming the last 3 digits are millis
                        time_components = time_part.split(':')
                        if len(time_components) == 3 and len(time_components[2]) > 2:
                            # This is likely the problematic format - last 3 digits are milliseconds
                            sec_milli = time_components[2]
                            seconds = sec_milli[:2]
                            milliseconds = sec_milli[2:]
                            if milliseconds.isdigit() and len(milliseconds) <= 6:  # Up to microsecond precision
                                corrected_time = f"{time_components[0]}:{time_components[1]}:{seconds}.{milliseconds}"
                                dt_str = f"{date_part}T{corrected_time}"
            return pd.to_datetime(dt_str, format='ISO8601', errors='coerce')
        except:
            return pd.NaT
    
    # Apply the safe parser to the datetime column
    df['datetime'] = df['datetime'].apply(safe_parse_datetime)
    
    # Drop rows with NaT (Not a Time) values
    df = df.dropna(subset=['datetime'])
    
    df = df.sort_values('datetime')
    return df


def plot_stats(df):
    """Create plots of the collected stats."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("matplotlib is required but not installed. Install with: pip install pandas matplotlib")
        return
    
    if df is None or df.empty:
        print("No data to plot")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Moltbook Statistics Over Time', fontsize=16)
    
    # AI Agents
    axes[0, 0].plot(df['datetime'], df['ai_agents'], marker='o', linestyle='-', color='blue')
    axes[0, 0].set_title('AI Agents')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].grid(True, alpha=0.3)
    # Format y-axis for large numbers (K for thousands, M for millions)
    axes[0, 0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else f'{int(x)}'))
    
    # Submolts
    axes[0, 1].plot(df['datetime'], df['submolts'], marker='o', linestyle='-', color='green')
    axes[0, 1].set_title('Submolts')
    axes[0, 1].set_xlabel('Date')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].grid(True, alpha=0.3)
    # Format y-axis for large numbers
    axes[0, 1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else f'{int(x)}'))
    
    # Posts
    axes[1, 0].plot(df['datetime'], df['posts'], marker='o', linestyle='-', color='red')
    axes[1, 0].set_title('Posts')
    axes[1, 0].set_xlabel('Date')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].grid(True, alpha=0.3)
    # Format y-axis for large numbers
    axes[1, 0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else f'{int(x)}'))
    
    # Comments
    axes[1, 1].plot(df['datetime'], df['comments'], marker='o', linestyle='-', color='orange')
    axes[1, 1].set_title('Comments')
    axes[1, 1].set_xlabel('Date')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].grid(True, alpha=0.3)
    # Format y-axis for large numbers
    axes[1, 1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else f'{int(x)}'))
    
    plt.tight_layout()
    # Also save as PNG in addition to SVG
    plt.savefig('moltbook_stats.svg', dpi=300, bbox_inches='tight')
    plt.savefig('moltbook_stats.png', dpi=300, bbox_inches='tight')
    print("Charts saved as moltbook_stats.png and moltbook_stats.svg")


def print_summary(df):
    """Print a summary of the collected data."""
    if df is None or df.empty:
        print("No data available")
        return
    
    print("\n--- Data Summary ---")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    
    if len(df) > 1:
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        print(f"\nLatest stats ({latest['datetime']}):")
        print(f"  AI Agents: {latest['ai_agents']:,}")
        print(f"  Submolts: {latest['submolts']:,}")
        print(f"  Posts: {latest['posts']:,}")
        print(f"  Comments: {latest['comments']:,}")
        
        print(f"\nChanges since previous:")
        print(f"  AI Agents: {latest['ai_agents'] - previous['ai_agents']:+,}")
        print(f"  Submolts: {latest['submolts'] - previous['submolts']:+,}")
        print(f"  Posts: {latest['posts'] - previous['posts']:+,}")
        print(f"  Comments: {latest['comments'] - previous['comments']:+,}")


def main():
    """Main function to run the visualization."""
    df = load_data()
    
    if df is not None:
        print_summary(df)
        plot_stats(df)
    else:
        print("Failed to load data, exiting.")


if __name__ == "__main__":
    main()
