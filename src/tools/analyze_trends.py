"""Analyze Trends tool for ClaimsIQ Nexus.

MCP-style tool for statistical analysis and visualization of claims data.
"""

from typing import Optional

from langchain_core.tools import tool

from src.services.claims_service import (
    load_claims,
    get_denial_trends_by_specialty,
    filter_claims,
)


@tool
def analyze_trends(
    metric: str,
    group_by: str,
    filters: Optional[dict] = None,
) -> dict:
    """Generate statistical analysis and visualizations for claims data.

    Aggregates claims data to compute metrics like denial rates,
    claim amounts, and volumes, grouped by various dimensions.
    Returns data suitable for chart visualization.

    Args:
        metric: Metric to analyze. Options:
            - "denial_rate": Percentage of claims denied
            - "acceptance_rate": Percentage of claims approved/accepted
            - "approval_rate": Same as acceptance_rate
            - "claim_amount": Total or average claim amounts
            - "volume": Count of claims
        group_by: Dimension to group by. Options:
            - "specialty": Provider specialty
            - "provider": Individual providers (doctors)
            - "doctor": Same as provider
            - "month": Time-based grouping
            - "denial_reason": Reason for denial
        filters: Optional filters (same as query_claims_db):
            - status, specialty, date_from, date_to, etc.

    Returns:
        Dictionary with:
            - data: List of data points, each with:
                - category: Group label (e.g., specialty name)
                - value: Metric value
                - benchmark: Expected/comparison value (if available)
            - chart_config: Plotly-compatible chart specification
            - insights: Auto-generated observations
            - ui_hint: Always "MODE_CHART" for visualizations

    Examples:
        Denial rates by specialty:
            analyze_trends(metric="denial_rate", group_by="specialty")

        Acceptance rates by provider:
            analyze_trends(metric="acceptance_rate", group_by="provider")

        Claim amounts by month:
            analyze_trends(metric="claim_amount", group_by="month")
    """
    # Normalize metric names (acceptance_rate and approval_rate are aliases)
    metric_normalized = metric.lower().strip()
    if metric_normalized in ["acceptance_rate", "approval_rate"]:
        metric_normalized = "acceptance_rate"
    elif metric_normalized == "denial_rate":
        metric_normalized = "denial_rate"
    elif metric_normalized in ["claim_amount", "amount"]:
        metric_normalized = "claim_amount"
    elif metric_normalized in ["volume", "count"]:
        metric_normalized = "volume"
    else:
        metric_normalized = metric
    
    # Normalize group_by names (doctor is alias for provider)
    group_by_normalized = group_by.lower().strip()
    if group_by_normalized in ["doctor", "doctors", "providers"]:
        group_by_normalized = "provider"
    elif group_by_normalized in ["specialties"]:
        group_by_normalized = "specialty"
    elif group_by_normalized in ["months", "time"]:
        group_by_normalized = "month"
    elif group_by_normalized in ["denial_reasons", "reasons"]:
        group_by_normalized = "denial_reason"
    else:
        group_by_normalized = group_by
    
    # Validate inputs
    valid_metrics = {"denial_rate", "acceptance_rate", "claim_amount", "volume"}
    valid_groups = {"specialty", "provider", "month", "denial_reason"}

    if metric_normalized not in valid_metrics:
        return {
            "data": [],
            "chart_config": {},
            "insights": [],
            "ui_hint": "MODE_EMPTY",
            "error": f"Invalid metric '{metric}'. Choose from: denial_rate, acceptance_rate, claim_amount, volume",
        }

    if group_by_normalized not in valid_groups:
        return {
            "data": [],
            "chart_config": {},
            "insights": [],
            "ui_hint": "MODE_EMPTY",
            "error": f"Invalid group_by '{group_by}'. Choose from: specialty, provider, month, denial_reason",
        }

    # Load claims data
    df = load_claims()

    # Apply filters if provided
    if filters:
        if filters.get("status"):
            df = df[df["claim_status"] == filters["status"]]
        if filters.get("specialty"):
            df = df[df["provider_specialty"] == filters["specialty"]]
        if filters.get("date_from"):
            df = df[df["claim_date"] >= filters["date_from"]]
        if filters.get("date_to"):
            df = df[df["claim_date"] <= filters["date_to"]]

    # Generate analysis based on metric and group_by (use normalized values)
    if group_by_normalized == "specialty":
        data, insights = _analyze_by_specialty(df, metric_normalized)
    elif group_by_normalized == "provider":
        data, insights = _analyze_by_provider(df, metric_normalized)
    elif group_by_normalized == "month":
        data, insights = _analyze_by_month(df, metric_normalized)
    elif group_by_normalized == "denial_reason":
        data, insights = _analyze_by_denial_reason(df, metric_normalized)
    else:
        data, insights = [], []

    # Generate chart config (use normalized values for proper labels)
    chart_config = _generate_chart_config(data, metric_normalized, group_by_normalized)

    return {
        "data": data,
        "chart_config": chart_config,
        "insights": insights,
        "ui_hint": "MODE_CHART",
        "metric": metric_normalized,
        "group_by": group_by_normalized,
    }


