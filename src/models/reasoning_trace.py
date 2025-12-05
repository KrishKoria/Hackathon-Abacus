"""Reasoning trace model for ClaimsIQ Nexus.

Contains the ReasoningTrace model for agent decision logging.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class TraceStep(BaseModel):
    """Single step in agent reasoning.

    Records a single action taken by the agent during
    query processing for transparency.
    """

    step_number: int
    timestamp: datetime
    action_type: str  # "think", "tool_call", "observe", "respond"
    content: str
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_output: Optional[dict] = None
    duration_ms: int


class ReasoningTrace(BaseModel):
    """Complete trace of agent reasoning for a query.

    Captures all steps the agent took to process a query,
    including tool calls and their results.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Why was Claim #1023 denied?",
                "steps": [
                    {
                        "step_number": 1,
                        "timestamp": "2024-12-04T10:30:00",
                        "action_type": "think",
                        "content": "User wants to investigate a denied claim. I should query the claims database first.",
                        "duration_ms": 50,
                    },
                    {
                        "step_number": 2,
                        "timestamp": "2024-12-04T10:30:00",
                        "action_type": "tool_call",
                        "content": "Calling query_claims_db",
                        "tool_name": "query_claims_db",
                        "tool_input": {"filters": {"claim_id": "CLM-01023"}},
                        "duration_ms": 150,
                    },
                ],
                "total_duration_ms": 2500,
                "tools_called": ["query_claims_db", "search_clinical_notes"],
                "final_canvas_mode": "MODE_DOC",
                "used_cache": False,
            }
        }
    )

    query: str
    steps: List[TraceStep] = Field(default_factory=list)
    total_duration_ms: int = 0
    tools_called: List[str] = Field(default_factory=list)
    final_canvas_mode: Optional[str] = None
    used_cache: bool = False
