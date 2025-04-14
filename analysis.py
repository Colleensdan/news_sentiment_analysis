# analysis.py
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from scipy.stats import chi2, f_oneway, mannwhitneyu

# Ensure the VADER lexicon is available.
nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def perform_sentiment_analysis(self, df):
        def classify(text):
            if pd.isnull(text):
                return None, None
            score = self.sia.polarity_scores(text)['compound']
            if score >= 0.05:
                return score, 'positive'
            elif score <= -0.05:
                return score, 'negative'
            else:
                return score, 'neutral'
        df[['compound_score', 'sentiment']] = df.apply(
            lambda row: pd.Series(classify(row['headline'])), axis=1)
        return df

    def get_significance_symbol(self, p):
        if p > 0.05:
            return "ns"
        elif p <= 0.0001:
            return "****"
        elif p <= 0.001:
            return "***"
        elif p <= 0.01:
            return "**"
        else:
            return "*"


    def perform_statistical_tests(self, df):
        """
        Perform chi-square, ANOVA, and Mann–Whitney U tests on the sentiment
        analysis results. Calculate effect sizes (Cramér’s V, eta-squared for ANOVA,
        and Cliff’s delta for the Mann–Whitney U test).
        P-values are formatted: if computed as 0, they are displayed as "<1e-10".
        Returns a dictionary of results, including a supplementary table (DataFrame).
        """
        # Count sentiments from the dataframe.
        sentiment_counts = df['sentiment'].value_counts(dropna=True)
        total_classified = sentiment_counts.sum()

        # Chi-square goodness-of-fit test.
        observed = sentiment_counts.reindex(['positive', 'negative', 'neutral'], fill_value=0).values
        expected = np.array([total_classified / 3] * 3)
        chi2_stat = ((observed - expected) ** 2 / expected).sum()
        chi2_p = chi2.sf(chi2_stat, df=2)

        # ANOVA on compound scores for the three groups.
        group_pos = df[df['sentiment'] == 'positive']['compound_score'].dropna().values
        group_neg = df[df['sentiment'] == 'negative']['compound_score'].dropna().values
        group_neu = df[df['sentiment'] == 'neutral']['compound_score'].dropna().values

        f_stat, anova_p = f_oneway(group_pos, group_neg, group_neu)
        # Calculate eta-squared: proportion of total variance explained by group differences.
        groups = [group_pos, group_neg, group_neu]
        all_data = np.concatenate(groups)
        overall_mean = np.mean(all_data)
        ss_between = sum(len(g) * (np.mean(g) - overall_mean)**2 for g in groups)
        ss_total = sum((x - overall_mean)**2 for x in all_data)
        eta_sq = ss_between / ss_total if ss_total != 0 else np.nan

        # Mann–Whitney U test between positive and negative headlines.
        mwu_stat, mwu_p = mannwhitneyu(group_pos, group_neg, alternative='two-sided')

        # Function to format p-values.
        def format_p(p):
            return "<1e-10" if p == 0 else "{:.4g}".format(p)

        chi2_p_str = format_p(chi2_p)
        anova_p_str = format_p(anova_p)
        mwu_p_str = format_p(mwu_p)

        # Define an inner function for Cliff's delta.
        def cliffs_delta(lst1, lst2):
            n1, n2 = len(lst1), len(lst2)
            # Count pairwise comparisons.
            greater = sum(1 for x in lst1 for y in lst2 if x > y)
            lesser = sum(1 for x in lst1 for y in lst2 if x < y)
            return (greater - lesser) / (n1 * n2) if n1 * n2 > 0 else 0

        raw_cliffs_d = cliffs_delta(group_pos.tolist(), group_neg.tolist())
        # Use a small epsilon to check for near-maximum effect.
        EPS = 1e-9
        if abs(1.0 - raw_cliffs_d) < EPS:
            cliffs_d_value = "~1.0"
        else:
            cliffs_d_value = f"{raw_cliffs_d:.4f}"

        # For chi-square, compute Cramér's V.
        cramers_v = np.sqrt(chi2_stat / (total_classified * (3 - 1))) if total_classified > 0 else np.nan
        cramers_v_str = f"{cramers_v:.4f}"

        # Prepare significance symbols (assuming you have a function get_significance_symbol)
        chi2_sig = self.get_significance_symbol(chi2_p)
        anova_sig = self.get_significance_symbol(anova_p)
        mwu_sig = self.get_significance_symbol(mwu_p)

        # Build the supplementary table as a DataFrame.
        supp_table = pd.DataFrame({
            "Test": ["Chi-square", "ANOVA", "Mann–Whitney U"],
            "Statistic": [chi2_stat, f_stat, mwu_stat],
            "p-value": [chi2_p_str, anova_p_str, mwu_p_str],
            "Effect Size": [cramers_v_str, f"{eta_sq:.4f}" if not np.isnan(eta_sq) else "NaN", cliffs_d_value],
            "Significance": [chi2_sig, anova_sig, mwu_sig]
        })

        return {
            "sentiment_counts": sentiment_counts,
            "total_classified": total_classified,
            "chi2_stat": chi2_stat,
            "chi2_p": chi2_p,
            "cramers_v": cramers_v,
            "anova_f": f_stat,
            "anova_p": anova_p,
            "eta_squared": eta_sq,
            "mannwhitney_u": mwu_stat,
            "mannwhitney_p": mwu_p,
            "cliffs_delta": raw_cliffs_d,
            "supplementary_table": supp_table
        }
