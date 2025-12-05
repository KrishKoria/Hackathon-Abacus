"""UI Components for ClaimsIQ Nexus Canvas.

This package contains the rendering components for different
canvas modes in the Evidence Canvas.
"""

from src.ui.components.claim_card import render_claim
from src.ui.components.doc_viewer import render_doc
from src.ui.components.chart_view import render_chart
from src.ui.components.graph_view import render_graph

__all__ = [
    "render_claim",
    "render_doc",
    "render_chart",
    "render_graph",
]
