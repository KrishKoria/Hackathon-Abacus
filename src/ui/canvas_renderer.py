"""Canvas renderer component for ClaimsIQ Nexus.

Provides the right-side Canvas panel (60% width) that renders
different visualization modes based on agent output.
"""

import streamlit as st
from typing import Any, Optional

from src.models import CanvasMode, CanvasState


def initialize_canvas_state() -> None:
    """Initialize canvas-related session state variables."""
    if "canvas_state" not in st.session_state:
        st.session_state.canvas_state = CanvasState()


def update_canvas_state(
    mode: CanvasMode,
    data: Optional[Any] = None,
    title: Optional[str] = None,
    last_tool: Optional[str] = None,
) -> None:
    """Update the canvas state.

    Args:
        mode: The new canvas mode
        data: Mode-specific data payload
        title: Display title for the canvas
        last_tool: Name of the tool that triggered this update
    """
    st.session_state.canvas_state = CanvasState(
        mode=mode, data=data, title=title, last_tool=last_tool
    )


def render_canvas() -> None:
    """Render the Canvas based on current state."""
    state: CanvasState = st.session_state.get("canvas_state", CanvasState())

    # Render based on mode
    if state.mode == CanvasMode.EMPTY:
        _render_empty_splash()
    elif state.mode == CanvasMode.CLAIM:
        _render_claim_mode(state)
    elif state.mode == CanvasMode.DOC:
        _render_doc_mode(state)
    elif state.mode == CanvasMode.CHART:
        _render_chart_mode(state)
    elif state.mode == CanvasMode.GRAPH:
        _render_graph_mode(state)
    else:
        _render_empty_splash()


def _render_empty_splash() -> None:
    """Render the empty state splash screen."""
    st.markdown(
        """
        <div class="empty-splash">
            <div class="empty-splash-icon">🔍</div>
            <div class="empty-splash-title">Ready to Investigate</div>
            <div class="empty-splash-subtitle">
                Ask me about claims, detect fraud patterns, or analyze denial trends.
                Your evidence will appear here.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick start suggestions
    st.markdown("---")
    st.markdown("**Try asking:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("• *Why was Claim #1023 denied?*")
        st.markdown("• *Analyze Dr. X for fraud*")
    with col2:
        st.markdown("• *Show denial trends by specialty*")
        st.markdown("• *Show me claim #1023*")


def _render_claim_mode(state: CanvasState) -> None:
    """Render the claim detail view."""
    # Canvas header
    _render_canvas_header(
        title=state.title or "Claim Details", tool=state.last_tool
    )

    data = state.data
    if not data:
        st.warning("No claim data available")
        return

    # Import here to avoid circular imports
    from src.ui.components.claim_card import render_claim

    render_claim(data)


def _render_doc_mode(state: CanvasState) -> None:
    """Render the clinical note viewer."""
    _render_canvas_header(
        title=state.title or "Clinical Documentation", tool=state.last_tool
    )

    data = state.data
    if not data:
        st.warning("No document data available")
        return

    # Import here to avoid circular imports
    from src.ui.components.doc_viewer import render_doc

    render_doc(data)


def _render_chart_mode(state: CanvasState) -> None:
    """Render the analytics chart view."""
    _render_canvas_header(
        title=state.title or "Analytics", tool=state.last_tool
    )

    data = state.data
    if not data:
        st.warning("No chart data available")
        return

    # Import here to avoid circular imports
    from src.ui.components.chart_view import render_chart

    render_chart(data)


def _render_graph_mode(state: CanvasState) -> None:
    """Render the network graph view."""
    _render_canvas_header(
        title=state.title or "Network Analysis", tool=state.last_tool
    )

    data = state.data
    if not data:
        st.warning("No graph data available")
        return

    # Import here to avoid circular imports
    from src.ui.components.graph_view import render_graph

    render_graph(data)


def _render_canvas_header(title: str, tool: Optional[str] = None) -> None:
    """Render the canvas header with title and optional tool indicator.

    Args:
        title: The canvas title
        tool: Name of the tool that generated this view
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### {title}")

    with col2:
        if tool:
            st.markdown(
                f'<div style="text-align: right; color: #64748b; font-size: 0.75rem;">'
                f"via {tool}</div>",
                unsafe_allow_html=True,
            )

    st.divider()
