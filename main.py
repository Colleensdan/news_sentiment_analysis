# main.py
import argparse
from pipeline import NewsPipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Analysis Pipeline")
    parser.add_argument("--update", action="store_true",
                        help="Force update headlines from the APIs")
    parser.add_argument("--mode", choices=["guardian", "all"], default="guardian",
                        help="Choose scraper mode: 'guardian' for Guardian-only (default) or 'all' for all NewsAPI sources")
    args = parser.parse_args()
    
    pipeline = NewsPipeline(mode=args.mode, force_update=args.update)
    pipeline.run()
