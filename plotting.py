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


def plot_sentiment_distribution(df, stats_results=None):
    """
    Generate a polished bar chart of headline sentiment distribution with error bars.
    The x-axis is labelled "Sentiment" and the three bars are labelled "Positive", "Neutral", "Negative".
    If stats_results is provided, annotate significance between the Positive and Negative bars.
    """
    # Set the category order we want to display.
    # Note: The sentiment analysis produces lowercase values, so we use lower() when retrieving counts.
    categories = ['Positive', 'Neutral', 'Negative']
    
    counts = []
    errors = []
    for cat in categories:
        # Retrieve counts by matching lowercase versions.
        n = int(df['sentiment'].value_counts().get(cat.lower(), 0))
        counts.append(n)
        errors.append(np.sqrt(n))
    
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.style.use('ggplot')
    positions = np.arange(len(categories))
    
    bars = ax.bar(positions, counts, width=0.6, yerr=errors, capsize=5)
    
    # Set the x-axis label and tick labels.
    ax.set_xlabel("Sentiment", fontsize=12, labelpad=20)
    ax.set_xticks(positions)
    ax.set_xticklabels(categories, fontsize=12)
    
    ax.set_title("Sentiment Distribution of Newspaper Headlines", fontsize=14, weight='bold')
    ax.set_ylabel("Number of Headlines", fontsize=12)
    ax.grid(True, which="both", linestyle='--', linewidth=0.5, alpha=0.7)
    
    # If statistical results exist, add significance annotation between positive and negative bars.
    if stats_results is not None:
        p_val = stats_results.get("mannwhitney_p", None)
        if p_val is not None:
            if p_val > 0.05:
                sig_symbol = "ns"
            elif p_val <= 0.0001:
                sig_symbol = "****"
            elif p_val <= 0.001:
                sig_symbol = "***"
            elif p_val <= 0.01:
                sig_symbol = "**"
            else:
                sig_symbol = "*"
            
            # Positive bar is at index 0; Negative bar is at index 2.
            x1, x2 = positions[0], positions[2]
            y1 = counts[0] + errors[0]
            y2 = counts[2] + errors[2]
            line_y = max(y1, y2) + 5  # Position line above the tallest of the two bars
            ax.plot([x1, x1, x2, x2], [line_y, line_y + 2, line_y + 2, line_y],
                    lw=1.5, c='black')
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, line_y + 3, sig_symbol,
                    ha='center', va='bottom', fontsize=14, color='black')
    
    plt.tight_layout()
    plt.show()
    return fig
