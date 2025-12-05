"""Graph service for ClaimsIQ Nexus.

Provides NetworkX-based fraud graph analysis using
pre-baked fraud ring data.
"""

import json
from pathlib import Path
from typing import Optional

import networkx as nx

from src.config import GOLDEN_PATH_DIR

# Global graph cache
_fraud_graph: Optional[nx.Graph] = None


def load_fraud_graph() -> nx.Graph:
    """Load the pre-baked fraud ring graph.

    Returns:
        NetworkX graph with fraud ring structure
    """
    global _fraud_graph

    if _fraud_graph is not None:
        return _fraud_graph

    # Load from golden path file
    fraud_file = Path(GOLDEN_PATH_DIR) / "fraud_hunter.json"

    if fraud_file.exists():
        with open(fraud_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        _fraud_graph = _build_graph_from_data(data)
    else:
        # Create empty graph if file doesn't exist
        _fraud_graph = nx.Graph()

    return _fraud_graph


def _build_graph_from_data(data: dict) -> nx.Graph:
    """Build NetworkX graph from JSON data.

    Args:
        data: Dictionary with 'nodes' and 'edges' lists

    Returns:
        NetworkX Graph
    """
    G = nx.Graph()

    # Add nodes
    for node in data.get("nodes", []):
        G.add_node(
            node["id"],
            type=node.get("type", "unknown"),
            label=node.get("label", node["id"]),
            specialty=node.get("specialty"),
            risk_score=node.get("risk_score", 0),
            total_claims=node.get("total_claims", 0),
            denial_rate=node.get("denial_rate", 0),
            is_fraud_ring_member=node.get("is_fraud_ring_member", False),
        )

    # Add edges
    for edge in data.get("edges", []):
        G.add_edge(
            edge["source"],
            edge["target"],
            relationship_type=edge.get("relationship_type", "related"),
            weight=edge.get("weight", 1),
        )

    return G


def get_provider_network(
    entity_id: str,
    depth: int = 2,
) -> dict:
    """Get the network around a specific entity.

    Args:
        entity_id: Provider or patient ID to analyze
        depth: How many hops to traverse (default: 2)

    Returns:
        Dictionary with nodes, edges, and findings
    """
    G = load_fraud_graph()

    # First, try to find the entity in the pre-baked fraud graph
    found_in_fraud_graph = entity_id in G
    
    if not found_in_fraud_graph:
        # Try to find by label
        matching_nodes = [n for n, d in G.nodes(data=True) if d.get("label") == entity_id]
        if matching_nodes:
            entity_id = matching_nodes[0]
            found_in_fraud_graph = True
    
    if found_in_fraud_graph:
        # Use the pre-baked fraud graph
        try:
            subgraph = nx.ego_graph(G, entity_id, radius=depth)
        except nx.NetworkXError:
            subgraph = G.subgraph([entity_id])

        nodes = []
        for node_id in subgraph.nodes():
            node_data = dict(G.nodes[node_id])
            node_data["id"] = node_id
            nodes.append(node_data)

        edges = []
        for source, target in subgraph.edges():
            edge_data = dict(G.edges[source, target])
            edge_data["source"] = source
            edge_data["target"] = target
            edges.append(edge_data)

        findings = _analyze_network_findings(subgraph, entity_id)

        return {
            "nodes": nodes,
            "edges": edges,
            "findings": findings,
            "center_entity": entity_id,
        }
    else:
        # Build dynamic network from claims data
        return _build_dynamic_provider_network(entity_id, depth)


def _analyze_network_findings(G: nx.Graph, center_id: str) -> list[dict]:
    """Analyze a network subgraph for fraud indicators.

    Args:
        G: NetworkX subgraph
        center_id: The central entity being analyzed

    Returns:
        List of finding dictionaries
    """
    findings = []

    # Check for circular referrals (cycles)
    try:
        # Convert to directed graph for cycle detection
        DG = G.to_directed()
        cycles = list(nx.simple_cycles(DG))

        if cycles:
            # Find cycles involving the center entity
            relevant_cycles = [c for c in cycles if center_id in c]
            if relevant_cycles:
                findings.append({
                    "finding_type": "circular_referral",
                    "description": f"Circular referral pattern detected involving {center_id}. Found {len(relevant_cycles)} cycle(s) in the network.",
                    "severity": "HIGH",
                })
    except Exception:
        pass

    # Check for high-degree nodes (unusual number of connections)
    center_degree = G.degree(center_id)
    avg_degree = sum(dict(G.degree()).values()) / len(G) if len(G) > 0 else 0

    if center_degree > avg_degree * 2:
        findings.append({
            "finding_type": "volume_anomaly",
            "description": f"{center_id} has {center_degree} connections, which is {center_degree/avg_degree:.1f}x the average.",
            "severity": "MEDIUM",
        })

    # Check for fraud ring members
    fraud_members = [n for n in G.nodes() if G.nodes[n].get("is_fraud_ring_member", False)]
    if len(fraud_members) > 1:
        findings.append({
            "finding_type": "billing_pattern",
            "description": f"Network contains {len(fraud_members)} entities flagged as potential fraud ring members.",
            "severity": "HIGH",
        })

    # If no findings, add a low-risk note
    if not findings:
        findings.append({
            "finding_type": "normal",
            "description": "No significant fraud indicators detected in this network segment.",
            "severity": "LOW",
        })

    return findings


def _build_dynamic_provider_network(entity_id: str, depth: int = 2) -> dict:
    """Build a dynamic network graph from claims data for a provider.
    
    This is used when the provider is not in the pre-baked fraud graph.
    
    Args:
        entity_id: Provider ID or name to analyze
        depth: Relationship depth (not fully used for dynamic graphs)
        
    Returns:
        Dictionary with nodes, edges, and findings
    """
    from src.services.claims_service import load_claims
    
    df = load_claims()
    
    # Find the provider - try by ID first, then by name
    provider_mask = (df["provider_id"] == entity_id)
    if not provider_mask.any():
        # Try by name (case-insensitive partial match)
        provider_mask = df["provider_name"].str.lower().str.contains(entity_id.lower(), na=False)
    
    if not provider_mask.any():
        return {
            "nodes": [],
            "edges": [],
            "findings": [{
                "finding_type": "not_found",
                "description": f"Provider '{entity_id}' not found in claims database.",
                "severity": "LOW",
            }],
            "error": f"Provider {entity_id} not found",
        }
    
    # Get provider info
    provider_claims = df[provider_mask]
    provider_id = provider_claims.iloc[0]["provider_id"]
    provider_name = provider_claims.iloc[0]["provider_name"]
    provider_specialty = provider_claims.iloc[0]["provider_specialty"]
    
    # Calculate provider stats
    total_claims = len(provider_claims)
    denied_claims = len(provider_claims[provider_claims["claim_status"] == "Denied"])
    denial_rate = denied_claims / total_claims if total_claims > 0 else 0
    total_amount = provider_claims["claim_amount"].sum()
    
    # Get unique patients for this provider
    patients = provider_claims[["patient_id", "patient_name"]].drop_duplicates()
    
    # Build graph
    G = nx.Graph()
    
    # Add provider node (center)
    G.add_node(
        provider_id,
        type="provider",
        label=provider_name,
        specialty=provider_specialty,
        risk_score=min(denial_rate * 1.5, 1.0),  # Simple risk calculation
        total_claims=total_claims,
        denial_rate=round(denial_rate, 3),
        is_fraud_ring_member=False,
    )
    
    # Add patient nodes and edges
    for _, patient in patients.iterrows():
        patient_id = patient["patient_id"]
        patient_name = patient["patient_name"]
        
        # Calculate patient-specific stats
        patient_provider_claims = provider_claims[provider_claims["patient_id"] == patient_id]
        claim_count = len(patient_provider_claims)
        
        # Check if this patient is connected to known fraud ring
        fraud_graph = load_fraud_graph()
        is_fraud_connected = patient_id in fraud_graph
        
        G.add_node(
            patient_id,
            type="patient",
            label=patient_name,
            risk_score=0.58 if is_fraud_connected else 0.2,
            total_claims=claim_count,
            is_fraud_ring_member=is_fraud_connected,
        )
        
        G.add_edge(
            provider_id,
            patient_id,
            relationship_type="treated_by",
            weight=claim_count,
        )
        
        # If patient is fraud-connected, add connection to fraud ring
        if is_fraud_connected:
            # Find what fraud ring members this patient connects to
            for neighbor in fraud_graph.neighbors(patient_id):
                neighbor_data = dict(fraud_graph.nodes[neighbor])
                if neighbor not in G:
                    G.add_node(
                        neighbor,
                        type=neighbor_data.get("type", "unknown"),
                        label=neighbor_data.get("label", neighbor),
                        specialty=neighbor_data.get("specialty"),
                        risk_score=neighbor_data.get("risk_score", 0.8),
                        is_fraud_ring_member=True,
                    )
                    G.add_edge(
                        patient_id,
                        neighbor,
                        relationship_type="fraud_ring_connection",
                        weight=1,
                    )
    
    # Convert to serializable format
    nodes = []
    for node_id in G.nodes():
        node_data = dict(G.nodes[node_id])
        node_data["id"] = node_id
        nodes.append(node_data)
    
    edges = []
    for source, target in G.edges():
        edge_data = dict(G.edges[source, target])
        edge_data["source"] = source
        edge_data["target"] = target
        edges.append(edge_data)
    
    # Generate findings
    findings = []
    
    # Check for fraud ring connections
    fraud_connected_patients = [n for n in G.nodes() if G.nodes[n].get("is_fraud_ring_member", False)]
    if fraud_connected_patients:
        findings.append({
            "finding_type": "fraud_ring_connection",
            "description": f"Provider has treated {len(fraud_connected_patients)} patient(s) connected to known fraud ring.",
            "severity": "HIGH",
        })
    
    # Check denial rate
    if denial_rate > 0.25:
        findings.append({
            "finding_type": "high_denial_rate",
            "description": f"Provider has a {denial_rate*100:.1f}% denial rate, which is above average.",
            "severity": "MEDIUM",
        })
    
    # Check billing volume
    if total_claims > 50:
        findings.append({
            "finding_type": "high_volume",
            "description": f"Provider has {total_claims} claims totaling ${total_amount:,.2f}.",
            "severity": "LOW",
        })
    
    if not findings:
        findings.append({
            "finding_type": "normal",
            "description": "No significant fraud indicators detected for this provider.",
            "severity": "LOW",
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "findings": findings,
        "center_entity": provider_id,
    }


def get_graph_statistics() -> dict:
    """Get statistics about the fraud graph.

    Returns:
        Dictionary with graph statistics
    """
    G = load_fraud_graph()

    providers = [n for n, d in G.nodes(data=True) if d.get("type") == "provider"]
    patients = [n for n, d in G.nodes(data=True) if d.get("type") == "patient"]
    fraud_members = [n for n, d in G.nodes(data=True) if d.get("is_fraud_ring_member", False)]

    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "providers": len(providers),
        "patients": len(patients),
        "fraud_ring_members": len(fraud_members),
        "density": nx.density(G) if G.number_of_nodes() > 0 else 0,
        "is_connected": nx.is_connected(G) if G.number_of_nodes() > 0 else False,
    }
