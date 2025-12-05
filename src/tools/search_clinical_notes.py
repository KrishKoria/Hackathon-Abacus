"""Search Clinical Notes tool for ClaimsIQ Nexus.

MCP-style tool for semantic search over clinical notes using ChromaDB.
"""

import re
from typing import Optional

from langchain_core.tools import tool

from src.services.rag_service import search_notes, get_note_by_id


# Minimum similarity score to consider a result relevant
MIN_SIMILARITY_THRESHOLD = 0.75


def _extract_patient_id_from_query(query: str) -> Optional[str]:
    """Extract patient ID from query if present.
    
    Args:
        query: Search query string
        
    Returns:
        Patient ID if found, None otherwise
    """
    # Match patterns like P-0024, P-1234, etc.
    match = re.search(r'\b(P-\d{4})\b', query, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def _extract_claim_id_from_query(query: str) -> Optional[str]:
    """Extract claim ID from query if present.
    
    Args:
        query: Search query string
        
    Returns:
        Claim ID if found, None otherwise
    """
    # Match patterns like CLM-00411, CLM-01234, etc.
    match = re.search(r'\b(CLM-\d{5})\b', query, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


@tool
def search_clinical_notes(
    query: str,
    patient_id: Optional[str] = None,
    limit: int = 5,
) -> dict:
    """Semantic search over clinical notes.

    Semantic search over unstructured patient records and clinical notes
    using vector embeddings. Supports optional patient ID filter.
    Returns relevant text chunks with similarity scores and citations.

    Args:
        query: Natural language search query (3-500 chars).
               Be specific about what you're looking for.
               Example: "cardiac emergency chest pain STEMI"
        patient_id: Optional patient filter (e.g., "P-0456")
        limit: Maximum number of results (1-20, default 5)

    Returns:
        Dictionary with:
            - results: List of matching notes with:
                - note_id: Unique note identifier
                - patient_id: Patient identifier
                - claim_id: Linked claim (if any)
                - note_type: Type of clinical note
                - content_snippet: Relevant excerpt
                - full_content: Complete note content
                - similarity_score: Relevance score (0-1)
                - is_golden_nugget: If this is a pre-scripted contradiction
            - ui_hint: "MODE_DOC" if relevant results found, "MODE_EMPTY" otherwise

    Examples:
        Search for trauma notes:
            search_clinical_notes(query="severe trauma surgery")

        Search for specific patient:
            search_clinical_notes(query="cardiac", patient_id="P-0456")
    """
    # Validate query
    if not query or len(query) < 3:
        return {
            "results": [],
            "ui_hint": "MODE_EMPTY",
            "error": "Query must be at least 3 characters",
        }

    if len(query) > 500:
        query = query[:500]

    # Validate limit
    limit = max(1, min(20, limit))
    
    # Extract patient_id from query if not explicitly provided
    query_patient_id = _extract_patient_id_from_query(query)
    query_claim_id = _extract_claim_id_from_query(query)
    
    # Use explicit patient_id if provided, otherwise use extracted one
    effective_patient_id = patient_id or query_patient_id

    # Perform search with patient filter if we have a patient ID
    results = search_notes(
        query=query,
        patient_id=effective_patient_id,
        limit=limit,
    )
    
    # If we had a specific patient/claim ID but got no results, report that clearly
    if not results:
        message_parts = []
        if effective_patient_id:
            message_parts.append(f"patient {effective_patient_id}")
        if query_claim_id:
            message_parts.append(f"claim {query_claim_id}")
        
        if message_parts:
            message = f"No clinical notes found for {' and '.join(message_parts)}"
        else:
            message = f"No clinical notes found matching '{query}'"
        
        return {
            "results": [],
            "ui_hint": "MODE_EMPTY",
            "message": message,
            "searched_patient_id": effective_patient_id,
            "searched_claim_id": query_claim_id,
        }
    
    # Filter results by relevance
    # If we're searching for a specific patient, only include results for that patient
    if effective_patient_id:
        patient_results = [r for r in results if r.get("patient_id") == effective_patient_id]
        if patient_results:
            results = patient_results
        else:
            # No results for the specific patient - return empty
            return {
                "results": [],
                "ui_hint": "MODE_EMPTY",
                "message": f"No clinical notes found for patient {effective_patient_id}",
                "searched_patient_id": effective_patient_id,
                "searched_claim_id": query_claim_id,
                "note": f"Semantic search found {len(results)} notes for other patients, but none for {effective_patient_id}",
            }
    
    # If we're searching for a specific claim, prioritize results linked to that claim
    if query_claim_id:
        claim_results = [r for r in results if r.get("claim_id") == query_claim_id]
        if claim_results:
            results = claim_results
    
    # Filter by minimum similarity threshold
    relevant_results = [r for r in results if r.get("similarity_score", 0) >= MIN_SIMILARITY_THRESHOLD]
    
    # If no results meet the threshold, check if we should still show them
    if not relevant_results:
        # If we had specific search criteria and nothing is relevant enough, return empty
        if effective_patient_id or query_claim_id:
            return {
                "results": [],
                "ui_hint": "MODE_EMPTY",
                "message": f"No sufficiently relevant clinical notes found",
                "searched_patient_id": effective_patient_id,
                "searched_claim_id": query_claim_id,
                "note": f"Found {len(results)} notes but none with similarity score above {MIN_SIMILARITY_THRESHOLD}",
            }
        # For general searches, use whatever we have but mark as low relevance
        relevant_results = results

    return {
        "results": relevant_results,
        "ui_hint": "MODE_DOC" if relevant_results else "MODE_EMPTY",
        "query": query,
        "total_results": len(relevant_results),
        "searched_patient_id": effective_patient_id,
        "searched_claim_id": query_claim_id,
    }
