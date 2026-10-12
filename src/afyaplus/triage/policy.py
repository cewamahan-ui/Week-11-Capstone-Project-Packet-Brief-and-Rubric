"""Single decision policy for triage acuity and routing.

The domain twin, the deterministic router and the fixture generator
all import from this module, so there is exactly one copy of the
rules. That is what keeps the golden labels in
``fixtures/triage_messages_sample.jsonl`` from drifting away from
what the runtime enforces - the failure mode recorded in
``docs/incidents/2026-10-13-fixture-label-drift.md``.

Acuity policy
    worst of (patient-reported urgency, symptom severity, vitals
    thresholds, age-band escalation).

Routing policy
    1. red-flag symptom        -> emergency_department
    2. acuity == high          -> urgent_care
    3. routine symptom         -> general_practice
    4. urgent symptom (fever…) -> urgent_care
    5. otherwise               -> primary_care
"""

from __future__ import annotations

# --- acuity ------------------------------------------------------------

ACUITY_ORDER: tuple[str, ...] = ("low", "moderate", "high")

# Symptom vocabulary -> clinical severity (substring match).
SYMPTOM_SEVERITY: dict[str, str] = {
    # high
    "chest_pain": "high",
    "minor_cut": "high",
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

# Vitals thresholds (synthetic teaching values).
TEMP_MODERATE = 38.0
TEMP_HIGH = 39.5
HR_HIGH = 120
HR_LOW = 50

# Age bands that force one escalation step.
ESCALATION_AGE_HIGH = 65
ESCALATION_AGE_LOW = 2


def severity_rank(level: str) -> int:
    return ACUITY_ORDER.index(level)


def worst(*levels: str) -> str:
    return max(levels, key=severity_rank)


def escalate(level: str) -> str:
    index = min(severity_rank(level) + 1, len(ACUITY_ORDER) - 1)
    return ACUITY_ORDER[index]


def clinical_severity(symptoms: list, age: int, vitals: dict | None) -> str:
    """Clinical severity from symptoms, vitals thresholds and age band."""
    vitals = vitals or {}
    severity = "low"

    for symptom in symptoms:
        token = str(symptom).strip().lower()
        for key, level in SYMPTOM_SEVERITY.items():
            if key in token:
                severity = worst(severity, level)
                break

    temperature = vitals.get("temperature")
    if temperature is not None:
        if temperature >= TEMP_HIGH:
            severity = worst(severity, "high")
        elif temperature >= TEMP_MODERATE:
            severity = worst(severity, "moderate")

    heart_rate = vitals.get("heart_rate")
    if heart_rate is not None and (heart_rate >= HR_HIGH or heart_rate <= HR_LOW):
        severity = worst(severity, "high")

    if int(age) >= ESCALATION_AGE_HIGH or int(age) <= ESCALATION_AGE_LOW:
        severity = escalate(severity)

    return severity


def compute_acuity(symptoms: list, age: int, urgency_level: str, vitals: dict | None) -> str:
    """Final acuity: never below patient-reported urgency, never below clinical."""
    return worst(str(urgency_level), clinical_severity(symptoms, age, vitals))


# --- routing -----------------------------------------------------------

EMERGENCY_ENDPOINT = "emergency_department"
URGENT_ENDPOINT = "urgent_care"
PRIMARY_ENDPOINT = "primary_care"
GENERAL_ENDPOINT = "general_practice"

ENDPOINT_PRIORITY = {
    EMERGENCY_ENDPOINT: 4,
    URGENT_ENDPOINT: 3,
    PRIMARY_ENDPOINT: 2,
    GENERAL_ENDPOINT: 1,
}

RED_FLAG_TOKENS = {
    "chest_pain",
    "minor_cut",
    "severe_bleeding",
    "shortness_of_breath",
    "stroke_signs",
    "seizure",
    "unresponsive",
}
ROUTINE_TOKENS = {
    "routine_checkup",
    "checkup",
    "follow_up",
    "prescription_refill",
}
URGENT_TOKENS = {
    "fever",
    "vomiting",
    "dehydration",
    "infection",
    "abdominal_pain",
}


def _matches(symptoms: list, tokens: set[str]) -> bool:
    for symptom in symptoms:
        token = str(symptom).strip().lower()
        if any(t in token for t in tokens):
            return True
    return False


def decide_endpoint(symptoms: list, acuity: str) -> tuple[str, str]:
    """Return ``(endpoint, reason)`` for a case under the routing policy."""
    if _matches(symptoms, RED_FLAG_TOKENS):
        return EMERGENCY_ENDPOINT, "red_flag_symptom"
    if str(acuity) == "high":
        return URGENT_ENDPOINT, "high_acuity"
    if _matches(symptoms, ROUTINE_TOKENS):
        return GENERAL_ENDPOINT, "routine_token_matched"
    if _matches(symptoms, URGENT_TOKENS):
        return URGENT_ENDPOINT, "urgent_token_matched"
    return PRIMARY_ENDPOINT, "default_primary_care"
