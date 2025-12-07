### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Baseline Plots

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def plot_kinematic_statics(all_metrics):
    """
    Plot statistics of input data such as speed distribution, braking intensity and lateral displacement before classification, to have a general idea of the dataset.
    
    :param all_metrics: list of dict, parsed from metrics.csv
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # Initialize 1x3 Dashboard
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "<b><i>Speed Distribution</i></b>",
            "<b><i>Braking Intensity</i></b>",
            "<b><i>Lateral Displacement</i></b>"
        ),
        horizontal_spacing=0.1
    )

    # --- HELPER: SMOOTH CURVE GENERATOR ---
    def get_trend_line(data, bins=30):
        counts, bin_edges = np.histogram(data, bins=bins)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        return bin_centers, counts

    # --- PLOT 1: SPEED ---
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=df['avg_speed_ms'], nbinsx=25,
            marker_color='skyblue', opacity=0.6,
            marker_line_color='black', marker_line_width=0.5,
            name='Speed', showlegend=False,
            hovertemplate="<b>Speed:</b> %{x:.1f} m/s<br><b>Count:</b> %{y}<extra></extra>"
        ), row=1, col=1
    )
    # Trend
    sx, sy = get_trend_line(df['avg_speed_ms'], bins=25)
    fig.add_trace(
        go.Scatter(
            x=sx, y=sy, mode='lines',
            line=dict(color='darkblue', width=3, shape='spline'),
            name='Speed Trend', showlegend=False, hoverinfo='skip'
        ), row=1, col=1
    )
    # Mean Line
    fig.add_vline(x=df['avg_speed_ms'].mean(), line_dash="dash", line_color="darkblue", row=1, col=1)

    # Annotation
    fig.add_annotation(
        x=df['avg_speed_ms'].mean(), y=0.95, yref="y domain",
        text=f"Mean: {df['avg_speed_ms'].mean():.1f} m/s",
        showarrow=False, font=dict(color="darkblue", size=10), row=1, col=1
    )

    # --- PLOT 2: BRAKING ---
    braking_data = df[df['max_braking'] < -0.1]['max_braking']

    # Histogram
    fig.add_trace(
        go.Histogram(
            x=braking_data, nbinsx=30,
            marker_color='coral', opacity=0.6,
            marker_line_color='black', marker_line_width=0.5,
            name='Braking', showlegend=False,
            hovertemplate="<b>Decel:</b> %{x:.1f} m/s²<br><b>Count:</b> %{y}<extra></extra>"
        ), row=1, col=2
    )
    # Trend
    if len(braking_data) > 0:
        bx, by = get_trend_line(braking_data, bins=30)
        fig.add_trace(
            go.Scatter(
                x=bx, y=by, mode='lines',
                line=dict(color='darkred', width=3, shape='spline'),
                name='Braking Trend', showlegend=False, hoverinfo='skip'
            ), row=1, col=2
        )
    # Threshold
    fig.add_vline(x=-3.0, line_dash="dash", line_color="red", row=1, col=2)
    fig.add_annotation(
        x=-3.0, y=1.05, yref="y2 domain",
        text="<i>Hard Brake<br>(-3.0)</i>", xanchor="right",
        showarrow=False, font=dict(color="red"),
        row=1, col=2
    )

    # --- PLOT 3: LATERAL ---
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=df['net_lateral_dist_m'], nbinsx=30,
            marker_color='lightgreen', opacity=0.6,
            marker_line_color='black', marker_line_width=0.5,
            name='Lateral', showlegend=False,
            hovertemplate="<b>Dist:</b> %{x:.1f} m<br><b>Count:</b> %{y}<extra></extra>"
        ), row=1, col=3
    )
    # Trend
    lx, ly = get_trend_line(df['net_lateral_dist_m'], bins=30)
    fig.add_trace(
        go.Scatter(
            x=lx, y=ly, mode='lines',
            line=dict(color='darkgreen', width=3, shape='spline'),
            name='Lateral Trend', showlegend=False, hoverinfo='skip'
        ), row=1, col=3
    )
    # Threshold
    fig.add_vline(x=3.7, line_dash="dash", line_color="green", row=1, col=3)
    fig.add_annotation(
        x=3.7, y=1.05, yref="y3 domain", text="<i>Avg. Lane Wdith<br>3.7m</i>",
        showarrow=False, font=dict(color="darkgreen", size=10), xanchor="right",
        row=1, col=3
    )

    # --- STYLING ---
    fig.update_layout(
        height=400, width=1500,
        title_text="<b>Motion Data</b>",
        title_x=0.5, title_xanchor='center',
        template='plotly_white',
        margin=dict(t=100, l=40, r=40, b=40),
        bargap=0.1
    )

    # Axis Labels
    fig.update_xaxes(title_text="Avg Speed (m/s)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)

    fig.update_xaxes(title_text="Max Deceleration (m/s²)", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)

    fig.update_xaxes(title_text="Net Lateral Dist (m)", row=1, col=3)
    fig.update_yaxes(title_text="Count", row=1, col=3)

    fig.show()


def plot_scenario_distribution(all_metrics):
    """
    Plot a bar chart showing the distribution of driving scenarios, to understand current scenarios we have.
    
    :param all_metrics: list of dict, parsed from metrics.csv
    :return: None
    """
    df = pd.DataFrame(all_metrics)

    # Count and Sort
    counts = df['scenario'].value_counts().reset_index()
    counts.columns = ['scenario', 'count']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=counts['scenario'],
        y=counts['count'],
        marker_color='teal',
        marker_line_color='black',
        marker_line_width=1.5,
        text=counts['count'],
        textposition='auto',
        name='Scenarios',
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
    ))

    fig.update_layout(
        height=500, width=800,
        title_text="<b>Driving Scenario Distribution</b>",
        title_x=0.5, title_xanchor='center',
        template='plotly_white',
        xaxis_title="Scenario Type",
        yaxis_title="Count",
        margin=dict(t=80, l=40, r=40, b=80),
        xaxis_tickangle=-15 # Slight tilt for readability
    )

    fig.show()