def _analyze_by_specialty(df, metric: str) -> tuple[list[dict], list[str]]:
    """Analyze claims grouped by provider specialty."""
    # Industry benchmarks for rates
    denial_benchmarks = {
        "Cardiology": 0.25,
        "Oncology": 0.25,
        "Orthopedics": 0.25,
        "Neurology": 0.25,
        "Emergency Medicine": 0.25,
        "Primary Care": 0.25,
        "Dermatology": 0.25,
        "Gastroenterology": 0.25,
    }
    
    # Acceptance benchmarks (inverse of denial)
    acceptance_benchmarks = {k: 1 - v for k, v in denial_benchmarks.items()}

    grouped = df.groupby("provider_specialty").agg(
        total=("claim_id", "count"),
        denied=("claim_status", lambda x: (x == "Denied").sum()),
        approved=("claim_status", lambda x: (x == "Approved").sum()),
        total_amount=("claim_amount", "sum"),
        avg_amount=("claim_amount", "mean"),
    ).reset_index()

    data = []
    insights = []

    for _, row in grouped.iterrows():
        specialty = row["provider_specialty"]

        if metric == "denial_rate":
            value = row["denied"] / row["total"] if row["total"] > 0 else 0
            benchmark = denial_benchmarks.get(specialty, 0.25)
        elif metric == "acceptance_rate":
            value = row["approved"] / row["total"] if row["total"] > 0 else 0
            benchmark = acceptance_benchmarks.get(specialty, 0.75)
        elif metric == "claim_amount":
            value = float(row["total_amount"])
            benchmark = None
        else:  # volume
            value = int(row["total"])
            benchmark = None

        data.append({
            "category": specialty,
            "value": round(value, 4) if isinstance(value, float) else value,
            "benchmark": benchmark,
            "count": int(row["total"]),
        })

    # Sort by value descending
    data = sorted(data, key=lambda x: x["value"], reverse=True)

    # Generate insights
    if metric == "denial_rate" and data:
        highest = data[0]
        lowest = data[-1]
        insights.append(
            f"{highest['category']} has the highest denial rate at {highest['value']*100:.1f}%"
        )
        insights.append(
            f"{lowest['category']} has the lowest denial rate at {lowest['value']*100:.1f}%"
        )

        # Check for above-benchmark specialties
        above_benchmark = [d for d in data if d.get("benchmark") and d["value"] > d["benchmark"]]
        if above_benchmark:
            insights.append(
                f"{len(above_benchmark)} specialties exceed the 25% industry benchmark"
            )
    elif metric == "acceptance_rate" and data:
        highest = data[0]
        lowest = data[-1]
        insights.append(
            f"{highest['category']} has the highest acceptance rate at {highest['value']*100:.1f}%"
        )
        insights.append(
            f"{lowest['category']} has the lowest acceptance rate at {lowest['value']*100:.1f}%"
        )

        # Check for below-benchmark specialties
        below_benchmark = [d for d in data if d.get("benchmark") and d["value"] < d["benchmark"]]
        if below_benchmark:
            insights.append(
                f"{len(below_benchmark)} specialties fall below the 75% industry benchmark"
            )

    return data, insights


def _analyze_by_provider(df, metric: str) -> tuple[list[dict], list[str]]:
    """Analyze claims grouped by provider."""
    grouped = df.groupby(["provider_id", "provider_name"]).agg(
        total=("claim_id", "count"),
        denied=("claim_status", lambda x: (x == "Denied").sum()),
        approved=("claim_status", lambda x: (x == "Approved").sum()),
        total_amount=("claim_amount", "sum"),
        avg_amount=("claim_amount", "mean"),
    ).reset_index()

    # Limit to top 20 by total claims
    grouped = grouped.nlargest(20, "total")

    data = []
    for _, row in grouped.iterrows():
        if metric == "denial_rate":
            value = row["denied"] / row["total"] if row["total"] > 0 else 0
        elif metric == "acceptance_rate":
            value = row["approved"] / row["total"] if row["total"] > 0 else 0
        elif metric == "claim_amount":
            value = float(row["total_amount"])
        else:  # volume
            value = int(row["total"])

        data.append({
            "category": f"{row['provider_name']} ({row['provider_id']})",
            "value": round(value, 4) if isinstance(value, float) else value,
            "benchmark": None,
            "count": int(row["total"]),
        })

    data = sorted(data, key=lambda x: x["value"], reverse=True)

    insights = []
    if data:
        insights.append(f"Analysis covers top {len(data)} providers by claim volume")
        if metric == "acceptance_rate":
            highest = data[0]
            lowest = data[-1]
            insights.append(f"{highest['category'].split('(')[0].strip()} has the highest acceptance rate at {highest['value']*100:.1f}%")
            insights.append(f"{lowest['category'].split('(')[0].strip()} has the lowest acceptance rate at {lowest['value']*100:.1f}%")
        elif metric == "denial_rate":
            highest = data[0]
            lowest = data[-1]
            insights.append(f"{highest['category'].split('(')[0].strip()} has the highest denial rate at {highest['value']*100:.1f}%")
            insights.append(f"{lowest['category'].split('(')[0].strip()} has the lowest denial rate at {lowest['value']*100:.1f}%")

    return data, insights


