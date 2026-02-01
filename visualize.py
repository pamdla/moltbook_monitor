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
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    return df


def plot_stats(df):
    """Create plots of the collected stats."""
    try:
        import matplotlib.pyplot as plt
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
    
    # Submolts
    axes[0, 1].plot(df['datetime'], df['submolts'], marker='o', linestyle='-', color='green')
    axes[0, 1].set_title('Submolts')
    axes[0, 1].set_xlabel('Date')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Posts
    axes[1, 0].plot(df['datetime'], df['posts'], marker='o', linestyle='-', color='red')
    axes[1, 0].set_title('Posts')
    axes[1, 0].set_xlabel('Date')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Comments
    axes[1, 1].plot(df['datetime'], df['comments'], marker='o', linestyle='-', color='orange')
    axes[1, 1].set_title('Comments')
    axes[1, 1].set_xlabel('Date')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('moltbook_stats.png', dpi=300, bbox_inches='tight')
    print("Chart saved as moltbook_stats.png")


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