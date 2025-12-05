"""Network graph view component for fraud detection.

Renders interactive network graphs using Plotly for visualizing
provider-patient relationships and fraud patterns.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Any
import math


def render_graph(data: Any) -> None:
    """Render a network graph for fraud analysis.

    Args:
        data: Graph data dictionary containing:
            - nodes: List of node dictionaries
            - edges: List of edge dictionaries
            - findings: List of fraud findings
            - center_entity: Central entity being analyzed
            - analyzed_entity: Entity that was analyzed
    """
    if not data:
        st.warning("No graph data available")
        return

    # Handle both dict and object access patterns
    if isinstance(data, dict):
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        findings = data.get("findings", [])
        center_entity = data.get("center_entity") or data.get("analyzed_entity", "")
    else:
        nodes = getattr(data, "nodes", [])
        edges = getattr(data, "edges", [])
        findings = getattr(data, "findings", [])
        center_entity = getattr(data, "center_entity", "") or getattr(data, "analyzed_entity", "")

    # Render the network graph
    if nodes and edges:
        _render_network_graph(nodes, edges, center_entity)
    else:
        st.info("No network data to visualize")

    # Render findings
    if findings:
        _render_findings(findings)


def _render_network_graph(nodes: list, edges: list, center_entity: str) -> None:
    """Render an interactive network graph using Plotly.

    Args:
        nodes: List of node dictionaries with id, type, label, flagged, risk_score
        edges: List of edge dictionaries with from, to, type, weight
        center_entity: ID of the central entity
    """
    # Create node positions using circular layout
    node_positions = _calculate_positions(nodes, center_entity)

    # Create figure
    fig = go.Figure()

    # Draw edges first (so they appear behind nodes)
    edge_x = []
    edge_y = []
    edge_colors = []

    for edge in edges:
        if isinstance(edge, dict):
            # Support both from/to and source/target formats
            from_id = edge.get("from") or edge.get("source", "")
            to_id = edge.get("to") or edge.get("target", "")
            edge_type = edge.get("type") or edge.get("relationship_type", "")
        else:
            from_id = getattr(edge, "from", "") or getattr(edge, "source", "")
            to_id = getattr(edge, "to", "") or getattr(edge, "target", "")
            edge_type = getattr(edge, "type", "") or getattr(edge, "relationship_type", "")

        if from_id in node_positions and to_id in node_positions:
            x0, y0 = node_positions[from_id]
            x1, y1 = node_positions[to_id]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            # Color based on edge type
            if edge_type == "referral":
                edge_colors.append("#f59e0b")  # Amber for referrals
            else:
                edge_colors.append("#64748b")  # Slate for treatment

    # Add edges trace
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=2, color="#475569"),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Separate nodes by type for different styling
    provider_nodes = []
    patient_nodes = []
    flagged_nodes = []

    for node in nodes:
        if isinstance(node, dict):
            node_id = node.get("id", "")
            node_type = node.get("type", "")
            label = node.get("label", node_id)
            # Support both flagged and is_fraud_ring_member
            flagged = node.get("flagged", False) or node.get("is_fraud_ring_member", False)
            risk_score = node.get("risk_score", 0)
        else:
            node_id = getattr(node, "id", "")
            node_type = getattr(node, "type", "")
            label = getattr(node, "label", node_id)
            flagged = getattr(node, "flagged", False) or getattr(node, "is_fraud_ring_member", False)
            risk_score = getattr(node, "risk_score", 0)

        if node_id in node_positions:
            x, y = node_positions[node_id]
            node_data = {
                "x": x,
                "y": y,
                "id": node_id,
                "label": label,
                "risk_score": risk_score,
            }

            if flagged:
                flagged_nodes.append(node_data)
            elif node_type == "provider":
                provider_nodes.append(node_data)
            else:
                patient_nodes.append(node_data)

    # Add patient nodes (blue)
    if patient_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in patient_nodes],
                y=[n["y"] for n in patient_nodes],
                mode="markers+text",
                marker=dict(
                    size=30,
                    color="#3b82f6",
                    line=dict(width=2, color="#1e40af"),
                ),
                text=[n["label"] for n in patient_nodes],
                textposition="bottom center",
                textfont=dict(size=10, color="#94a3b8"),
                hovertemplate="<b>%{text}</b><br>Type: Patient<extra></extra>",
                name="Patients",
            )
        )

    # Add provider nodes (green)
    if provider_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in provider_nodes],
                y=[n["y"] for n in provider_nodes],
                mode="markers+text",
                marker=dict(
                    size=40,
                    color="#22c55e",
                    line=dict(width=2, color="#166534"),
                ),
                text=[n["label"] for n in provider_nodes],
                textposition="bottom center",
                textfont=dict(size=10, color="#94a3b8"),
                hovertemplate="<b>%{text}</b><br>Type: Provider<extra></extra>",
                name="Providers",
            )
        )

    # Add flagged nodes (red) - on top
    if flagged_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in flagged_nodes],
                y=[n["y"] for n in flagged_nodes],
                mode="markers+text",
                marker=dict(
                    size=50,
                    color="#ef4444",
                    line=dict(width=3, color="#991b1b"),
                    symbol="hexagon",
                ),
                text=[n["label"] for n in flagged_nodes],
                textposition="bottom center",
                textfont=dict(size=11, color="#fca5a5", weight=700),
                hovertemplate="<b>%{text}</b><br>⚠️ FLAGGED<br>Risk: %{customdata:.0%}<extra></extra>",
                customdata=[n["risk_score"] for n in flagged_nodes],
                name="Flagged",
            )
        )

    # Layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#94a3b8"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="closest",
    )

    st.plotly_chart(fig, width="stretch", key="network_graph")

    # Legend explanation
    st.markdown(
        """
        <div style="
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 0.5rem;
            color: #64748b;
            font-size: 0.75rem;
        ">
            <span>🔴 Flagged Provider</span>
            <span>🟢 Provider</span>
            <span>🔵 Patient</span>
            <span>— Relationship</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _calculate_positions(nodes: list, center_entity: str) -> dict:
    """Calculate node positions using a circular layout.

    Places flagged/center nodes in the inner circle, others in outer circle.

    Args:
        nodes: List of node dictionaries
        center_entity: ID of the central entity

    Returns:
        Dictionary mapping node IDs to (x, y) positions
    """
    positions = {}

    # Separate into center and outer nodes
    center_nodes = []
    outer_nodes = []

    for node in nodes:
        if isinstance(node, dict):
            node_id = node.get("id", "")
            flagged = node.get("flagged", False) or node.get("is_fraud_ring_member", False)
        else:
            node_id = getattr(node, "id", "")
            flagged = getattr(node, "flagged", False) or getattr(node, "is_fraud_ring_member", False)

        if flagged or node_id == center_entity:
            center_nodes.append(node_id)
        else:
            outer_nodes.append(node_id)

    # Position center nodes in inner circle
    inner_radius = 1.0
    for i, node_id in enumerate(center_nodes):
        angle = (2 * math.pi * i) / max(len(center_nodes), 1)
        x = inner_radius * math.cos(angle)
        y = inner_radius * math.sin(angle)
        positions[node_id] = (x, y)

    # Position outer nodes in outer circle
    outer_radius = 2.5
    for i, node_id in enumerate(outer_nodes):
        angle = (2 * math.pi * i) / max(len(outer_nodes), 1)
        x = outer_radius * math.cos(angle)
        y = outer_radius * math.sin(angle)
        positions[node_id] = (x, y)

    return positions


