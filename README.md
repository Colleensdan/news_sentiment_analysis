# News Analysis Project

## Overview

The **News Analysis Project** is a modular, object-oriented Python application designed to collect, analyze, and visualize newspaper headlines over the last 5 years. The project supports two distinct data collection methods:

1. **Guardian-only Mode (Default):**  
   Uses the official Guardian API to collect headlines exclusively from The Guardian. No web scraping is involved.

2. **All-Sources Mode:**  
   Uses NewsAPI to collect headlines across all available sources, with additional debugging output to help diagnose issues.

Collected headlines are stored in a local SQLite database to conserve API calls. After data collection, the application performs sentiment analysis using NLTK’s VADER sentiment analyzer, conducts statistical tests (including chi-square, ANOVA, and Mann–Whitney U tests) with effect size calculations, and produces a polished bar chart with error bars and significance annotations.

## Why This Project?

- **Data Collection Efficiency:**  
  Uses a database to store results, conserving limited API calls (e.g., 500 requests per day).

- **Robust Sentiment Analysis:**  
  Leverages VADER sentiment analysis and integrated statistical tests to yield insights into the sentiment distribution of headlines.

- **Modular Design:**  
  Code is organized into multiple modules (configuration, database, analysis, plotting, scrapers, and pipeline) for easier maintenance and testing.

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
├── resume_state.py          # Helper functions for loading/saving resume state to resume_state.json.
├── resume_state.json        # Initialized as an empty JSON object (e.g., "{}")
├── README.txt               # This file.
├── .gitignore               # Git ignore rules (e.g., to ignore api_keys.txt, resume_state.json, etc.).
└── scrapers/
    ├── __init__.py          # Marks scrapers as a package.
    ├── base_scraper.py      # Abstract base class for scraper implementations.
    ├── guardian_scraper.py  # GuardianScraper using the official Guardian API with resume state and key rotation.
    └── newsapi_scraper.py   # NewsAPIScraper for collecting headlines from all sources with debugging.

```
## Requirements and Installation

- **Python 3.7+**
- **SQLite3** (included with Python)
- **Dependencies:** Requests, Pandas, Matplotlib, NLTK, SciPy  
  Install using pip:

  ```bash
  pip install requests pandas matplotlib nltk scipy
 
 - **NLTK Data:** The VADER lexicon downloads automatically when you run the code.

 ## How to Use

1. **Clone or Download the Project**  
   Open the project root folder (the one containing `main.py`) in your development environment (e.g., VS Code).

2. **Configuration**

   - **API Keys:**  
     Update `config.py` with your API keys:
     - `GUARDIAN_API_KEYS`: A list of Guardian API keys (e.g., `["e1fb2aa1-9bd9-4040-87c2-adca1ec50d90", "..."]`).
     - `NEWSAPI_API_KEY` for NewsAPI mode.

   - **Date Range:**  
     By default, the project collects headlines from the last 5 years. The current date is set to a fixed value (14 April 2025) for reproducibility.

   - **Inclusion Keywords:**  
     Edit the list in `config.py` to change the search terms.

3. **Running the Project**  
   In a terminal at the project root, run:

   - **Default Mode (Guardian-only, incremental update):**
     ```bash
     python main.py
     ```
     This uses the Guardian API exclusively.

   - **Force Data Refresh (Incremental Update):**
     ```bash
     python main.py --update
     ```
     This will fetch new data from where it left off.

   - **All-Sources Mode (NewsAPI):**
     ```bash
     python main.py --mode all
     ```
     You can combine options:
     ```bash
     python main.py --mode all --update
     ```

   - **Full Refresh (Clear Database and Resume State):**
     ```bash
     python main.py --full-refresh
     ```

4. **Output**  
   The application will:
   - Retrieve and deduplicate headlines (subject to API quotas and availability).
   - Store headlines in a SQLite database (`headlines.db`).
   - Perform sentiment analysis and statistical tests, displaying a supplementary table (as a figure) with significance markers and effect sizes.
   - Generate a polished bar chart with error bars and significance annotations. The x-axis is labelled **"Sentiment"** and the bars are labelled **"Positive"**, **"Neutral"**, and **"Negative"**.

## How It Works

1. **Data Retrieval:**  
   The `NewsPipeline` class (in `pipeline.py`) checks if headlines are already stored in the database and loads them unless a forced update is specified. It then computes the remaining keywords by comparing the full list (`INCLUSION_KEYWORDS`) with the keywords marked as finished in `searched_keywords.txt`. It instantiates the appropriate scraper (GuardianScraper or NewsAPIScraper) using only the remaining keywords. The GuardianScraper uses `resume_state.json` to track the current page for each keyword, allowing the scraper to resume where it left off.

2. **Data Merging:**  
   New headlines are merged with any existing data from the database and deduplicated before being re-saved.

3. **Analysis & Visualization:**  
   Sentiment scores are computed using NLTK's VADER, and statistical tests (chi-square, ANOVA with eta-squared, Mann–Whitney U with Cliff’s delta) are performed. Results are displayed as a supplementary stats table (rendered as a figure) and visualized in a bar chart.

## License

This project is released under the MIT License.

## Conclusion

The News Analysis Project provides a robust pipeline for collecting, processing, and analyzing newspaper headline sentiment. With flexible update options, resume state functionality, and in-depth statistical analysis, it offers a solid foundation for further news analytics and research.


