# News Analysis Project

## Overview

The **News Analysis Project** is a modular, object-oriented Python application designed to collect, analyze, and visualize newspaper headlines over the last 5 years. The project supports two distinct data collection methods:

1. **Guardian-only Mode (Default):**  
   Uses the official Guardian API (with the key `e1fb2aa1-9bd9-4040-87c2-adca1ec50d90`) to collect headlines exclusively from The Guardian. No web scraping is involved.

2. **All-Sources Mode:**  
   Uses NewsAPI to collect headlines across all available sources, with additional debugging output to help diagnose issues.

Collected headlines are stored in a local SQLite database to conserve API calls. After data collection, the application performs sentiment analysis using NLTK’s VADER sentiment analyzer, conducts statistical tests (including chi-square, ANOVA, and Mann–Whitney U tests) with significance assessments and effect size calculations, and produces a polished bar chart with error bars and significance annotations.

## Why This Project?

- **Data Collection Efficiency:**  
  Uses a database to store results, conserving limited API calls (e.g., 100 requests per day).

- **Robust Sentiment Analysis:**  
  Leverages VADER sentiment analysis and integrated statistical tests to yield insights into the sentiment distribution of headlines.

- **Modular Design:**  
  Code is organized into multiple modules (configuration, database, analysis, plotting, scrapers, and pipeline) to improve maintainability and testability.

- **Flexible Data Retrieval:**  
  Operates in two modes: Guardian-only or all-sources, depending on your requirements.

## Project Structure

```plaintext
news_analysis_project/
│
├── config.py                # Configuration settings and helper functions.
├── database.py              # DatabaseManager class (SQLite interactions).
├── analysis.py              # SentimentAnalyzer (sentiment analysis and statistical tests).
├── plotting.py              # Plotting routines for polished visualizations.
├── pipeline.py              # NewsPipeline class orchestrates data retrieval, analysis, and plotting.
├── main.py                  # Entry point; handles command-line arguments and starts the pipeline.
└── scrapers/
    ├── __init__.py          # Empty file to mark scrapers as a package.
    ├── base_scraper.py      # Abstract base class for scraper implementations.
    ├── guardian_scraper.py  # GuardianScraper using the official Guardian API.
    └── newsapi_scraper.py   # NewsAPIScraper for collecting headlines from all sources.
```

## Requirements and Dependencies

- **Python 3.7+**
- **SQLite3** (comes standard with Python)
- **Requests**
- **Pandas**
- **Matplotlib**
- **NLTK** (VADER lexicon is downloaded automatically)
- **SciPy**

Install dependencies via pip:

```bash
pip install requests pandas matplotlib nltk scipy

## How to Use

1. **Clone or Download the Project**  
   Open the project root folder (the one containing `main.py`) in your development environment (e.g., VS Code).

2. **Configuration**

   - **API Keys:**  
     The project uses the Guardian API key `e1fb2aa1-9bd9-4040-87c2-adca1ec50d90` for Guardian-only mode and the same key for NewsAPI mode. Update `config.py` if needed.

   - **Date Range:**  
     By default, the project collects headlines from the last 5 years. The current date is set to a fixed value (14 April 2025) for reproducibility (defined in `config.py`).

   - **Inclusion Keywords:**  
     Adjust the list in `config.py` to change the search terms.

3. **Running the Project**  
   In a terminal at the project root, run:

   - **Default Mode (Guardian-only):**
     ```bash
     python main.py
     ```
     This uses the Guardian API exclusively.

   - **Force Data Refresh:**  
     To re-query the APIs instead of loading headlines from the local database, run:
     ```bash
     python main.py --update
     ```

   - **All-Sources Mode:**  
     To use the NewsAPI scraper (all sources), run:
     ```bash
     python main.py --mode all
     ```
     You can combine options:
     ```bash
     python main.py --mode all --update
     ```

4. **Output**  
   The application will:
   - Retrieve and deduplicate headlines (subject to API quotas and availability).
   - Store headlines in a SQLite database (`headlines.db`).
   - Perform sentiment analysis and statistical tests, printing a supplementary table with significance markers and effect sizes.
   - Generate a polished bar chart with error bars and significance annotations. The x-axis is labelled **"Sentiment"** and the bars are labelled **"Positive"**, **"Neutral"**, and **"Negative"**.

## How It Works

1. **Data Retrieval:**  
   The `NewsPipeline` class (in `pipeline.py`) checks if headlines are already stored in the database and loads them unless a forced update is specified. Depending on the selected mode, it instantiates either:
   - **GuardianScraper** (in `scrapers/guardian_scraper.py`): Uses the official Guardian API.
   - **NewsAPIScraper** (in `scrapers/newsapi_scraper.py`): Uses NewsAPI across all sources with added debugging.

2. **Data Storage:**  
   The `DatabaseManager` (in `database.py`) stores headlines in a SQLite database and deduplicates them.

3. **Analysis:**  
   The `SentimentAnalyzer` (in `analysis.py`) computes sentiment scores for each headline using NLTK’s VADER, classifies them as positive, negative, or neutral, and performs statistical tests (chi-square, ANOVA, Mann–Whitney U) with effect size calculations.

4. **Plotting:**  
   The `plot_sentiment_distribution` function (in `plotting.py`) produces a bar chart with error bars. The x-axis is labelled **"Sentiment"**, and the bars are displayed as **"Positive"**, **"Neutral"**, and **"Negative"**. Significance annotations (asterisks) are displayed between the Positive and Negative bars.

## Conclusion

This project demonstrates a complete, modular pipeline for collecting, processing, and analyzing newspaper headlines using API-based retrieval methods. Its design emphasizes efficiency (through data caching), robust analysis (via sentiment and statistical testing), and polished visual output, providing a solid foundation for further exploration or extensions in news analytics.

Happy coding!
