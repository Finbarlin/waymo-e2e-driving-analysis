### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Interaction Analysis Plots

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_interaction(all_metrics):
    """
    Deep dive into high interaction score events, to understand the risk context and dynamics.
    Generate two plots:
    1) Risk Context: Scatter plot of Speed vs Interaction Score, colored by Scenario
    2) Dynamics Map: Scatter plot of Max Lateral Accel vs Max Braking, colored by Net Lateral Distance

    :param all_metrics: parsed from classified_metrics.csv
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # 1. Filter High Interaction
    threshold = df['interaction_score'].quantile(0.90)
    hi_df = df[df['interaction_score'] >= threshold].copy()

    if hi_df.empty:
        print(f"No events found above score threshold {threshold:.1f}")
        return

    print(f"Visualizing {len(hi_df)} Critical Events (Score > {threshold:.1f})")

    # =========================================================================
    # FIGURE 1: RISK CONTEXT (Speed vs. Score)
    # =========================================================================
    fig1 = go.Figure()

    unique_scenarios = hi_df['scenario'].unique()
    colors = px.colors.qualitative.Bold

    for i, scen in enumerate(unique_scenarios):
        scen_data = hi_df[hi_df['scenario'] == scen]
        color_code = colors[i % len(colors)]

        fig1.add_trace(go.Scatter(
            x=scen_data['avg_speed_ms'],
            y=scen_data['interaction_score'],
            mode='markers',
            marker=dict(
                size=12,
                color=color_code,
                line=dict(width=1, color='black'),
                opacity=0.8
            ),
            name=scen,
            text=scen_data['scenario'],
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "<b>Speed:</b> %{x:.1f} m/s<br>" +
                "<b>Score:</b> %{y:.1f}<extra></extra>"
            )
        ))

    fig1.update_layout(
        height=500, width=900,
        title_text=f"<b>Risk Context</b> <br><i><sup>Score vs Speed in Different Driving Scenarios</i></sup>",
        template='plotly_white',
        xaxis_title="Avg Speed (m/s)",
        yaxis_title="Interaction Score",
        title_x=0.5,
        title_xanchor='center',
        margin=dict(t=80, l=80, r=80, b=80),
        legend=dict(
            yanchor="top", y=0.98,
            xanchor="right", x=0.98,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="Black",
            borderwidth=1
        )
    )

    fig1.show()

    # =========================================================================
    # FIGURE 2: DYNAMICS MAP (Braking vs. Swerving)
    # =========================================================================
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=hi_df['max_lateral_accel'],
        y=hi_df['max_braking'].abs(),
        mode='markers',
        marker=dict(
            size=14, # Slightly larger for physics emphasis
            color=hi_df['net_lateral_dist_m'],
            colorscale='Viridis',
            line=dict(width=1, color='black'),
            opacity=0.8,
            colorbar=dict(
                title="Net Dist (m)",
                len=1.0,
                thickness=15
            )
        ),
        name='Dynamics',
        text=hi_df['scenario'],
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "<b>Lat G:</b> %{x:.2f} m/s²<br>" +
            "<b>Brake G:</b> -%{y:.2f} m/s²<br>" +
            "<b>Moved:</b> %{marker.color:.1f} m<extra></extra>"
        )
    ))

    fig2.update_layout(
        height=500, width=900,
        title_text=f"<b>Dynamics Map</b> <br><i><sup>Breaking or Swerving with Lateral Movement for top 10% of high interaction evemts</i></sup>",
        template='plotly_white',
        xaxis_title="Max Lateral Accel (m/s²)",
        yaxis_title="Max Braking Force (m/s²)",
        title_x=0.5,
        title_xanchor='center',
        margin=dict(t=80, l=80, r=80, b=80)
    )

    fig2.show()