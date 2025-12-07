### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Baseline Plots

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sns.set_theme(style="whitegrid")

def plot_kinematic_statics(all_metrics):
    """
    Seaborn version of kinematic statistics 1x3 dashboard.
    """
    df = pd.DataFrame(all_metrics)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Motion Data', fontsize=16, weight='bold', y=1.05)

    # --- PLOT 1: SPEED ---
    sns.histplot(
        data=df, x='avg_speed_ms', ax=axes[0], 
        kde=True, color='skyblue', bins=25,
        line_kws={'linewidth': 3}
    )
    
    # Mean Line & Annotation
    mean_speed = df['avg_speed_ms'].mean()
    axes[0].axvline(mean_speed, color='darkblue', linestyle='--', linewidth=2)
    axes[0].text(
        x=mean_speed, y=axes[0].get_ylim()[1]*0.95, 
        s=f" Mean: {mean_speed:.1f} m/s", 
        color='darkblue', fontweight='bold'
    )
    axes[0].set_title("Speed Distribution", fontweight='bold')
    axes[0].set_xlabel("Avg Speed (m/s)")

    # --- PLOT 2: BRAKING ---
    braking_data = df[df['max_braking'] < -0.1]
    
    sns.histplot(
        data=braking_data, x='max_braking', ax=axes[1], 
        kde=True, color='coral', bins=30,
        line_kws={'linewidth': 3}
    )
    
    # Threshold Line & Annotation
    axes[1].axvline(-3.0, color='red', linestyle='--', linewidth=2)
    axes[1].text(
        x=-3.0, y=axes[1].get_ylim()[1]*0.95, 
        s=" Hard Brake\n (-3.0)", 
        color='red', ha='left', va='top'
    )
    axes[1].set_title("Braking Intensity", fontweight='bold')
    axes[1].set_xlabel("Max Deceleration (m/s²)")

    # --- PLOT 3: LATERAL ---
    sns.histplot(
        data=df, x='net_lateral_dist_m', ax=axes[2], 
        kde=True, color='lightgreen', bins=30,
        line_kws={'linewidth': 3}
    )
    
    # Threshold Line & Annotation
    axes[2].axvline(3.7, color='green', linestyle='--', linewidth=2)
    axes[2].text(
        x=3.7, y=axes[2].get_ylim()[1]*0.95, 
        s=" Avg Lane\n Width (3.7m)", 
        color='darkgreen', ha='right', va='top'
    )
    axes[2].set_title("Lateral Displacement", fontweight='bold')
    axes[2].set_xlabel("Net Lateral Dist (m)")

    plt.tight_layout()
    plt.show()


def plot_scenario_distribution(all_metrics):
    """
    Seaborn version of scenario distribution bar chart.
    """
    df = pd.DataFrame(all_metrics)

    # Count and Sort
    counts = df['scenario'].value_counts().reset_index()
    counts.columns = ['scenario', 'count']

    plt.figure(figsize=(10, 6))
    
    # Create Bar Plot
    ax = sns.barplot(
        data=counts, x='scenario', y='count', 
        color='teal', edgecolor='black'
    )

    # Add Text Labels on top of bars
    ax.bar_label(ax.containers[0], padding=3)

    plt.title("Driving Scenario Distribution", fontsize=14, weight='bold')
    plt.xlabel("Scenario Type")
    plt.ylabel("Count")
    plt.xticks(rotation=15)
    
    plt.tight_layout()
    plt.show()