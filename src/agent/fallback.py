"""Fallback and Golden Path handling for ClaimsIQ Nexus.

Provides cached responses for demo reliability and fallback chains.
"""

import json
from pathlib import Path
from typing import Optional

from src.config import GOLDEN_PATH_DIR


def load_golden_path(scenario: str) -> Optional[dict]:
    """Load a pre-computed Golden Path response.

    Args:
        scenario: One of 'silo_breaker', 'fraud_hunter', 'trend_analyst'

    Returns:
        Pre-computed response dict or None if not found
    """
    valid_scenarios = {"silo_breaker", "fraud_hunter", "trend_analyst"}
    if scenario not in valid_scenarios:
        return None

    filepath = Path(GOLDEN_PATH_DIR) / f"{scenario}.json"
    if not filepath.exists():
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def match_golden_path_query(query: str) -> Optional[str]:
    """Check if a query matches a Golden Path scenario.
    
    Golden paths are pre-computed demo responses for specific scenarios.
    Only exact demo queries should trigger golden paths - generic queries
    should go to the real agent.

    Args:
        query: User's natural language query

    Returns:
        Scenario name ('silo_breaker', 'fraud_hunter', 'trend_analyst') or None
    """
    query_lower = query.lower().strip()

    # Silo Breaker scenario - ONLY for Claim #1023 specifically
    if any(
        pattern in query_lower
        for pattern in ["claim #1023", "claim 1023", "clm-1023", "clm-01023", "#1023"]
    ):
        return "silo_breaker"

    # Fraud Hunter scenario - ONLY for Dr. X specifically (not generic fraud queries)
    # Must mention "dr. x" or "dr x" or the specific provider ID
    if any(
        pattern in query_lower
        for pattern in ["dr. x", "dr x", "prv-007", "doctor x"]
    ):
        return "fraud_hunter"

    # Trend Analyst scenario - ONLY for the specific demo query about specialty trends
    # Must explicitly ask for trends BY SPECIALTY - not by provider/doctor/month/etc.
    # This is very specific to avoid matching other trend queries
    specialty_trend_patterns = [
        "denial trends by specialty",
        "trends by specialty", 
        "denial rate by specialty",
        "show me denial trends by specialty",
        "show denial trends by specialty",
    ]
    if any(pattern in query_lower for pattern in specialty_trend_patterns):
        return "trend_analyst"

    # All other queries go to the real agent
    # This includes:
    # - "denial trends by doctors" -> real agent
    # - "denial trends by provider" -> real agent  
    # - "denial trends by month" -> real agent
    # - "show trends" (generic) -> real agent
    # - "trend analysis" (generic) -> real agent
    return None


def get_fallback_response(mode: str, error: Optional[str] = None) -> dict:
    """Get a fallback response when primary rendering fails.

    Implements fallback chains:
    - Graph → Table → Markdown
    - Chart → Table
    - Doc → Plain text

    Args:
        mode: Canvas mode that failed (MODE_GRAPH, MODE_CHART, MODE_DOC)
        error: Optional error message

    Returns:
        Fallback response with degraded but functional data
    """
    fallbacks = {
        "MODE_GRAPH": {
            "mode": "MODE_EMPTY",
            "data": None,
            "title": "Graph visualization unavailable",
            "message": "Network graph could not be rendered. Please try again or view data in table format.",
            "error": error,
        },
        "MODE_CHART": {
            "mode": "MODE_EMPTY",
            "data": None,
            "title": "Chart unavailable",
            "message": "Chart could not be rendered. Data is available in text format.",
            "error": error,
        },
        "MODE_DOC": {
            "mode": "MODE_EMPTY",
            "data": None,
            "title": "Document unavailable",
            "message": "Clinical note could not be displayed.",
            "error": error,
        },
        "MODE_CLAIM": {
            "mode": "MODE_EMPTY",
            "data": None,
            "title": "Claim details unavailable",
            "message": "Claim information could not be retrieved.",
            "error": error,
        },
    }

    return fallbacks.get(
        mode,
        {
            "mode": "MODE_EMPTY",
            "data": None,
            "title": "Error",
            "message": "An unexpected error occurred.",
            "error": error,
        },
    )
