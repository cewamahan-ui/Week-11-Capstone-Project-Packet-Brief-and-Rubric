"""Integration tests for the HTTP API (run with: pytest -m integration).

Uses FastAPI's TestClient - in-process, no sockets, no external
services, which is what makes the integration tier runnable in CI
without secrets.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.afyaplus import __version__
from src.afyaplus.security.redaction import redact
from src.afyaplus.triage.api import app
from src.afyaplus.triage.auth import issue_token

pytestmark = pytest.mark.integration

CASE = {"symptoms": ["fever", "cough"], "age": 27, "urgency_level": "moderate"}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def clinician_token() -> str:
    return issue_token("integration-test", role="clinician")


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestHealth:
    def test_health_is_public_and_reports_stub_mode(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "afyaplus-triage"
        assert body["version"] == __version__
        assert body["mode"] == "stub"
        assert isinstance(body["uptime_seconds"], (int, float))


class TestTokenEndpoint:
    def test_issues_bearer_token_for_clinician(self, client):
        response = client.post("/token", json={"client_id": "clinic-a", "role": "clinician"})
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"].count(".") == 2

    def test_rejects_unknown_role(self, client):
        response = client.post("/token", json={"client_id": "clinic-a", "role": "wizard"})
        assert response.status_code == 422

    def test_rejects_missing_client_id(self, client):
        response = client.post("/token", json={"role": "clinician"})
        assert response.status_code == 422


class TestTriageAuth:
    def test_missing_token_returns_401(self, client):
        response = client.post("/triage", json=CASE)
        assert response.status_code == 401
        assert response.headers.get("www-authenticate") == "Bearer"

    def test_garbage_token_returns_401(self, client):
        response = client.post("/triage", json=CASE, headers=_auth("not.a.token"))
        assert response.status_code == 401

    def test_viewer_role_returns_403(self, client):
        token = issue_token("viewer-1", role="viewer")
        response = client.post("/triage", json=CASE, headers=_auth(token))
        assert response.status_code == 403


class TestTriageEndpoint:
    def test_clinician_gets_deterministic_assessment(self, client, clinician_token):
        first = client.post("/triage", json=CASE, headers=_auth(clinician_token))
        second = client.post("/triage", json=CASE, headers=_auth(clinician_token))
        assert first.status_code == 200
        assert second.status_code == 200

        body = first.json()
        assert body["acuity"] in ("low", "moderate", "high")
        assert body["recommendation"] in (
            "immediate_attention",
            "within_24_hours",
            "routine_follow_up",
        )
        assert 1 <= body["priority"] <= 4
        assert body["confidence_score"] > 0
        assert body["request_id"]
        assert any(r.startswith("endpoint=") for r in body["reasons"])

        for field in ("acuity", "recommendation", "priority", "confidence_score"):
            assert second.json()[field] == body[field]

    def test_invalid_age_returns_422(self, client, clinician_token):
        bad = dict(CASE, age=-3)
        response = client.post("/triage", json=bad, headers=_auth(clinician_token))
        assert response.status_code == 422

    def test_empty_symptoms_returns_422(self, client, clinician_token):
        bad = dict(CASE, symptoms=[])
        response = client.post("/triage", json=bad, headers=_auth(clinician_token))
        assert response.status_code == 422

    def test_unknown_acuity_returns_422(self, client, clinician_token):
        bad = dict(CASE, urgency_level="critical")
        response = client.post("/triage", json=bad, headers=_auth(clinician_token))
        assert response.status_code == 422

    def test_note_is_redacted_before_echo(self, client, clinician_token):
        note = "Call 0712345678 or jane.otieno@example.com about the fever"
        response = client.post(
            "/triage",
            json=dict(CASE, note=note),
            headers=_auth(clinician_token),
        )
        assert response.status_code == 200
        assert "0712345678" not in response.text
        assert "jane.otieno@example.com" not in response.text
        assert response.json()["redacted_note"] == redact(note)
