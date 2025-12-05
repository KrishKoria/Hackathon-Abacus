"""Query Claims Database tool for ClaimsIQ Nexus.

MCP-style tool for structured SQL-like queries against the claims database.
"""

from typing import Optional

from langchain_core.tools import tool

from src.services.claims_service import filter_claims, get_claim_by_id


@tool
def query_claims_db(
    filters: Optional[dict] = None,
    sort_by: str = "claim_date",
    limit: int = 10,
) -> dict:
    """Query the structured claims database.

    Structured SQL-like query capability for the claims database.
    Supports filtering by claim ID, patient, provider, status, date range,
    and specialty. Returns matching claims with pagination support.

    Args:
        filters: Dictionary of filter criteria:
            - claim_id: Specific claim ID (e.g., "CLM-01023" or "1023")
            - patient_id: Filter by patient (e.g., "P-0456")
            - provider_id: Filter by provider (e.g., "PRV-007")
            - status: Claim status (Approved, Denied, Pending)
            - specialty: Provider specialty (e.g., "Cardiology")
            - denial_reason: Specific denial reason
            - date_from: Start of date range (YYYY-MM-DD)
            - date_to: End of date range (YYYY-MM-DD)
        sort_by: Field to sort by (claim_date, claim_amount, processing_date)
        limit: Maximum number of results (1-100, default 10)

    Returns:
        Dictionary with:
            - claims: List of matching claim records
            - total_count: Total matches (before limit)
            - ui_hint: Suggested Canvas mode (MODE_CLAIM or MODE_CHART)

    Examples:
        Query single claim:
            query_claims_db(filters={"claim_id": "CLM-01023"})

        Query denied cardiology claims:
            query_claims_db(filters={"status": "Denied", "specialty": "Cardiology"})
    """
    # Handle None or empty filters
    if filters is None:
        filters = {}

    # Validate limit
    limit = max(1, min(100, limit))

    # Check for single claim query
    if filters.get("claim_id"):
        claim_id = filters["claim_id"]
        claim = get_claim_by_id(claim_id)

        if claim:
            return {
                "claims": [claim],
                "total_count": 1,
                "ui_hint": "MODE_CLAIM",
                "query_type": "single_claim",
            }
        else:
            return {
                "claims": [],
                "total_count": 0,
                "ui_hint": "MODE_EMPTY",
                "error": f"Claim {claim_id} not found",
            }

    # Multiple claims query
    claims = filter_claims(
        filters=filters,
        sort_by=sort_by,
        limit=limit,
    )

    # Determine UI hint based on result count
    if len(claims) == 0:
        ui_hint = "MODE_EMPTY"
    elif len(claims) == 1:
        ui_hint = "MODE_CLAIM"
    else:
        ui_hint = "MODE_CHART"  # Multiple claims better as chart/table

    return {
        "claims": claims,
        "total_count": len(claims),
        "ui_hint": ui_hint,
        "query_type": "filtered_query",
        "filters_applied": filters,
    }
