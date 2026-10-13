"""Golden-set evaluation over the teaching fixture (Weeks 3 and 5 reuse).

The eval compares the deterministic pipeline (router + domain twin)
against the fixture's expected labels and reports exact-match
accuracy. It never calls a paid API: the fixture is the golden set,
the stub model is the system under test.
"""

from __future__ import annotations

from src.afyaplus.router.deterministic import Router
from src.afyaplus.triage.domain_twin import DomainTwin
from src.afyaplus.triage.models import TriageRequest

TOLERANCE = 0.0


def _request_from_row(row: dict) -> TriageRequest:
    return TriageRequest(
        symptoms=list(row["symptoms"]),
        age=int(row["age"]),
        urgency_level=row.get("urgency_level", "moderate"),
        vitals=dict(row.get("vitals", {})),
    )


def evaluate(rows: list[dict]) -> dict:
    """Score the stub pipeline against gold labels; returns metrics dict."""
    twin = DomainTwin()
    router = Router()

    total = len(rows)
    acuity_matches = 0
    recommendation_matches = 0
    endpoint_matches = 0
    mismatches: list[dict] = []

    for row in rows:
        request = _request_from_row(row)
        response = twin.assess(request)
        route = router.route(request)

        acuity_ok = response.acuity == row.get("expected_urgency")
        rec_ok = response.recommendation == row.get("expected_recommendation")
        endpoint_ok = route["endpoint"] == row.get("expected_department")

        acuity_matches += int(acuity_ok)
        recommendation_matches += int(rec_ok)
        endpoint_matches += int(endpoint_ok)

        if not (acuity_ok and rec_ok and endpoint_ok):
            mismatches.append(
                {
                    "id": row.get("id"),
                    "got": {
                        "acuity": response.acuity,
                        "recommendation": response.recommendation,
                        "endpoint": route["endpoint"],
                    },
                    "expected": {
                        "acuity": row.get("expected_urgency"),
                        "recommendation": row.get("expected_recommendation"),
                        "endpoint": row.get("expected_department"),
                    },
                }
            )

    exact_matches = total - len(mismatches)
    score = round(exact_matches / total, 4) if total else 0.0

    return {
        "rows": total,
        "score": score,
        "exact_matches": exact_matches,
        "acuity_accuracy": round(acuity_matches / total, 4) if total else 0.0,
        "recommendation_accuracy": round(recommendation_matches / total, 4) if total else 0.0,
        "endpoint_accuracy": round(endpoint_matches / total, 4) if total else 0.0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:20],
    }