def _analyze_by_month(df, metric: str) -> tuple[list[dict], list[str]]:
    """Analyze claims grouped by month."""
    df = df.copy()
    df["month"] = df["claim_date"].dt.to_period("M")

    grouped = df.groupby("month").agg(
        total=("claim_id", "count"),
        denied=("claim_status", lambda x: (x == "Denied").sum()),
        approved=("claim_status", lambda x: (x == "Approved").sum()),
        total_amount=("claim_amount", "sum"),
        avg_amount=("claim_amount", "mean"),
    ).reset_index()

    data = []
    for _, row in grouped.iterrows():
        if metric == "denial_rate":
            value = row["denied"] / row["total"] if row["total"] > 0 else 0
        elif metric == "acceptance_rate":
            value = row["approved"] / row["total"] if row["total"] > 0 else 0
        elif metric == "claim_amount":
            value = float(row["total_amount"])
        else:  # volume
            value = int(row["total"])

        data.append({
            "category": str(row["month"]),
            "value": round(value, 4) if isinstance(value, float) else value,
            "benchmark": None,
            "count": int(row["total"]),
        })

    insights = []
    if len(data) > 1:
        first_val = data[0]["value"]
        last_val = data[-1]["value"]
        if first_val > 0:
            change = ((last_val - first_val) / first_val) * 100
            direction = "increased" if change > 0 else "decreased"
            insights.append(f"Trend has {direction} by {abs(change):.1f}% over the period")

    return data, insights


def _analyze_by_denial_reason(df, metric: str) -> tuple[list[dict], list[str]]:
    """Analyze claims grouped by denial reason."""
    # Filter to only denied claims
    denied_df = df[df["claim_status"] == "Denied"]

    if len(denied_df) == 0:
        return [], ["No denied claims found"]

    grouped = denied_df.groupby("denial_reason").agg(
        total=("claim_id", "count"),
        total_amount=("claim_amount", "sum"),
        avg_amount=("claim_amount", "mean"),
    ).reset_index()

    total_denied = len(denied_df)

    data = []
    for _, row in grouped.iterrows():
        reason = row["denial_reason"]
        if reason is None:
            reason = "Unknown"

        if metric == "denial_rate":
            # For denial reasons, show percentage of total denials
            value = row["total"] / total_denied if total_denied > 0 else 0
        elif metric == "claim_amount":
            value = float(row["total_amount"])
        else:
            value = int(row["total"])

        data.append({
            "category": reason,
            "value": round(value, 4) if isinstance(value, float) else value,
            "benchmark": None,
            "count": int(row["total"]),
        })

    data = sorted(data, key=lambda x: x["value"], reverse=True)

    insights = []
    if data:
        top_reason = data[0]
        insights.append(
            f"'{top_reason['category']}' is the most common denial reason ({top_reason['count']} claims)"
        )

    return data, insights


def _generate_chart_config(data: list[dict], metric: str, group_by: str) -> dict:
    """Generate Plotly-compatible chart configuration."""
    categories = [d["category"] for d in data]
    values = [d["value"] for d in data]
    benchmarks = [d.get("benchmark") for d in data]

    # Determine chart type and formatting
    if group_by == "month":
        chart_type = "line"
    else:
        chart_type = "bar"

    # Y-axis formatting based on metric
    if metric == "denial_rate":
        y_format = ".0%"
        y_title = "Denial Rate"
        color = "#ef4444"  # Red for denial
    elif metric == "acceptance_rate":
        y_format = ".0%"
        y_title = "Acceptance Rate"
        color = "#22c55e"  # Green for acceptance
    elif metric == "claim_amount":
        y_format = "$,.0f"
        y_title = "Total Claim Amount ($)"
        color = "#6366f1"  # Indigo
    else:  # volume
        y_format = ",.0f"
        y_title = "Claim Count"
        color = "#6366f1"  # Indigo

    config = {
        "chart_type": chart_type,
        "x": categories,
        "y": values,
        "benchmarks": benchmarks if any(b for b in benchmarks) else None,
        "x_title": group_by.replace("_", " ").title(),
        "y_title": y_title,
        "y_format": y_format,
        "title": f"{metric.replace('_', ' ').title()} by {group_by.replace('_', ' ').title()}",
        "color": color,
        "benchmark_color": "#f59e0b",  # Amber for benchmark line
    }

    return config
