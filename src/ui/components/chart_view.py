"""Chart view component for analytics visualization.

Renders interactive charts using Plotly for trend analysis
and statistical visualizations.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Any


def render_chart(data: Any) -> None:
    """Render an analytics chart.

    Args:
        data: Chart data dictionary containing:
            - chart_config: Plotly chart configuration
            - data: Raw data points
            - insights: List of insights
            - metric: Metric being analyzed
            - group_by: Grouping dimension
    """
    if not data:
        st.warning("No chart data available")
        return

    # Handle both dict and object access patterns
    if isinstance(data, dict):
        chart_config = data.get("chart_config", {})
        raw_data = data.get("data", [])
        insights = data.get("insights", [])
        metric = data.get("metric", "analysis")
        group_by = data.get("group_by", "")
    else:
        chart_config = getattr(data, "chart_config", {})
        raw_data = getattr(data, "data", [])
        insights = getattr(data, "insights", [])
        metric = getattr(data, "metric", "analysis")
        group_by = getattr(data, "group_by", "")

    # Render the Plotly chart
    if chart_config:
        _render_plotly_chart(chart_config)
    elif raw_data:
        _render_data_table(raw_data, metric, group_by)

    # Render insights
    if insights:
        _render_insights(insights)

    # Data table toggle
    with st.expander(" View Raw Data"):
        if raw_data:
            st.dataframe(raw_data, width="stretch")
        else:
            st.info("No raw data available")


def _render_plotly_chart(config: dict) -> None:
    """Render a Plotly chart from configuration.

    Args:
        config: Chart configuration containing:
            - chart_type: 'bar', 'line', 'scatter', etc.
            - x: X-axis data
            - y: Y-axis data
            - benchmarks: Optional benchmark values
            - title: Chart title
            - x_title: X-axis title
            - y_title: Y-axis title
            - y_format: Y-axis format string
            - color: Bar/line color
            - benchmark_color: Benchmark line color
    """
    chart_type = config.get("chart_type", "bar")
    x = config.get("x", [])
    y = config.get("y", [])
    benchmarks = config.get("benchmarks", [])
    title = config.get("title", "")
    x_title = config.get("x_title", "")
    y_title = config.get("y_title", "")
    y_format = config.get("y_format", "")
    color = config.get("color", "#6366f1")
    benchmark_color = config.get("benchmark_color", "#ef4444")

    fig = go.Figure()

    # Add main data trace
    if chart_type == "bar":
        fig.add_trace(
            go.Bar(
                x=x,
                y=y,
                marker_color=color,
                name="Actual",
                text=[f"{v:.1%}" if isinstance(v, float) and v < 1 else str(v) for v in y],
                textposition="outside",
            )
        )
    elif chart_type == "line":
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color=color, width=3),
                marker=dict(size=10),
                name="Actual",
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(color=color, size=10),
                name="Actual",
            )
        )

    # Add benchmark line if provided
    if benchmarks and any(b is not None for b in benchmarks):
        # Filter out None values
        valid_benchmarks = [(x[i], b) for i, b in enumerate(benchmarks) if b is not None]
        if valid_benchmarks:
            bx, by = zip(*valid_benchmarks)
            fig.add_trace(
                go.Scatter(
                    x=list(bx),
                    y=list(by),
                    mode="lines+markers",
                    line=dict(color=benchmark_color, width=2, dash="dash"),
                    marker=dict(size=8, symbol="diamond"),
                    name="Benchmark",
                )
            )

    # Layout configuration
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color="#f8fafc"),
            x=0.5,
        ),
        xaxis=dict(
            title=dict(text=x_title, font=dict(color="#94a3b8")),
            tickfont=dict(color="#94a3b8"),
            gridcolor="#334155",
            tickangle=-45 if len(x) > 5 else 0,
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color="#94a3b8")),
            tickfont=dict(color="#94a3b8"),
            gridcolor="#334155",
            tickformat=y_format,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        font=dict(color="#f8fafc"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94a3b8"),
        ),
        margin=dict(l=60, r=40, t=60, b=80),
        hovermode="x unified",
    )

    st.plotly_chart(fig, width="stretch")


def _render_data_table(data: list, metric: str, group_by: str) -> None:
    """Render data as a formatted table when no chart config is available.

    Args:
        data: List of data dictionaries
        metric: Metric being analyzed
        group_by: Grouping dimension
    """
    if not data:
        st.info("No data to display")
        return

    st.dataframe(data, width="stretch")


def _render_insights(insights: list) -> None:
    """Render insights as styled cards.

    Args:
        insights: List of insight dictionaries or strings containing:
            - type: Insight type (ABOVE_BENCHMARK, BELOW_BENCHMARK, etc.)
            - severity: HIGH, MEDIUM, LOW, POSITIVE
            - description: Insight text
            - entity: Related entity
            OR just a string with the insight text
    """
    st.markdown("#### 💡 Key Insights")

    for insight in insights:
        # Handle string insights (simple format)
        if isinstance(insight, str):
            description = insight
            severity = "MEDIUM"
            entity = ""
            # Auto-detect severity from text
            lower_text = insight.lower()
            if "highest" in lower_text or "exceed" in lower_text or "above" in lower_text:
                severity = "HIGH"
            elif "better" in lower_text or "lowest" in lower_text or "below" in lower_text:
                severity = "POSITIVE"
        elif isinstance(insight, dict):
            severity = insight.get("severity", "MEDIUM")
            description = insight.get("description", "")
            entity = insight.get("entity", "")
        else:
            severity = getattr(insight, "severity", "MEDIUM")
            description = getattr(insight, "description", "")
            entity = getattr(insight, "entity", "")

        # Skip empty insights
        if not description:
            continue

        # Severity-based styling
        if severity == "HIGH":
            icon = "🔴"
            bg = "#7f1d1d20"
            border = "#ef4444"
        elif severity == "MEDIUM":
            icon = "🟡"
            bg = "#78350f20"
            border = "#eab308"
        elif severity == "POSITIVE":
            icon = "✅"
            bg = "#14532d20"
            border = "#22c55e"
        else:
            icon = "🔵"
            bg = "#1e3a8a20"
            border = "#3b82f6"

        # Build entity div separately to avoid nested f-string issues
        entity_html = ""
        if entity:
            entity_html = f'<div style="color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">{entity}</div>'

        # Build HTML as single line to avoid whitespace issues
        html = f'<div style="background: {bg}; border-left: 4px solid {border}; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;"><div style="display: flex; align-items: flex-start; gap: 0.5rem;"><span>{icon}</span><div><div style="color: #f8fafc; font-weight: 500;">{description}</div>{entity_html}</div></div></div>'
        st.markdown(html, unsafe_allow_html=True)
