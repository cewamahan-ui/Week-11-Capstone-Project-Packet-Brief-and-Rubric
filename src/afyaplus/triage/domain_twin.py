"""Domain twin: deterministic triage assessment with no network calls.

Week 1-5 reuse: this is the stub model the whole system falls back on.
All acuity rules live in :mod:`src.afyaplus.triage.policy`, which is
also what generates the golden fixture labels - so fixture and runtime
cannot drift apart silently (see docs/incidents/2026-10-13-fixture-label-drift.md).
"""

from __future__ import annotations

from src.afyaplus.triage import policy
from src.afyaplus.triage.models import (
    PRIORITY_BY_ACUITY,
    RECOMMENDATION_TOKENS,
    TriageRequest,
    TriageResponse,
)


class DomainTwin:
    """Deterministic stand-in for a trained triage model (stub mode)."""

    def __init__(self) -> None:
        self.rules_version = "twin-rules-1.1"

    def clinical_severity(self, request: TriageRequest) -> str:
        """Delegate to the shared policy (kept as a convenience hook)."""
        return policy.clinical_severity(
            list(request.symptoms), request.age, dict(request.vitals)
        )

    def assess(self, request: TriageRequest) -> TriageResponse:
        """Full assessment: acuity, disposition token, priority, confidence."""
        patient = request.urgency_level
        clinical = policy.clinical_severity(list(request.symptoms), request.age, dict(request.vitals))
        acuity = policy.worst(patient, clinical)

        recognised = any(
            key in str(symptom).strip().lower()
            for symptom in request.symptoms
            for key in policy.SYMPTOM_SEVERITY
        )

        confidence = 0.55
        if patient in RECOMMENDATION_TOKENS:
            confidence += 0.15
        if recognised:
            confidence += 0.15
        if request.vitals:
            confidence += 0.10
        if request.age >= policy.ESCALATION_AGE_HIGH or request.age <= policy.ESCALATION_AGE_LOW:
            confidence += 0.05
        confidence = round(min(confidence, 0.99), 2)

        reasons = [
            f"patient_reported_urgency={patient}",
            f"clinical_severity={clinical}",
        ]
        if acuity != patient:
            reasons.append(f"escalated_from_patient_report={patient}")
        if request.vitals:
            reasons.append("vitals_considered")
        if request.age >= policy.ESCALATION_AGE_HIGH or request.age <= policy.ESCALATION_AGE_LOW:
            reasons.append("age_band_escalation")

        return TriageResponse(
            acuity=acuity,
            recommendation=RECOMMENDATION_TOKENS[acuity],
            priority=PRIORITY_BY_ACUITY[acuity],
            confidence_score=confidence,
            reasons=reasons,
        )

    def recommend(self, request: TriageRequest) -> str:
        """Disposition token only (quick helper used by the CLI pipeline)."""
        return self.assess(request).recommendation
