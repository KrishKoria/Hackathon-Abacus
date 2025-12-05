"""Canvas state model for ClaimsIQ Nexus.

Contains the CanvasState model for UI state management.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CanvasMode(str, Enum):
    """Canvas display modes for the right-side panel."""

    EMPTY = "MODE_EMPTY"  # Default splash screen
    CLAIM = "MODE_CLAIM"  # Claim detail card
    DOC = "MODE_DOC"  # Clinical note viewer
    CHART = "MODE_CHART"  # Plotly analytics chart
    GRAPH = "MODE_GRAPH"  # Network visualization


class CanvasState(BaseModel):
    """Current Canvas rendering state.

    Tracks the current display mode and associated data
    for the Canvas panel in the split-screen UI.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "mode": "MODE_CLAIM",
                    "data": {"claim_id": "CLM-01023"},
                    "last_tool": "query_claims_db",
                    "title": "Claim Investigation: CLM-01023",
                },
                {
                    "mode": "MODE_GRAPH",
                    "data": {"nodes": [], "edges": []},
                    "last_tool": "analyze_network_graph",
                    "title": "Fraud Analysis: Dr. X",
                },
            ]
        }
    )

    mode: CanvasMode = CanvasMode.EMPTY
    data: Optional[Any] = None  # Mode-specific payload
    last_tool: Optional[str] = None  # Tool that triggered this state
    title: Optional[str] = None  # Display title for the Canvas