def _render_findings(findings: list) -> None:
    """Render fraud findings as styled cards.

    Args:
        findings: List of finding dictionaries containing:
            - type: Finding type (CIRCULAR_REFERRAL, BILLING_ANOMALY, etc.)
            - severity: HIGH, MEDIUM, LOW
            - description: Finding text
            - entities: Related entity IDs
    """
    st.markdown("#### 🚨 Fraud Findings")

    for finding in findings:
        if isinstance(finding, dict):
            # Support both type and finding_type formats
            finding_type = finding.get("type") or finding.get("finding_type", "")
            severity = finding.get("severity", "MEDIUM")
            description = finding.get("description", "")
            entities = finding.get("entities", [])
        else:
            finding_type = getattr(finding, "type", "") or getattr(finding, "finding_type", "")
            severity = getattr(finding, "severity", "MEDIUM")
            description = getattr(finding, "description", "")
            entities = getattr(finding, "entities", [])

        # Severity-based styling
        if severity == "HIGH":
            icon = "🔴"
            bg = "#7f1d1d20"
            border = "#ef4444"
        elif severity == "MEDIUM":
            icon = "🟡"
            bg = "#78350f20"
            border = "#eab308"
        else:
            icon = "🔵"
            bg = "#1e3a8a20"
            border = "#3b82f6"

        # Type-based icons (support both uppercase and lowercase)
        type_icons = {
            "CIRCULAR_REFERRAL": "🔄",
            "circular_referral": "🔄",
            "BILLING_ANOMALY": "💰",
            "billing_anomaly": "💰",
            "billing_pattern": "💰",
            "PATIENT_CONCENTRATION": "👥",
            "patient_concentration": "👥",
            "UNUSUAL_VOLUME": "📈",
            "volume_anomaly": "📈",
        }
        type_icon = type_icons.get(finding_type, "⚠️")

        # Build entities div separately to avoid nested f-string issues
        entities_html = ""
        if entities:
            entities_str = ", ".join(entities) if isinstance(entities, list) else str(entities)
            entities_html = f'<div style="color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">Entities: {entities_str}</div>'

        # Format finding type for display
        type_display = finding_type.replace('_', ' ').title() if finding_type else "Finding"
        
        # Build HTML as single line to avoid whitespace issues
        html = f'<div style="background: {bg}; border-left: 4px solid {border}; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;"><div style="display: flex; align-items: flex-start; gap: 0.5rem;"><span>{type_icon}</span><div style="flex: 1;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;"><span style="color: #f8fafc; font-weight: 600;">{type_display}</span><span style="font-size: 0.625rem; padding: 0.125rem 0.375rem; border-radius: 9999px; background: {border}40; color: {border};">{severity}</span></div><div style="color: #cbd5e1; font-size: 0.875rem;">{description}</div>{entities_html}</div></div></div>'
        st.markdown(html, unsafe_allow_html=True)

    # Risk summary
    high_count = sum(
        1 for f in findings
        if (f.get("severity") if isinstance(f, dict) else getattr(f, "severity", "")) == "HIGH"
    )
    medium_count = sum(
        1 for f in findings
        if (f.get("severity") if isinstance(f, dict) else getattr(f, "severity", "")) == "MEDIUM"
    )

    if high_count > 0 or medium_count > 0:
        risk_html = f'<div style="background: #1e293b; border-radius: 8px; padding: 0.75rem 1rem; margin-top: 1rem; text-align: center;"><span style="color: #64748b; font-size: 0.875rem;">Risk Summary:</span><span style="color: #ef4444; font-weight: 600; margin-left: 0.5rem;">{high_count} High</span><span style="color: #eab308; font-weight: 600; margin-left: 0.5rem;">{medium_count} Medium</span></div>'
        st.markdown(risk_html, unsafe_allow_html=True)
