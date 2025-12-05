"""Analyze Network Graph tool for ClaimsIQ Nexus.

MCP-style tool for fraud detection through provider-patient relationship analysis.
"""

from typing import Optional

from langchain_core.tools import tool

from src.services.graph_service import get_provider_network, load_fraud_graph


@tool
def analyze_network_graph(
    entity_id: str,
    depth: int = 2,
) -> dict:
    """Analyze provider-patient relationships for fraud detection.

    Analyzes relationships between providers and patients to detect
    collusion patterns such as circular referrals, unusual billing
    patterns, and shared patient networks.

    For demo purposes, uses pre-baked fraud ring graph data centered
    around PRV-007 (Dr. X) and PRV-012 (Dr. Y).

    Args:
        entity_id: Provider or patient ID to analyze.
                   Examples: "PRV-007", "Dr. X", "P-0101"
        depth: Relationship traversal depth (1-3, default 2).
               Higher depth shows more connections but may be slower.

    Returns:
        Dictionary with:
            - nodes: List of entities in the network, each with:
                - id: Entity identifier
                - type: "provider" or "patient"
                - label: Display name
                - risk_score: Fraud risk score (0-1)
                - specialty: Provider specialty (if applicable)
            - edges: List of relationships, each with:
                - source: Source entity ID
                - target: Target entity ID
                - relationship_type: Type of connection
                - weight: Strength of relationship
            - findings: List of fraud indicators, each with:
                - finding_type: Category of finding
                - description: Detailed explanation
                - severity: LOW, MEDIUM, or HIGH
            - ui_hint: Always "MODE_GRAPH" for network visualization

    Examples:
        Analyze a specific provider:
            analyze_network_graph(entity_id="PRV-007")

        Deep analysis of provider network:
            analyze_network_graph(entity_id="Dr. X", depth=3)
    """
    # Validate depth
    depth = max(1, min(3, depth))

    # Handle common aliases for demo
    entity_id_normalized = entity_id
    if entity_id.lower() in ["dr. x", "dr x", "doctor x"]:
        entity_id_normalized = "PRV-007"
    elif entity_id.lower() in ["dr. y", "dr y", "doctor y"]:
        entity_id_normalized = "PRV-012"

    # Get network data
    result = get_provider_network(
        entity_id=entity_id_normalized,
        depth=depth,
    )

    if result.get("error"):
        return {
            "nodes": [],
            "edges": [],
            "findings": [],
            "ui_hint": "MODE_EMPTY",
            "error": result["error"],
        }

    result["ui_hint"] = "MODE_GRAPH"
    result["analyzed_entity"] = entity_id
    result["depth"] = depth

    return result
