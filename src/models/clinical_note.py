"""Clinical note data model for ClaimsIQ Nexus.

Contains the ClinicalNote model for unstructured clinical documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NoteType(str, Enum):
    """Types of clinical notes."""

    CHIEF_COMPLAINT = "ChiefComplaint"
    NURSING_NOTES = "NursingNotes"
    RADIOLOGY_REPORT = "RadiologyReport"
    PROCEDURE_NOTES = "ProcedureNotes"


class ClinicalNote(BaseModel):
    """Unstructured clinical documentation.

    Clinical notes are stored as Markdown files and indexed
    in ChromaDB for semantic search.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "note_id": "CN-001",
                "patient_id": "P-0456",
                "claim_id": "CLM-01023",
                "note_date": "2024-06-15T14:30:00",
                "note_type": "ChiefComplaint",
                "content": "Patient presented to the Emergency Department with severe chest pain radiating to left arm. Initial assessment indicates acute myocardial infarction. Immediate cardiac catheterization recommended.",
                "is_golden_nugget": True,
            }
        }
    )

    note_id: str = Field(..., pattern=r"^CN-\d{3}$", description="Unique note identifier")
    patient_id: str = Field(..., pattern=r"^P-\d{4}$", description="Patient identifier")
    claim_id: Optional[str] = Field(
        default=None, pattern=r"^CLM-\d{5}$", description="Linked claim if applicable"
    )
    note_date: datetime
    note_type: NoteType
    content: str = Field(..., min_length=50, description="The clinical note text")
    is_golden_nugget: bool = Field(
        default=False, description="Pre-scripted contradiction for demo"
    )
