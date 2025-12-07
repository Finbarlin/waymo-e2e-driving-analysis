### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Score Distribution Plots

import plotly.express as px
import pandas as pd
import pandas as pd

def iqr(x):
    """
    Calculate the interquartile range (IQR) of a pandas Series.
    
    :param x: input series
    :return: interquartile range
    """
    return x.quantile(0.75) - x.quantile(0.25)

def plot_interaction_score(all_metrics):
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

def plot_physics_deep_dive(all_metrics):
    """
    Based on the interaction score, plot the score variance/stability of each scenario type, as an indication of how risky they are.
    
    :param all_metrics: pd.DataFrame
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # Clean up Scenario Names for nicer legends
    df['scenario_clean'] = df['scenario'].str.replace('/', '/<br>')

    # =========================================================================
    # FIGURE: THE RISK PROFILE (Box Plot)
    # =========================================================================
    # Insight: Shows the variance/stability of each scenario type

    sorted_scenarios = df.groupby('scenario')['interaction_score'].median().sort_values(ascending=False).index

    fig = px.box(
        df,
        x='scenario',
        y='interaction_score',
        color='scenario',
        points='outliers',
        hover_data=['avg_speed_ms'],
        category_orders={'scenario': list(sorted_scenarios)},
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    #fig.update_yaxes(range=[0, 5])
    fig.update_layout(
        height=600, width=900,
        title_text=(
            "<b> Risk Profile:</b> Score Distribution by Scenario<br>"
            "<sup><i>(Box shows variance; Dots are outliers)</i></sup>"
        ),
        title_x=0.5, title_xanchor='center',
        template='plotly_white',
        showlegend=False,
        margin=dict(t=100, l=80, r=80, b=80),
        xaxis_title="Scenario", yaxis_title="Interaction Score"
    )
    fig.show()

    # End of plot_physics_deep_dive

def plot_physics_deep_dive_optional(all_metrics):
    """
    Further analysis on physics metrics, optional for final report.
    Plots 1) The maneuver map: Distinguishes "Swerving" (staying in lane) from "Changing Lanes"
          2) The danger zone: how strong does the deceleration look like for different scenarios
    
    :param all_metrics: pd.DataFrame
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # 1. Clean up Scenario Names for nicer legends
    df['scenario_clean'] = df['scenario'].str.replace('/', '/<br>')

    # =========================================================================
    # FIGURE 1: THE MANEUVER MAP (Displacement vs. Force)
    # =========================================================================
    # Insight: Distinguishes "Swerving" (staying in lane) from "Changing Lanes"

    fig1 = px.scatter(
        df,
        x='net_lateral_dist_m',
        y='max_lateral_accel',
        color='interaction_score',
        size='avg_speed_ms',
        hover_name='scenario',
        hover_data={'scene_id': True, 'net_lateral_dist_m': ':.2f', 'max_lateral_accel': ':.2f'},
        color_continuous_scale='Viridis', # Professional gradient
        title='<b>1. The Maneuver Map:</b> Displacement vs. G-Force',
        labels={'net_lateral_dist_m': 'Net Displacement (m)', 'max_lateral_accel': 'Lateral G-Force (m/s²)'}
    )

    # --- SEMANTIC ZONES (The "Why") ---

    # Zone A: Aggressive Cut-In (High Force + High Dist)
    fig1.add_shape(type="rect",
        x0=2.5, x1=df['net_lateral_dist_m'].max()*1.1,
        y0=2.0, y1=df['max_lateral_accel'].max()*1.1,
        fillcolor="red", opacity=0.1, layer="below", line_width=0
    )
    fig1.add_annotation(
        x=0.98, y=0.98, xref="paper", yref="paper",
        text="<b>Aggressive Cut-In</b>", font=dict(color="darkred", size=12),
        showarrow=False, xanchor="right"
    )

    # Zone B: Evasive Swerve (High Force + Low Dist)
    fig1.add_shape(type="rect",
        x0=0, x1=1.5,
        y0=2.0, y1=df['max_lateral_accel'].max()*1.1,
        fillcolor="orange", opacity=0.1, layer="below", line_width=0
    )
    fig1.add_annotation(
        x=0.02, y=0.98, xref="paper", yref="paper",
        text="<b>Evasive Swerve</b>", font=dict(color="darkorange", size=12),
        showarrow=False, xanchor="left"
    )

    # Zone C: Normal Lane Change (Low Force + High Dist)
    fig1.add_shape(type="rect",
        x0=2.5, x1=df['net_lateral_dist_m'].max()*1.1,
        y0=0, y1=2.0,
        fillcolor="green", opacity=0.1, layer="below", line_width=0
    )
    fig1.add_annotation(
        x=0.98, y=0.05, xref="paper", yref="paper",
        text="<b>Normal Lane Change</b>", font=dict(color="darkgreen", size=12),
        showarrow=False, xanchor="right"
    )

    fig1.update_layout(
        height=600, width=900,
        title_text=(
            "<b>1. The Maneuver Map:</b> Displacement vs. G-Force<br>"
            "<sup><i>(Distinguishes Lane Changes from Evasive Swerves)</i></sup>"
        ),
        title_x=0.5, title_xanchor='center',
        template='plotly_white',
        margin=dict(t=100, l=80, r=80, b=80)
    )
    fig1.show()
    
    # =========================================================================
    # FIGURE 2: THE DANGER ZONE (Longitudinal Risk)
    # =========================================================================

    # We use -0.1 to filter out floating point noise/coasting
    braking_df = df[df['max_braking'] < -0.1].copy()

    fig2 = px.scatter(
        braking_df,
        x='avg_speed_ms',
        y='max_braking', # These will now all be negative
        color='scenario',
        symbol='scenario',
        hover_name='scene_id',
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # Reverse Y axis logic (Braking)
    fig2.update_yaxes(autorange="reversed")

    # Threshold Line
    fig2.add_hline(y=-3.0, line_dash="dash", line_color="red")
    fig2.add_annotation(
        x=df['avg_speed_ms'].max(), y=-3.05,
        text="<b>Hard Braking Threshold (-3.0)</b>",
        showarrow=False, font=dict(color="red", size=10),
        xanchor="right", yanchor="bottom"
    )

    fig2.update_layout(
        height=600, width=900,
        title_text=(
            "<b>2. The Danger Zone:</b> Speed vs. Braking Intensity<br>"
            "<sup><i>(Filtered: Only showing events with actual deceleration < -0.1 m/s²)</i></sup>"
        ),
        title_x=0.5, title_xanchor='center',
        template='plotly_white',
        xaxis_title="Vehicle Speed (m/s)",
        yaxis_title="Deceleration (m/s²) [Negative = Braking]",
        margin=dict(t=100, l=80, r=80, b=80)
    )
    fig2.show()