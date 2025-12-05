"""Claims service for ClaimsIQ Nexus.

Provides Pandas-based operations for querying and filtering
the structured claims database (CSV).
"""

from datetime import date
from typing import Optional
import pandas as pd

from src.config import CLAIMS_CSV_PATH

# Global claims dataframe cache
_claims_df: Optional[pd.DataFrame] = None


def load_claims(force_reload: bool = False) -> pd.DataFrame:
    """Load claims data from CSV into a Pandas DataFrame.

    Args:
        force_reload: If True, reload from disk even if cached

    Returns:
        DataFrame containing all claims
    """
    global _claims_df

    if _claims_df is None or force_reload:
        _claims_df = pd.read_csv(
            CLAIMS_CSV_PATH,
            parse_dates=["claim_date", "processing_date"],
            dtype={
                "claim_id": str,
                "patient_id": str,
                "provider_id": str,
                "is_emergency": bool,
                "is_inpatient": bool,
            },
        )
        # Ensure claim_amount is float
        _claims_df["claim_amount"] = pd.to_numeric(
            _claims_df["claim_amount"], errors="coerce"
        )
        _claims_df["approved_amount"] = pd.to_numeric(
            _claims_df["approved_amount"], errors="coerce"
        )

    return _claims_df


def get_claim_by_id(claim_id: str) -> Optional[dict]:
    """Get a single claim by its ID.

    Args:
        claim_id: The claim identifier (e.g., "CLM-01023")

    Returns:
        Claim data as dictionary, or None if not found
    """
    df = load_claims()

    # Normalize claim_id format
    if not claim_id.startswith("CLM-"):
        # Handle cases like "1023" -> "CLM-01023"
        claim_id = f"CLM-{int(claim_id):05d}"

    result = df[df["claim_id"] == claim_id]

    if result.empty:
        return None

    # Convert to dict and handle NaN values
    claim_dict = result.iloc[0].to_dict()

    # Convert NaN to None
    for key, value in claim_dict.items():
        if pd.isna(value):
            claim_dict[key] = None
        elif isinstance(value, pd.Timestamp):
            claim_dict[key] = value.strftime("%Y-%m-%d")

    return claim_dict


def filter_claims(
    filters: Optional[dict] = None,
    sort_by: str = "claim_date",
    ascending: bool = False,
    limit: int = 10,
) -> list[dict]:
    """Filter claims based on criteria.

    Args:
        filters: Dictionary of filter criteria:
            - claim_id: Exact match
            - patient_id: Exact match
            - provider_id: Exact match
            - status: Exact match (Approved, Denied, Pending)
            - specialty: Exact match
            - denial_reason: Exact match
            - date_from: Claims on or after this date
            - date_to: Claims on or before this date
            - is_emergency: Boolean filter
            - is_inpatient: Boolean filter
        sort_by: Column to sort by (default: claim_date)
        ascending: Sort order (default: False, descending)
        limit: Maximum number of results (default: 10)

    Returns:
        List of claim dictionaries
    """
    df = load_claims().copy()

    if filters:
        # Apply filters
        if "claim_id" in filters and filters["claim_id"]:
            claim_id = filters["claim_id"]
            if not claim_id.startswith("CLM-"):
                claim_id = f"CLM-{int(claim_id):05d}"
            df = df[df["claim_id"] == claim_id]

        if "patient_id" in filters and filters["patient_id"]:
            df = df[df["patient_id"] == filters["patient_id"]]

        if "provider_id" in filters and filters["provider_id"]:
            df = df[df["provider_id"] == filters["provider_id"]]

        if "status" in filters and filters["status"]:
            df = df[df["claim_status"] == filters["status"]]

        if "specialty" in filters and filters["specialty"]:
            df = df[df["provider_specialty"] == filters["specialty"]]

        if "denial_reason" in filters and filters["denial_reason"]:
            df = df[df["denial_reason"] == filters["denial_reason"]]

        if "date_from" in filters and filters["date_from"]:
            date_from = pd.to_datetime(filters["date_from"])
            df = df[df["claim_date"] >= date_from]

        if "date_to" in filters and filters["date_to"]:
            date_to = pd.to_datetime(filters["date_to"])
            df = df[df["claim_date"] <= date_to]

        if "is_emergency" in filters:
            df = df[df["is_emergency"] == filters["is_emergency"]]

        if "is_inpatient" in filters:
            df = df[df["is_inpatient"] == filters["is_inpatient"]]

    # Sort
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)

    # Limit
    df = df.head(limit)

    # Convert to list of dicts
    results = []
    for _, row in df.iterrows():
        claim_dict = row.to_dict()
        # Convert NaN to None and Timestamps to strings
        for key, value in claim_dict.items():
            if pd.isna(value):
                claim_dict[key] = None
            elif isinstance(value, pd.Timestamp):
                claim_dict[key] = value.strftime("%Y-%m-%d")
        results.append(claim_dict)

    return results


def get_claims_stats() -> dict:
    """Get summary statistics for claims data.

    Returns:
        Dictionary with claims statistics
    """
    df = load_claims()

    return {
        "total_claims": len(df),
        "by_status": df["claim_status"].value_counts().to_dict(),
        "by_specialty": df["provider_specialty"].value_counts().to_dict(),
        "total_amount": float(df["claim_amount"].sum()),
        "average_amount": float(df["claim_amount"].mean()),
        "denial_rate": float(
            (df["claim_status"] == "Denied").sum() / len(df)
        ) if len(df) > 0 else 0,
    }


def get_denial_trends_by_specialty() -> list[dict]:
    """Calculate denial rates grouped by specialty.

    Returns:
        List of dicts with specialty, denial_rate, and count
    """
    df = load_claims()

    # Group by specialty
    grouped = df.groupby("provider_specialty").agg(
        total=("claim_id", "count"),
        denied=("claim_status", lambda x: (x == "Denied").sum()),
        approved=("claim_status", lambda x: (x == "Approved").sum()),
        total_amount=("claim_amount", "sum"),
    ).reset_index()

    grouped["denial_rate"] = grouped["denied"] / grouped["total"]
    grouped["approval_rate"] = grouped["approved"] / grouped["total"]

    # Convert to list of dicts
    results = []
    for _, row in grouped.iterrows():
        results.append({
            "specialty": row["provider_specialty"],
            "total_claims": int(row["total"]),
            "denied_claims": int(row["denied"]),
            "approved_claims": int(row["approved"]),
            "denial_rate": round(float(row["denial_rate"]), 4),
            "approval_rate": round(float(row["approval_rate"]), 4),
            "total_amount": round(float(row["total_amount"]), 2),
        })

    return sorted(results, key=lambda x: x["denial_rate"], reverse=True)
