# pipeline.py

import datetime
import os
import json
import pandas as pd
from config import (
    INCLUSION_KEYWORDS, NEWSAPI_API_KEY, GUARDIAN_API_KEYS, DB_NAME,
    NEWSAPI_CONFIG, GUARDIAN_CONFIG, get_date_range
)
from database import DatabaseManager
from analysis import SentimentAnalyzer
from plotting import plot_sentiment_distribution, plot_supplementary_table
from scrapers.guardian_scraper import GuardianScraper
from scrapers.newsapi_scraper import NewsAPIScraper

# Files for tracking state
SEARCHED_KEYWORDS_FILE = "searched_keywords.txt"

def get_searched_keywords(file_path=SEARCHED_KEYWORDS_FILE):
    """
    Read the keywords that have been completely processed already from the file.
    Returns a set of keywords.
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            keywords = f.read().splitlines()
        return set(keywords)
    else:
        return set()

def update_searched_keywords(new_keywords, file_path=SEARCHED_KEYWORDS_FILE):
    """
    Update the file by adding new keywords that have been processed.
    """
    already_searched = get_searched_keywords(file_path)
    updated = already_searched.union(new_keywords)
    with open(file_path, "w") as f:
        for kw in sorted(updated):
            f.write(kw + "\n")

def update_finished_keywords():
    """
    Examine the resume state (stored in resume_state.json) and add any keyword
    that is finished (i.e. its resume page is 1) to the searched_keywords file.
    """
    # Assume resume_state functions are in resume_state.py in the project root.
    from resume_state import load_resume_state
    rs = load_resume_state()
    finished_keywords = {kw for kw, page in rs.items() if page == 1}
    update_searched_keywords(finished_keywords)

class NewsPipeline:
    """
    Orchestrates data retrieval, analysis, and plotting.
    Supports two modes:
      - "guardian" uses the official Guardian API (default).
      - "all" uses NewsAPI across all sources.
    Update strategies:
      - Incremental update (default): fetch new data from where it left off.
      - Full refresh: clear the current database, resume state, and searched keywords, then fetch all data from scratch.
    """
    def __init__(self, mode="guardian", force_update=False, full_refresh=False):
        self.mode = mode
        self.force_update = force_update
        self.full_refresh = full_refresh
        self.db = DatabaseManager(DB_NAME)
        self.db.initialize_database()
        self.start_date, self.to_date = get_date_range()

    def retrieve_data(self):
        # If full refresh is selected, clear the database and reset searched keywords.
        if self.full_refresh:
            print("Full refresh selected: clearing database and resetting resume state and searched keywords.")
            self.db.clear_headlines()
            from resume_state import save_resume_state
            save_resume_state({})  # Clear resume_state.json
            with open(SEARCHED_KEYWORDS_FILE, "w") as f:
                f.write("")  # Clear searched_keywords file
            existing_df = None
        else:
            if self.db.has_headlines():
                print("Loading headlines from database...")
                existing_df = self.db.load_headlines()
            else:
                existing_df = None

        # Determine which keywords haven't been completely processed.
        searched = get_searched_keywords()
        remaining_keywords = list(set(INCLUSION_KEYWORDS) - searched)
        if not remaining_keywords:
            print("All keywords have been processed already. No new data to fetch.")
            return self.db.load_headlines()
        print("Remaining keywords to search:", remaining_keywords)

        # Instantiate the appropriate scraper based on the mode.
        if self.mode == "guardian":
            print("Using Guardian-only scraper (API only)...")
            scraper = GuardianScraper(
                GUARDIAN_API_KEYS,  # a list of API keys from config.py
                self.start_date,
                self.to_date,
                remaining_keywords,
                page_size=NEWSAPI_CONFIG["page_size"],
                max_pages=None  # We rely on resume state for resuming.
            )
        elif self.mode == "all":
            print("Using general NewsAPI scraper (all sources) with debugging...")
            scraper = NewsAPIScraper(
                NEWSAPI_API_KEY,
                self.start_date,
                self.to_date,
                remaining_keywords,
                page_size=NEWSAPI_CONFIG["page_size"],
                max_pages=None
            )
        else:
            raise ValueError("Invalid scraper mode specified.")

        # Collect new headlines for the remaining keywords.
        new_headlines = scraper.collect_headlines()
        print(f"New headlines collected: {len(new_headlines)}")

        # After scraping, update searched keywords only for keywords that are finished.
        update_finished_keywords()

        # Merge new headlines with any existing database data.
        if existing_df is not None:
            new_df = pd.DataFrame(new_headlines)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            deduped_df = combined_df.drop_duplicates(subset=["source", "headline", "date"])
        else:
            deduped_df = pd.DataFrame(new_headlines)

        self.db.clear_headlines()
        self.db.store_headlines(deduped_df.to_dict("records"))
        return deduped_df

    def run(self):
        headlines = self.retrieve_data()
        print(f"Database now contains {len(headlines)} headlines.")

        analyzer = SentimentAnalyzer()
        headlines = analyzer.perform_sentiment_analysis(headlines)

        # ←—— INSERTED: print sentiment % breakdown
        sentiment_counts = headlines['sentiment'].value_counts(dropna=False)
        total = sentiment_counts.sum()
        print("\nSentiment percentages:")
        for sentiment, count in sentiment_counts.items():
            pct = count / total * 100
            print(f"  {sentiment.capitalize():8s}: {pct:5.2f}%")

        stats_results = analyzer.perform_statistical_tests(headlines)

        # show supplementary stats table as figure
        supp_fig = plot_supplementary_table(stats_results["supplementary_table"])
        supp_fig.show()

        # interpret chi² and Mann–Whitney
        if stats_results["chi2_p"] < 0.05:
            chi_interpretation = (
                f"the overall sentiment distribution is significantly different "
                f"(chi-square p={stats_results['chi2_p']:.4f}, Cramér's V = {stats_results['cramers_v']:.4f}),"
            )
        else:
            chi_interpretation = (
                f"there is no significant difference in the overall sentiment distribution "
                f"(chi-square p={stats_results['chi2_p']:.4f}),"
            )

        if stats_results["mannwhitney_p"] < 0.05:
            mwu_interpretation = (
                f"and there is a significant difference between positive and negative headlines "
                f"(Mann–Whitney U p={stats_results['mannwhitney_p']:.4f}, "
                f"Cliff's delta = {stats_results['cliffs_delta']:.4f})."
            )
        else:
            mwu_interpretation = (
                f"and there is no significant difference between positive and negative headlines "
                f"(Mann–Whitney U p={stats_results['mannwhitney_p']:.4f})."
            )

        print("\nStatistical Analysis Summary:")
        print(f"Based on our tests, {chi_interpretation} {mwu_interpretation}")

        plot_sentiment_distribution(headlines, stats_results)
        self.db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="News Analysis Pipeline")
    parser.add_argument("--update", action="store_true",
                        help="Update headlines (append new data) from APIs.")
    parser.add_argument("--full-refresh", action="store_true",
                        help="Fetch a completely new database from scratch.")
    parser.add_argument("--mode", choices=["guardian", "all"], default="guardian",
                        help="Choose scraper mode: 'guardian' (default) for Guardian-only or 'all' for all NewsAPI sources")
    args = parser.parse_args()

    pipeline = NewsPipeline(mode=args.mode, force_update=args.update, full_refresh=args.full_refresh)
    pipeline.run()
