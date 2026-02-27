from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data_prep import DAYS_ORDER, Metrics


def fig_overview(df: pd.DataFrame, m: Metrics) -> go.Figure:

    heatmap_data = df.groupby(["week_commencing", "day_of_week"]).size().reset_index(name="count")
    heatmap_pivot = (
        heatmap_data.pivot(index="day_of_week", columns="week_commencing", values="count")
        .fillna(0)
        .reindex(DAYS_ORDER)
    )
    heatmap_pivot = heatmap_pivot.fillna(0)

    x_labels = [d.strftime('%b %Y') if i == 0 or d.month != heatmap_pivot.columns[i-1].month else ""
            for i, d in enumerate(heatmap_pivot.columns)]

    # Create GitHub-style Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Greens',
        xgap=3, 
        ygap=3,
        showscale=True,
        colorbar=dict(
            thickness=12,
            len=0.2,            
            x=0.95, y=-0.23,   
            xanchor='right', yanchor='top',
            orientation='h',
            tickvals=[],    
        ),
        hovertemplate="Week: %{x|%d %b %Y}<br>Day: %{y}<br>Apps: <b>%{z:d}</b><extra></extra>"
    ))
    fig.update_traces(
        colorbar=dict(
            thickness=12,
            len=0.2,
            x=0.95, 
            y=-0.18,
            xanchor='right', 
            yanchor='middle',
            orientation='h',
            tickvals=[],
        ),
        selector=dict(type='heatmap')
    )

    fig.update_layout(
        title_text='<b>WEEKLY APPLICATION INTENSITY</b>',
        title_x=0.0,
        title_y=0.98,
        xaxis=dict(
            tickmode='array',
            tickvals=heatmap_pivot.columns,
            ticktext=x_labels,
            side='top',
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11)
        ),
        plot_bgcolor='white',
        margin=dict(t=120, b=80, l=80, r=40), 
        height=400,
        
        annotations=[
            dict(
                text="Less", x=0.75, y=-0.23,
                xref="paper", yref="paper",
                showarrow=False, font=dict(size=12, color="gray")
            ),
            dict(
                text="More", x=0.98, y=-0.23,
                xref="paper", yref="paper",
                showarrow=False, font=dict(size=12, color="gray")
            )
        ]
    )

    return fig


def fig_funnel(m: Metrics) -> go.Figure:
    stages = ["<b>Applications</b> 📤", "<b>Replies</b> 📩", "<b>Interviews</b> 🤝"]
    values = [m.total_apps, m.replied, m.interviews]

    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            insidetextfont=dict(size=16, color="white"),
            marker = {"color": ['#1D446D', '#5FB1C1', '#B34138']},
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Success Rate: %{percentInitial:.1%}<br>" + 
                "<extra></extra>"
            )
        )
    )
    fig.update_layout(title_text="<b>JOB SEARCH CONVERSION</b>", height=480, template="plotly_white")

    return fig

def fig_minimalistic_funnel(m: Metrics) -> go.Figure:
    stages = ["<b>Applications</b> 📤", "<b>Replies</b> 📩", "<b>Interviews</b> 🤝"]
    values = [m.total_apps, m.replied, m.interviews]

    initial_value = values[0]
    percentages = [(v / initial_value) * 100 for v in values]
    colors = ['#1D446D', '#5FB1C1', '#B34138'] 

    fig = go.Figure()

    for i, (stage, value, pct, color) in enumerate(zip(stages, values, percentages, colors)):
        fig.add_trace(go.Bar(
            y=[stage],
            x=[value],
            orientation='h',
            # Shift the start of the bar to the left by half the value
            base=[-value/2 for _ in range(1)], 
            marker=dict(
                color=color,
                cornerradius=15 # Adjusting rounding
            ),
            text=f'<b>{value}</b><br>{pct:.1f}%',
            textposition='inside',
            insidetextanchor='middle',
            insidetextfont=dict(size=14, color="white"), # if i > 0 else "black"),
            width=0.9, 
            customdata=[[pct, value]],
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Value: %{customdata[1]}<br>" +  # Take the second value from customdata
                "Success Rate: %{customdata[0]:.1f}%<br>" + 
                "<extra></extra>"
            ),
            showlegend=False
        ))

    fig.update_layout(
        title_text='<b>JOB SEARCH CONVERSION</b>',
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            # Fix the range so that the funnel does not "jump"
            range=[-max(values)*0.6, max(values)*0.6] 
        ),
        yaxis=dict(
            autorange="reversed", 
            tickfont=dict(size=14),
            showline=False
        ),
        template="plotly_white",
        height=400,
        bargap=0.2,
        #margin=dict(t=80, b=20) # Can adjust the indents to center it visually
    )

    return fig


