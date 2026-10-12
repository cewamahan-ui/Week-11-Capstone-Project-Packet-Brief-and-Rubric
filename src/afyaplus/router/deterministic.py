"""Deterministic request router (Week 1-2 reuse, no LLM dependency).

Routing is a fixed rule table: first match wins in the order
emergency -> urgent -> primary -> general. The same input always
produces the same output, which is what the automated tests assert.
"""

from __future__ import annotations

from src.afyaplus.triage.models import TriageRequest

EMERGENCY_ENDPOINT = "emergency_department"
URGENT_ENDPOINT = "urgent_care"
PRIMARY_ENDPOINT = "primary_care"
GENERAL_ENDPOINT = "general_practice"

EMERGENCY_TOKENS = {
    "chest_pain",
    "minor_cut",
    "severe_bleeding",
    "shortness_of_breath",
    "stroke_signs",
    "seizure",
    "unresponsive",
}
URGENT_TOKENS = {
    "fever",
    "high",
    "vomiting",
    "dehydration",
    "infection",
    "abdominal_pain",
}
PRIMARY_TOKENS = {
    "headache",
    "mild",
    "cough",
    "fatigue",
    "rash",
    "dizziness",
}
GENERAL_TOKENS = {
    "routine_checkup",
    "checkup",
    "follow_up",
    "prescription_refill",
}

ENDPOINT_PRIORITY = {
    EMERGENCY_ENDPOINT: 4,
    URGENT_ENDPOINT: 3,
    PRIMARY_ENDPOINT: 2,
    GENERAL_ENDPOINT: 1,
}

POLICY_VERSION = "router-policy-1.0"


class Router:
    """Maps a triage case to a service endpoint without model calls."""

    def __init__(self) -> None:
        self.policy_version = POLICY_VERSION

    @staticmethod
    def _match(symptoms: list[str], tokens: set[str]) -> bool:
        for symptom in symptoms:
            token = str(symptom).strip().lower()
            if any(t in token for t in tokens):
                return True
        return False

    def route(self, request: TriageRequest) -> dict:
        """Return ``endpoint``, ``priority`` and the matched rule."""
        symptoms = [str(s).lower() for s in request.symptoms]

        if self._match(symptoms, EMERGENCY_TOKENS):
            endpoint = EMERGENCY_ENDPOINT
            reason = "emergency_token_matched"
        elif self._match(symptoms, URGENT_TOKENS):
            endpoint = URGENT_ENDPOINT
            reason = "urgent_token_matched"
        elif self._match(symptoms, PRIMARY_TOKENS):
            endpoint = PRIMARY_ENDPOINT
            reason = "primary_token_matched"
        elif self._match(symptoms, GENERAL_TOKENS):
            endpoint = GENERAL_ENDPOINT
            reason = "general_token_matched"
        else:
            endpoint = PRIMARY_ENDPOINT
            reason = "default_primary_care"

        return {
            "endpoint": endpoint,
            "priority": ENDPOINT_PRIORITY[endpoint],
            "reason": reason,
            "policy_version": POLICY_VERSION,
        }
