### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Interaction Analysis Plots

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Set theme
sns.set_theme(style="whitegrid")

def plot_interaction(all_metrics):
    """
    Seaborn version: Deep dive into high interaction score events.
    1) Risk Context: Speed vs Interaction Score (Categorical Color)
    2) Dynamics Map: Lateral Accel vs Max Braking (Continuous Gradient Color)
    """
    df = pd.DataFrame(all_metrics)

    # 1. Filter High Interaction (Top 10%)
    threshold = df['interaction_score'].quantile(0.90)
    hi_df = df[df['interaction_score'] >= threshold].copy()

    if hi_df.empty:
        print(f"No events found above score threshold {threshold:.1f}")
        return

    print(f"Visualizing {len(hi_df)} Critical Events (Score > {threshold:.1f})")

    # Clean up names for legend
    hi_df['scenario_clean'] = hi_df['scenario'].str.replace('/', '/\n')
    
    # Calculate Abs Braking for Plot 2
    hi_df['braking_abs'] = hi_df['max_braking'].abs()

    # =========================================================================
    # FIGURE 1: RISK CONTEXT (Speed vs. Score)
    # =========================================================================
    
    plt.figure(figsize=(10, 6))
    
    sns.scatterplot(
        data=hi_df,
        x='avg_speed_ms',
        y='interaction_score',
        hue='scenario_clean',
        palette='bright', # High contrast
        s=100,            # Marker size
        alpha=0.8,
        edgecolor='black'
    )

    # Titles
    plt.suptitle("Risk Context", fontsize=16, weight='bold', y=0.98)
    plt.title(f"(Score vs Speed for top 10% events > {threshold:.1f})", fontsize=11, style='italic', pad=10)
    
    plt.xlabel("Avg Speed (m/s)")
    plt.ylabel("Interaction Score")
    
    # Move legend outside
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, title="Scenario")
    
    plt.show()

    # =========================================================================
    # FIGURE 2: DYNAMICS MAP (Braking vs. Swerving)
    # =========================================================================
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # We use 'hue' for the color, but we turn off the default legend
    # so we can build a proper Colorbar later.
    scatter = sns.scatterplot(
        data=hi_df,
        x='max_lateral_accel',
        y='braking_abs',
        hue='net_lateral_dist_m',
        palette='viridis',
        s=120, # Slightly larger for emphasis
        alpha=0.9,
        edgecolor='black',
        legend=False, # We will make our own colorbar
        ax=ax
    )
    
    # --- CUSTOM COLORBAR LOGIC ---
    # This creates the gradient bar on the right side
    norm = plt.Normalize(hi_df['net_lateral_dist_m'].min(), hi_df['net_lateral_dist_m'].max())
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])
    
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label('Net Lateral Dist (m)', rotation=270, labelpad=15)
    # -----------------------------

    # Titles
    plt.suptitle("Dynamics Map", fontsize=16, weight='bold', y=0.98)
    plt.title("(Braking vs Swerving for Critical Events)", fontsize=11, style='italic', pad=10)

    plt.xlabel("Max Lateral Accel (m/s²)")
    plt.ylabel("Max Braking Force (m/s²)")

    plt.show()