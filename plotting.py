# plotting.py
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt

def plot_supplementary_table(supp_table):
    """
    Generate a matplotlib figure that displays the supplementary statistical table
    with adequate space for all values. The header row is shaded and bold for clarity.
    
    Parameters:
      - supp_table: A pandas DataFrame containing the supplementary table.
      
    Returns:
      A matplotlib figure object with the formatted table.
    """
    # Estimate rows and columns
    n_rows, n_cols = supp_table.shape

    # Create a figure sized to fit the table content
    # Increase width or height if columns/rows are large
    fig_width = 2 + n_cols * 2
    fig_height = 2 + 0.5 * n_rows
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.axis('tight')
    ax.axis('off')

    # Create the table
    table = ax.table(
        cellText=supp_table.values,
        colLabels=supp_table.columns,
        loc='center',
        cellLoc='center'
    )

    # Let Matplotlib auto-size columns based on content
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Attempt to auto-fit column widths based on content
    table.auto_set_column_width(col=list(range(n_cols)))

    # Optionally scale the table if further space is needed
    # (scale_x, scale_y) = (1.0, 1.2) for instance
    table.scale(1.0, 1.2)

    # Shade and bold the header row (row == 0)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#cccccc')  # light grey
            cell.set_text_props(weight='bold')

    fig.tight_layout()
    return fig

import matplotlib.pyplot as plt
import numpy as np
import os

def plot_sentiment_distribution(df, stats_results=None):
    """
    Generate a polished bar chart of headline sentiment distribution with error bars.
    The x-axis is labelled "Sentiment" and bars are labeled "Positive", "Neutral", and "Negative".
    If statistical results are provided, draw stacked significance lines for:
      - Positive vs. Negative
      - Positive vs. Neutral
      - Negative vs. Neutral
    and save the figure to the 'figures' folder.
    """
    # Category names expected in df['sentiment'] are lowercase
    categories = ['positive', 'neutral', 'negative']
    display_labels = ['Positive', 'Neutral', 'Negative']

    # Calculate counts and approximate errors (Poisson ~ sqrt(n))
    counts = []
    errors = []
    for cat in categories:
        n = int(df['sentiment'].value_counts().get(cat, 0))
        counts.append(n)
        errors.append(np.sqrt(n))

    fig, ax = plt.subplots(figsize=(8, 6))
    plt.style.use('ggplot')
    positions = np.arange(len(categories))

    # Create bar chart with error bars
    bars = ax.bar(positions, counts, width=0.6, yerr=errors, capsize=5, color="#87CEFA")

    ax.set_xlabel("Sentiment", fontsize=12, labelpad=20)
    ax.set_ylabel("Number of Headlines", fontsize=12)
    ax.set_title("Sentiment Distribution of Newspaper Headlines", fontsize=14, weight='bold')
    ax.set_xticks(positions)
    ax.set_xticklabels(display_labels, fontsize=12)
    ax.grid(True, which="both", linestyle='--', linewidth=0.5, alpha=0.7)

    # Helper function for significance symbol
    def get_sig_symbol(p):
        if p is None:
            return None
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

    # If we have stats, draw stacked lines for three pairwise comparisons
    if stats_results is not None:
        # Mann–Whitney p-values from your analysis:
        p_pos_neg = stats_results.get("mannwhitney_p", None)           # pos vs neg
        p_pos_neu = stats_results.get("mannwhitney_p_pos_neu", None)   # pos vs neu
        p_neg_neu = stats_results.get("mannwhitney_p_neg_neu", None)   # neg vs neu

        # We'll use the maximum bar height to choose an offset. 
        # The offsets array sets how many "levels" above the bar each line will be.
        max_bar = max(counts[i] + errors[i] for i in range(len(counts)))
        base_offset = 0.03 * max_bar  # A fraction of the highest bar as a vertical gap

        # We'll define an ordered list of comparisons: (start_index, end_index, p_val, offset_level)
        # offset_level is how many "steps" above the top we'll place the line.
        comparisons = [
            (0, 2, p_pos_neg, 3),  # pos vs neg
            (0, 1, p_pos_neu, 2),  # pos vs neu
            (1, 2, p_neg_neu, 1)   # neg vs neu
        ]

        for start_idx, end_idx, p_val, level in comparisons:
            sig = get_sig_symbol(p_val)
            if sig is None:
                continue  # no data
            # Determine the y positions for start_idx and end_idx
            y_start = counts[start_idx] + errors[start_idx]
            y_end = counts[end_idx] + errors[end_idx]
            # The line is placed a certain offset above the max of y_start, y_end
            line_y = max(y_start, y_end) + base_offset * level

            # Draw horizontal bracket
            ax.plot([start_idx, start_idx, end_idx, end_idx],
                    [line_y, line_y + 2, line_y + 2, line_y],
                    lw=1.5, c='black')
            # Place significance symbol in the middle
            mid_x = (start_idx + end_idx) / 2
            ax.text(mid_x, line_y + 4, sig, ha='center', va='bottom', fontsize=14, color='black')

    plt.tight_layout()

    # Ensure figures folder exists
    figures_dir = "figures"
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    # Save and show
    fig_path = os.path.join(figures_dir, "plot_sentiment_distribution.png")
    plt.savefig(fig_path)
    print(f"Figure saved to {fig_path}")

    plt.show()
    return fig
