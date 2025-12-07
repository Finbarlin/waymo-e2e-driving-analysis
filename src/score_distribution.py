### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Score Distribution Plots

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set_theme(style="whitegrid")

def iqr(x):
    """
    Calculate the interquartile range (IQR) of a pandas Series.
    
    :param x: input series
    :return: interquartile range
    """
    return x.quantile(0.75) - x.quantile(0.25)

def interaction_stats_table(all_metrics):
    """
    Display a summary table of interaction score statistics for each scenario type.
    
    :param all_metrics: input dataframe
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # Clean up Scenario Names for nicer legends
    df['scenario_clean'] = df['scenario'].str.replace('/', '/<br>')
    # =========================================================================
    # TABLE: THE RISK PROFILE STATS SUMMARY
    # =========================================================================
    # Insight: List the statistics for each scenario type
    stats_df = df.groupby('scenario')['interaction_score'].agg(
        median='median',
        iqr=iqr,
        max='max',
        min='min'
    ).reset_index().sort_values(by='median', ascending=False)
    print("\n=== RISK PROFILE STATS SUMMARY ===")
    print(stats_df.to_markdown(index=False))
    # End of plot_interaction_score

def plot_interaction_score(all_metrics):
    """
    Plots the score variance/stability of each scenario type.
    """
    df = pd.DataFrame(all_metrics)

    # Clean up Scenario Names for nicer legends
    df['scenario_clean'] = df['scenario'].str.replace('/', '/\n')

    # Sort scenarios by median interaction score
    order = df.groupby('scenario_clean')['interaction_score'].median().sort_values(ascending=False).index

    
    plt.figure(figsize=(12, 6))
    
    # BOX PLOT
    sns.boxplot(
        data=df, 
        x='scenario_clean', 
        y='interaction_score', 
        order=order,
        palette="bright",
        hue='scenario_clean'
    )
    
    plt.suptitle("Risk Profile: Score Distribution by Scenario", fontsize=18, weight='bold', y=0.98)
    
    # title = The Subtitle (Attached to the plot axis, with padding)
    plt.title("(Box shows variance; Dots are outliers)", fontsize=11, style='italic')
    
    plt.ylabel("Interaction Score", fontsize=12)
    plt.xlabel("Scenario", fontsize=12)
    plt.xticks(rotation=15) 
    
    plt.legend([],[], frameon=False)
    
    plt.show()