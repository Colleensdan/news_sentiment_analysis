# pipeline.py
import datetime
from config import INCLUSION_KEYWORDS, NEWSAPI_API_KEY, GUARDIAN_API_KEY, DB_NAME, NEWSAPI_CONFIG, GUARDIAN_CONFIG, get_date_range
from database import DatabaseManager
from analysis import SentimentAnalyzer
from plotting import plot_sentiment_distribution
from scrapers.guardian_scraper import GuardianScraper
from scrapers.newsapi_scraper import NewsAPIScraper
from plotting import plot_supplementary_table
import os
from config import INCLUSION_KEYWORDS  # Full list of inclusion keywords

def retrieve_data(self):
    # Load headlines from DB if available and not forcing an update:
    if not self.force_update and self.db.has_headlines():
        print("Loading headlines from database...")
        return self.db.load_headlines()
    else:
        # Determine which keywords haven't been processed yet.
        searched = get_searched_keywords()
        remaining_keywords = list(set(INCLUSION_KEYWORDS) - searched)
        
        if not remaining_keywords:
            print("All keywords have been processed already. No new data to fetch.")
            # Optionally, just return what's in the DB.
            return self.db.load_headlines()
        
        print("Remaining keywords to search:", remaining_keywords)
        
        # Choose the appropriate scraper based on the mode.
        if self.mode == "guardian":
            print("Using Guardian-only scraper (API only)...")
            scraper = GuardianScraper(
                GUARDIAN_API_KEY,
                self.start_date,
                self.to_date,
                remaining_keywords,
                page_size=NEWSAPI_CONFIG["page_size"],
                max_pages=None  # No fixed limit
            )
        elif self.mode == "all":
            print("Using general NewsAPI scraper (all sources) with debugging...")
            scraper = NewsAPIScraper(
                NEWSAPI_API_KEY,
                self.start_date,
                self.to_date,
                remaining_keywords,
                page_size=NEWSAPI_CONFIG["page_size"],
                max_pages=None  # No fixed limit
            )
        else:
            raise ValueError("Invalid scraper mode specified.")
        
        # Collect headlines for the remaining keywords.
        headlines = scraper.collect_headlines()
        
        # Update the file with the keywords that were processed (the remaining keywords).
        update_searched_keywords(remaining_keywords)
        
        # Clear any existing headlines and store the new ones.
        self.db.clear_headlines()
        self.db.store_headlines(headlines)
        return self.db.load_headlines()

def get_searched_keywords(file_path="searched_keywords.txt"):
    """
    Read the keywords that have been processed already from the file.
    Returns a set of keywords.
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            keywords = f.read().splitlines()
        return set(keywords)
    else:
        return set()

def update_searched_keywords(new_keywords, file_path="searched_keywords.txt"):
    """
    Update the file with new keywords that have been processed.
    """
    already_searched = get_searched_keywords(file_path)
    updated = already_searched.union(new_keywords)
    with open(file_path, "w") as f:
        for kw in sorted(updated):
            f.write(kw + "\n")


class NewsPipeline:
    """
    Orchestrates data retrieval, analysis, and plotting.
    Mode "guardian" uses the official Guardian API; mode "all" uses NewsAPI across all sources.
    """
    def __init__(self, mode="guardian", force_update=False):
        self.mode = mode
        self.force_update = force_update
        self.db = DatabaseManager(DB_NAME)
        self.db.initialize_database()
        self.start_date, self.to_date = get_date_range()
    
    def retrieve_data(self):
        if not self.force_update and self.db.has_headlines():
            print("Loading headlines from database...")
            return self.db.load_headlines()
        else:
            if self.mode == "guardian":
                print("Using Guardian-only scraper (API only)...")
                scraper = GuardianScraper(
                    GUARDIAN_API_KEY,
                    self.start_date,
                    self.to_date,
                    INCLUSION_KEYWORDS,
                    page_size=NEWSAPI_CONFIG["page_size"],
                    max_pages=None  # No fixed page limit.
                )
            elif self.mode == "all":
                print("Using general NewsAPI scraper (all sources) with debugging...")
                scraper = NewsAPIScraper(
                    NEWSAPI_API_KEY,
                    self.start_date,
                    self.to_date,
                    INCLUSION_KEYWORDS,
                    page_size=NEWSAPI_CONFIG["page_size"],
                    max_pages=None  # No fixed page limit.
                )
            else:
                raise ValueError("Invalid scraper mode specified.")
            
            headlines = scraper.collect_headlines()
            self.db.clear_headlines()
            self.db.store_headlines(headlines)
            return self.db.load_headlines()
    
    def run(self):
        headlines = self.retrieve_data()
        print(f"Database now contains {len(headlines)} headlines.")
        analyzer = SentimentAnalyzer()
        headlines = analyzer.perform_sentiment_analysis(headlines)
        stats_results = analyzer.perform_statistical_tests(headlines)
        
        from plotting import plot_supplementary_table

        # Generate and display the stats table as a figure.
        supp_fig = plot_supplementary_table(stats_results["supplementary_table"])
        supp_fig.show()  # Alternatively, use plt.show() if needed.


        if stats_results["chi2_p"] < 0.05:
            chi_interpretation = (f"the overall sentiment distribution is significantly different (chi-square p={stats_results['chi2_p']:.4f}, "
                                  f"Cramér's V = {stats_results['cramers_v']:.3f}),")
        else:
            chi_interpretation = (f"there is no significant difference in the overall sentiment distribution (chi-square p={stats_results['chi2_p']:.4f}),")
        
        if stats_results["mannwhitney_p"] < 0.05:
            mwu_interpretation = (f"and there is a significant difference between positive and negative headlines "
                                  f"(Mann–Whitney U p={stats_results['mannwhitney_p']:.4f}, Cliff's delta = {stats_results['cliffs_delta']:.3f}).")
        else:
            mwu_interpretation = (f"and there is no significant difference between positive and negative headlines "
                                  f"(Mann–Whitney U p={stats_results['mannwhitney_p']:.4f}).")
        
        print("\nStatistical Analysis Summary:")
        print(f"Based on our tests, {chi_interpretation} {mwu_interpretation}")
        
        plot_sentiment_distribution(headlines, stats_results)
        self.db.close()
