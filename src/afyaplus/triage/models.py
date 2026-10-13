"""Request/response models for the triage service.

Week 6 reuse: field constraints follow the same pattern as the Week 6
triage API (bounded age, constrained acuity vocabulary, non-empty
symptom list). All inputs are synthetic teaching data - no patient
identifiers are accepted in these models.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Acuity = Literal["low", "moderate", "high"]

# Canonical disposition vocabulary. The golden fixture and every
# consumer of the domain twin compare against these exact tokens.
RECOMMENDATION_TOKENS: dict[str, str] = {
    "high": "immediate_attention",
    "moderate": "within_24_hours",
    "low": "routine_follow_up",
}

# Priority scale: 1 = lowest, 4 = immediate.
PRIORITY_BY_ACUITY: dict[str, int] = {
    "high": 4,
    "moderate": 3,
    "low": 2,
}


class TriageRequest(BaseModel):
    """A triage case as submitted by clinic staff."""

    symptoms: list[str] = Field(
        min_length=1,
        description="Non-empty list of free-text or coded symptoms.",
    )
    age: int = Field(ge=0, le=120, description="Patient age in years.")
    urgency_level: Acuity = Field(
        default="moderate",
        description="Patient-reported urgency (low / moderate / high).",
    )
    vitals: dict[str, float] = Field(
        default_factory=dict,
        description="Optional numeric vitals, e.g. temperature, heart_rate.",
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional free-text note; redacted before it is echoed or logged.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "symptoms": ["fever", "cough"],
                "age": 28,
                "urgency_level": "moderate",
                "vitals": {"temperature": 38.6, "heart_rate": 96},
                "note": "Call me on 0712345678",
            }
        }
    }


class TriageResponse(BaseModel):
    """Deterministic assessment produced by the domain twin."""

    acuity: Acuity
    recommendation: str
    priority: int = Field(ge=1, le=4)
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    request_id: str = ""
    redacted_note: str = ""
