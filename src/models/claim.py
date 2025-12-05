"""Claim data model for ClaimsIQ Nexus.

Contains the core Claim model with all 20 fields, along with
Provider and Patient models for fraud graph analysis.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ClaimStatus(str, Enum):
    """Claim processing status."""

    APPROVED = "Approved"
    DENIED = "Denied"
    PENDING = "Pending"


class ProviderSpecialty(str, Enum):
    """Healthcare provider specialty categories."""

    CARDIOLOGY = "Cardiology"
    ONCOLOGY = "Oncology"
    ORTHOPEDICS = "Orthopedics"
    NEUROLOGY = "Neurology"
    EMERGENCY_MEDICINE = "Emergency Medicine"
    PRIMARY_CARE = "Primary Care"
    DERMATOLOGY = "Dermatology"
    GASTROENTEROLOGY = "Gastroenterology"


class DenialReason(str, Enum):
    """Standard claim denial reasons."""

    PRE_AUTH = "Pre-auth not obtained"
    OUT_OF_NETWORK = "Out of network"
    NOT_MEDICALLY_NECESSARY = "Not medically necessary"
    DUPLICATE = "Duplicate claim"
    INCOMPLETE = "Incomplete information"


class Claim(BaseModel):
    """Healthcare claim record with 20 fields.

    This model represents a complete healthcare billing record
    including patient, provider, clinical, financial, status,
    and temporal information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "claim_id": "CLM-01023",
                "patient_id": "P-0456",
                "patient_name": "John Smith",
                "patient_age": 45,
                "patient_gender": "Male",
                "provider_id": "PRV-007",
                "provider_name": "Dr. Jane Wilson",
                "provider_specialty": "Cardiology",
                "diagnosis_code": "I10",
                "diagnosis_description": "Essential hypertension",
                "procedure_code": "99214",
                "procedure_description": "Office visit, established patient",
                "claim_amount": 250.00,
                "approved_amount": None,
                "claim_status": "Denied",
                "denial_reason": "Not medically necessary",
                "claim_date": "2024-06-15",
                "processing_date": "2024-06-20",
                "is_emergency": False,
                "is_inpatient": False,
            }
        }
    )

    # Identifiers
    claim_id: str = Field(..., pattern=r"^CLM-\d{5}$", description="Unique claim identifier")

    # Patient Information
    patient_id: str = Field(..., pattern=r"^P-\d{4}$", description="Patient identifier")
    patient_name: str = Field(..., min_length=1, max_length=100)
    patient_age: int = Field(..., ge=0, le=120)
    patient_gender: str = Field(..., pattern=r"^(Male|Female|Other)$")

    # Provider Information
    provider_id: str = Field(..., pattern=r"^PRV-\d{3}$", description="Provider identifier")
    provider_name: str = Field(..., min_length=1, max_length=100)
    provider_specialty: ProviderSpecialty

    # Clinical Information
    diagnosis_code: str = Field(..., description="ICD-10 code")
    diagnosis_description: str
    procedure_code: str = Field(..., description="CPT code")
    procedure_description: str

    # Financial Information
    claim_amount: Decimal = Field(..., gt=0, description="Billed amount in USD")
    approved_amount: Optional[Decimal] = Field(
        default=None, ge=0, description="Approved amount (None if pending/denied)"
    )

    # Status Information
    claim_status: ClaimStatus
    denial_reason: Optional[DenialReason] = Field(default=None)

    # Temporal Information
    claim_date: date
    processing_date: Optional[date] = None

    # Flags
    is_emergency: bool = False
    is_inpatient: bool = False

    @field_validator("denial_reason")
    @classmethod
    def denial_reason_required_if_denied(cls, v, info):
        """Validate that denial_reason is present when claim is denied."""
        if info.data.get("claim_status") == ClaimStatus.DENIED and v is None:
            raise ValueError("denial_reason required when claim_status is Denied")
        return v

    @field_validator("approved_amount")
    @classmethod
    def approved_not_exceed_claim(cls, v, info):
        """Validate that approved_amount does not exceed claim_amount."""
        claim_amount = info.data.get("claim_amount")
        if v is not None and claim_amount is not None and v > claim_amount:
            raise ValueError("approved_amount cannot exceed claim_amount")
        return v


class Provider(BaseModel):
    """Healthcare provider for fraud analysis.

    Used in the fraud graph to represent providers and their
    relationships with patients and other providers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider_id": "PRV-007",
                "name": "Dr. X",
                "specialty": "Cardiology",
                "is_fraud_ring_member": True,
                "risk_score": 0.85,
                "total_claims": 150,
                "denial_rate": 0.12,
                "average_claim_amount": 3500.00,
            }
        }
    )

    provider_id: str = Field(..., pattern=r"^PRV-\d{3}$")
    name: str
    specialty: ProviderSpecialty
    is_fraud_ring_member: bool = Field(default=False)
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)

    # Computed statistics
    total_claims: int = 0
    denial_rate: float = 0.0
    average_claim_amount: float = 0.0


class Patient(BaseModel):
    """Patient entity for relationship mapping.

    Used in the fraud graph to represent patients and their
    relationships with providers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_id": "P-0456",
                "name": "John Smith",
                "age": 45,
                "gender": "Male",
                "is_fraud_ring_member": False,
            }
        }
    )

    patient_id: str = Field(..., pattern=r"^P-\d{4}$")
    name: str
    age: int = Field(..., ge=0, le=120)
    gender: str
    is_fraud_ring_member: bool = Field(default=False)
