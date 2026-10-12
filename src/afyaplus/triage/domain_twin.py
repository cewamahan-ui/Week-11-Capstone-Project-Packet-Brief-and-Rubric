"""Domain twin: deterministic triage assessment with no network calls.

Week 1-5 reuse: this is the stub model the whole system falls back on.
The acuity decision is the worst of (a) patient-reported urgency,
(b) clinical severity derived from symptoms, (c) vitals thresholds and
(d) age escalation. The same rules are exercised by the golden fixture
tests, so any drift between fixture labels and twin output fails loudly
in ``tests/test_gold_fixture.py``.
"""

from __future__ import annotations

from src.afyaplus.triage.models import (
    PRIORITY_BY_ACUITY,
    RECOMMENDATION_TOKENS,
    TriageRequest,
    TriageResponse,
)

ACUITY_ORDER: tuple[str, ...] = ("low", "moderate", "high")

# Symptom vocabulary -> clinical severity. Matching is substring based
# so that "severe_chest_pain" still resolves to the chest_pain entry.
SYMPTOM_SEVERITY: dict[str, str] = {
    # high
    "chest_pain": "high",
    "severe_bleeding": "high",
    "shortness_of_breath": "high",
    "stroke_signs": "high",
    "seizure": "high",
    "unresponsive": "high",
    "confusion": "high",
    "severe_pain": "high",
    # moderate
    "fever": "moderate",
    "vomiting": "moderate",
    "dehydration": "moderate",
    "infection": "moderate",
    "headache": "moderate",
    "injury": "moderate",
    "rash": "moderate",
    "dizziness": "moderate",
    "abdominal_pain": "moderate",
    # low
    "mild": "low",
    "fatigue": "low",
    "cough": "low",
    "routine_checkup": "low",
    "follow_up": "low",
    "prescription_refill": "low",
}

# Vitals thresholds (values are synthetic teaching data).
TEMP_MODERATE = 38.0
TEMP_HIGH = 39.5
HR_HIGH = 120
HR_LOW = 50

# Age bands that force one escalation step.
ESCALATION_AGE_HIGH = 65
ESCALATION_AGE_LOW = 2


def _severity_rank(level: str) -> int:
    return ACUITY_ORDER.index(level)


def _worst(*levels: str) -> str:
    return max(levels, key=_severity_rank)


def _escalate(level: str) -> str:
    idx = min(_severity_rank(level) + 1, len(ACUITY_ORDER) - 1)
    return ACUITY_ORDER[idx]


class DomainTwin:
    """Deterministic stand-in for a trained triage model (stub mode)."""

    def __init__(self) -> None:
        self.rules_version = "twin-rules-1.0"

    def clinical_severity(self, request: TriageRequest) -> str:
        """Derive clinical severity from symptoms, vitals and age."""
        severity = "low"
        recognised = False
        for symptom in request.symptoms:
            token = str(symptom).strip().lower()
            for key, level in SYMPTOM_SEVERITY.items():
                if key in token:
                    severity = _worst(severity, level)
                    recognised = True
                    break
        if not recognised:
            severity = _worst(severity, "low")

        temperature = request.vitals.get("temperature")
        if temperature is not None:
            if temperature >= TEMP_HIGH:
                severity = _worst(severity, "high")
            elif temperature >= TEMP_MODERATE:
                severity = _worst(severity, "moderate")

        heart_rate = request.vitals.get("heart_rate")
        if heart_rate is not None and (heart_rate >= HR_HIGH or heart_rate <= HR_LOW):
            severity = _worst(severity, "high")

        if request.age >= ESCALATION_AGE_HIGH or request.age <= ESCALATION_AGE_LOW:
            severity = _escalate(severity)

        return severity

    def assess(self, request: TriageRequest) -> TriageResponse:
        """Full assessment: acuity, disposition token, priority, confidence."""
        patient = request.urgency_level
        clinical = self.clinical_severity(request)
        acuity = _worst(patient, clinical)

        recognised = any(
            key in str(symptom).strip().lower() for symptom in request.symptoms
            for key in SYMPTOM_SEVERITY
        )

        confidence = 0.55
        if patient in RECOMMENDATION_TOKENS:
            confidence += 0.15
        if recognised:
            confidence += 0.15
        if request.vitals:
            confidence += 0.10
        if request.age >= ESCALATION_AGE_HIGH or request.age <= ESCALATION_AGE_LOW:
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
        if request.age >= ESCALATION_AGE_HIGH or request.age <= ESCALATION_AGE_LOW:
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