def fig_response_time(df: pd.DataFrame, m: Metrics) -> go.Figure:

    plot_data = df.dropna(subset=["response_time_days"]).copy()
    fig = px.histogram(
        plot_data,
        x="response_time_days",
        nbins=20,
        title="<b>RESPONSE TIME DISTRIBUTION (Mean vs Median)</b>",
        labels={"response_time_days": "Response time (days)"},
        template="plotly_white",
        color_discrete_sequence=['#5FB1C1']
    )

    # Setting the vertical line for MEAN
    if m.avg_response_time_days is not None:
        fig.add_vline(
            x=m.avg_response_time_days,
            line_dash="dash",
            line_color="#1D446D",
            line_width=2,
            annotation_text=f"Mean: {m.avg_response_time_days:.1f}d",
            annotation_position="top right",
            annotation_font_color="#1D446D",
            annotation_yshift=10, 
        )

    # Setting the vertical line for MEDIAN
    if m.median_response_time_days is not None:
        fig.add_vline(
            x=m.median_response_time_days,
            line_dash="solid",
            line_color="#1D446D",
            line_width=2,
            annotation_text=f"Median: {m.median_response_time_days:.0f}d",
            annotation_position="top left",
            annotation_font_color="#1D446D",
            annotation_yshift=10,
        )

    # Align the height of all annotations and add some "air"
    fig.update_annotations(
        yref="paper", 
        y=1,
        font_size=13,
        bgcolor="rgba(255,255,255,0.8)"
    )

    fig.update_layout(
        xaxis_title="Days from application", 
        yaxis_title="Count of Companies", 
        bargap=0.1,
        margin=dict(t=80),
        barcornerradius=15
    )
    return fig


def fig_weekday_effectiveness(df: pd.DataFrame) -> go.Figure:
    ct = pd.crosstab(df["response_status"], df["day_of_week"]).reindex(columns=DAYS_ORDER).fillna(0)
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

    status_emoji_map = {
        "Active Interest": "🙂 Active Interest",
        "Rejection": "😞 Rejection",
        "No Feedback": "😐 No Feedback",
    }
    display_y = [status_emoji_map.get(s, s) for s in ct_pct.index]

    weekday_counts = df["day_of_week"].value_counts().reindex(DAYS_ORDER).fillna(0)

    # Create a grid of 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.15,
        subplot_titles=("<b>RESPONSE EFFECTIVENESS BY DAY</b>", "<b>TOTAL APPLICATION VOLUME</b>")
    )

    # ADD HEATMAP 
    fig.add_trace(
        go.Heatmap(
            z=ct_pct.values,
            x=ct_pct.columns,
            y=display_y,
            colorscale='darkmint',
            texttemplate="<b>%{z:.1f}%</b>",
            showscale=False,
            xgap=5,
            ygap=5,
            hovertemplate=(
                "<b>Day Applied:</b> %{x}<br>" +
                "<b>Outcome:</b> %{y}<br>" +
                "<b>Share:</b> %{z:.1f}%<extra></extra>"
            )
        ), row=1, col=1
    )

    # ADD BAR CHART
    fig.add_trace(
        go.Bar(
            x=weekday_counts.index,
            y=weekday_counts.values,
            marker_color='#5FB1C1',
            text=weekday_counts.values,
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=14, family="Arial", weight='bold'),
            name="Total Apps",
            hovertemplate="<b>%{x}</b><br>Total Applications: <b>%{y}</b><extra></extra>"
        ), row=2, col=1
    )

    # Adjusting the spaces and headings
    # Raise the subheadings slightly (controlled by y in the annotations)
    for i in fig['layout']['annotations']:
        i['y'] += 0.02 

    fig.update_xaxes(tickfont=dict(size=13), row=2, col=1)
    fig.update_yaxes(title_text="Apps Count", row=2, col=1)

    fig.update_layout(
        height=600,
        showlegend=False,
        template="plotly_white",
        title_text="<b>HOW WEEKDAY IMPACTS YOUR SUCCESS</b>",
        title_x=0.0,
        title_y=0.98,
        margin=dict(t=100, b=50, l=150, r=50),
        barcornerradius=15
    )

    return fig


def fig_success_by_level(df: pd.DataFrame) -> go.Figure:
    level_stats = (
        df.groupby("level")
        .agg(
            total=("position", "count"),
            interviews=("status", lambda x: x.isin(["Interview", "Test task"]).sum()),
        )
        .reset_index()
    )
    level_stats["conversion"] = (level_stats["interviews"] / level_stats["total"] * 100).round(1)
    level_stats["label_text"] = (
        "<b>" + level_stats["level"] + "</b>" + "<br>Conv: " + level_stats["conversion"].astype(str) + "%"
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=level_stats["level"],
                values=level_stats["total"],
                hole=0.65,
                text=level_stats["label_text"],
                textinfo="text",
                textposition="outside",
                hovertemplate=(
                    "<b>%{label}</b><br>" +
                    "Apps: %{value}<br>" +
                    "Apps %: %{percent}<extra></extra>"
                ),
                marker=dict(colors=['#1D446D', '#B34138', '#5FB1C1'] ,
                line=dict(color='#FFFFFF', width=2)),
                pull=[0.05, 0] # Let's push the answer segment forward a bit for emphasis
            )
        ]
    )
    fig.update_layout(title_text="<b>APPLICATIONS BY ROLE LEVEL</b>", template="plotly_white", height=400)
    return fig


def fig_response_by_specialization(df: pd.DataFrame) -> go.Figure:
    spec = df.groupby("specialization")["has_response"].mean().reset_index()
    spec["response_rate_pct"] = spec["has_response"] * 100
    spec = spec.sort_values("response_rate_pct", ascending=False)

    fig = px.bar(
        spec,
        x="response_rate_pct",
        y="specialization",
        orientation="h",
        title="<b>RESPONSE RATE BY ROLE SPECIALIZATION</b>",
        labels={"response_rate_pct": "Response rate (%)", "specialization": ""},
        template="plotly_white",
    )
    return fig
