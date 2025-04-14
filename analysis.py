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
        sentiment_counts = df['sentiment'].value_counts(dropna=True)
        total_classified = sentiment_counts.sum()

        # Chi-square goodness-of-fit test.
        observed = sentiment_counts.reindex(['positive', 'negative', 'neutral'], fill_value=0).values
        expected = np.array([total_classified / 3] * 3)
        chi2_stat = ((observed - expected) ** 2 / expected).sum()
        chi2_p = chi2.sf(chi2_stat, df=2)

        # ANOVA on compound scores.
        group_pos = df[df['sentiment'] == 'positive']['compound_score'].dropna()
        group_neg = df[df['sentiment'] == 'negative']['compound_score'].dropna()
        group_neu = df[df['sentiment'] == 'neutral']['compound_score'].dropna()
        f_stat, anova_p = f_oneway(group_pos, group_neg, group_neu)

        # Mann–Whitney U test between positive and negative.
        mwu_stat, mwu_p = mannwhitneyu(group_pos, group_neg, alternative='two-sided')

        # Effect sizes.
        k = 3
        cramers_v = np.sqrt(chi2_stat / (total_classified * (k - 1))) if total_classified > 0 else np.nan

        def cliffs_delta(lst1, lst2):
            n1, n2 = len(lst1), len(lst2)
            greater = sum(1 for x in lst1 for y in lst2 if x > y)
            lesser = sum(1 for x in lst1 for y in lst2 if x < y)
            return (greater - lesser) / (n1 * n2) if n1 * n2 > 0 else 0
        cliffs_d = cliffs_delta(group_pos.tolist(), group_neg.tolist())

        chi2_sig = self.get_significance_symbol(chi2_p)
        anova_sig = self.get_significance_symbol(anova_p)
        mwu_sig = self.get_significance_symbol(mwu_p)

        supp_table = pd.DataFrame({
            "Test": ["Chi-square", "ANOVA", "Mann–Whitney U"],
            "Statistic": [chi2_stat, f_stat, mwu_stat],
            "p-value": [chi2_p, anova_p, mwu_p],
            "Effect Size": [cramers_v, np.nan, cliffs_d],
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
            "mannwhitney_u": mwu_stat,
            "mannwhitney_p": mwu_p,
            "cliffs_delta": cliffs_d,
            "supplementary_table": supp_table
        }
