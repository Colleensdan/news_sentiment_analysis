# main.py
import argparse
from pipeline import NewsPipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Analysis Pipeline")
    parser.add_argument("--update", action="store_true", help="Update headlines (append new data) from APIs.")
    parser.add_argument("--full-refresh", action="store_true", help="Fetch a completely new database from scratch.")
    parser.add_argument("--mode", choices=["guardian", "all"], default="guardian",
                        help="Choose scraper mode: 'guardian' (default) for Guardian-only or 'all' for all NewsAPI sources")
    args = parser.parse_args()
    
    pipeline = NewsPipeline(mode=args.mode, force_update=args.update, full_refresh=args.full_refresh)
    pipeline.run()
