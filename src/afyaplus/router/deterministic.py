"""Deterministic request router (Week 1-2 reuse, no LLM dependency).

Routing follows the shared policy in :mod:`src.afyaplus.triage.policy`:
red-flag symptom first, then acuity, then routine/urgent symptom
vocabularies. Because the router now sees acuity (and the generator
labels ``expected_department`` with the same function), gold routing
labels and runtime routing cannot disagree.

The same input always produces the same output - what the automated
tests assert.
"""

from __future__ import annotations

from src.afyaplus.triage import policy
from src.afyaplus.triage.models import TriageRequest

POLICY_VERSION = "router-policy-1.1"


class Router:
    """Maps a triage case to a service endpoint without model calls."""

    def __init__(self) -> None:
        self.policy_version = POLICY_VERSION

    def route(self, request: TriageRequest) -> dict:
        """Return ``endpoint``, ``priority`` and the matched rule."""
        acuity = policy.compute_acuity(
            list(request.symptoms), request.age, request.urgency_level, dict(request.vitals)
        )
        endpoint, reason = policy.decide_endpoint(list(request.symptoms), acuity)

        return {
            "endpoint": endpoint,
            "priority": policy.ENDPOINT_PRIORITY[endpoint],
            "reason": reason,
            "acuity": acuity,
            "policy_version": POLICY_VERSION,
        }
