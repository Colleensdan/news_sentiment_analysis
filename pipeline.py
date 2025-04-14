# pipeline.py
import datetime
from config import INCLUSION_KEYWORDS, NEWSAPI_API_KEY, GUARDIAN_API_KEY, DB_NAME, NEWSAPI_CONFIG, GUARDIAN_CONFIG, get_date_range
from database import DatabaseManager
from analysis import SentimentAnalyzer
from plotting import plot_sentiment_distribution
from scrapers.guardian_scraper import GuardianScraper
from scrapers.newsapi_scraper import NewsAPIScraper

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
        
        print("\nSupplementary Statistical Table:")
        print(stats_results["supplementary_table"].to_string(index=False))
        
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
