"""Week 9 security smoke, adapted for the capstone.

Covers the compliance checklist the demo claims:
- real PII redaction (unit level and through the HTTP API),
- no committed secrets (whole-repo pattern scan),
- no live patient rows in either fixture line (fixture scan),
- tampered or unsigned tokens rejected.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.afyaplus.security.redaction import contains_pii, redact, redact_value
from src.afyaplus.triage.api import app
from src.afyaplus.triage.auth import AuthError, issue_token, verify_token

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.security

SAMPLE_NOTE = (
    "Follow up with Jane Otieno on 0712345678 or jane.otieno@example.com; "
    "national ID 34817291, DOB 1985-06-21, card 4111 1111 1111 1111."
)

SCAN_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".sh", ".txt", ".ini", ".cfg", ".jsonl"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "venv", ".venv"}

# Built at runtime so this file does not contain the raw needles.
SECRET_NEEDLES = [
    r"\bsk-[A-Za-z0-9]{16,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bghp_[A-Za-z0-9]{36}\b",
    "-" * 5 + "BEGIN [A-Z ]*PRIVATE KEY",
]


def repo_text_files():
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if SKIP_DIRS & set(path.parts):
            continue
        yield path


class TestRedaction:
    """Real redaction checks (not a mock)."""

    def test_redaction_masks_every_identifier(self):
        assert contains_pii(SAMPLE_NOTE) is True
        redacted = redact(SAMPLE_NOTE)

        assert "jane.otieno@example.com" not in redacted
        assert "0712345678" not in redacted
        assert "34817291" not in redacted
        assert "1985-06-21" not in redacted
        assert "4111 1111 1111 1111" not in redacted

        assert "[EMAIL]" in redacted
        assert "[PHONE]" in redacted
        assert "[ID]" in redacted
        assert "[DOB]" in redacted
        assert "[CARD]" in redacted
        assert contains_pii(redacted) is False

    def test_redaction_preserves_clinical_content(self):
        redacted = redact(SAMPLE_NOTE)
        assert "follow up" in redacted.lower()

    def test_redact_value_walks_nested_structures(self):
        payload = {"case": {"note": SAMPLE_NOTE, "tags": ["fever", SAMPLE_NOTE]}}
        clean = redact_value(payload)
        assert contains_pii(clean["case"]["note"]) is False
        assert contains_pii(clean["case"]["tags"][1]) is False
        assert clean["case"]["tags"][0] == "fever"

    def test_pii_redaction_integration(self):
        """End to end: PII in the request must never leave the process."""
        client = TestClient(app)
        token = issue_token("security-smoke", role="clinician")
        response = client.post(
            "/triage",
            json={
                "symptoms": ["fever", "cough"],
                "age": 31,
                "urgency_level": "moderate",
                "note": SAMPLE_NOTE,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.text
        assert "jane.otieno@example.com" not in body
        assert "0712345678" not in body
        assert "34817291" not in body
        assert "[EMAIL]" in body
        assert response.json()["redacted_note"] == redact(SAMPLE_NOTE)


class TestRepoHygiene:
    """No secrets committed, no patient rows in fixtures."""

    def test_no_secrets_committed(self):
        import re

        offenders = []
        for path in repo_text_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in SECRET_NEEDLES:
                if re.search(needle, text):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {needle}")
        assert offenders == [], f"possible secrets found: {offenders}"

    def test_no_env_file_committed(self):
        assert not (REPO_ROOT / ".env").exists(), ".env must never be committed"
        for path in REPO_ROOT.rglob(".env"):
            assert SKIP_DIRS & set(path.parts), f"unexpected env file: {path}"

    def test_fixture_contains_no_direct_identifiers(self):
        fixtures_dir = REPO_ROOT / "fixtures"
        for path in fixtures_dir.glob("*.jsonl"):
            text = path.read_text(encoding="utf-8")
            assert contains_pii(text) is False, f"{path.name} contains PII patterns"

    def test_fixture_rows_carry_no_identifier_fields(self):
        import json

        forbidden = {
            "name", "patient_name", "email", "phone", "national_id",
            "id_number", "address", "dob", "date_of_birth", "nhs_number",
        }
        triage = REPO_ROOT / "fixtures" / "triage_messages_sample.jsonl"
        with open(triage, encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                assert not (forbidden & set(row)), (
                    f"identifier fields in fixture row: {sorted(forbidden & set(row))}"
                )

    def test_catalog_fixture_has_no_clinical_fields(self):
        import json

        clinical = {"symptoms", "age", "vitals", "urgency_level", "expected_urgency"}
        catalog = REPO_ROOT / "fixtures" / "catalog_listings_sample.jsonl"
        with open(catalog, encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                assert not (clinical & set(row)), (
                    f"clinical fields in catalog row: {sorted(clinical & set(row))}"
                )


class TestTokenIntegrity:
    """Week 9 token hygiene."""

    def test_valid_token_roundtrip(self):
        token = issue_token("alice", role="clinician")
        payload = verify_token(token)
        assert payload["sub"] == "alice"
        assert payload["role"] == "clinician"

    def test_tampered_token_rejected(self):
        token = issue_token("alice", role="clinician")
        head, body, sig = token.split(".")
        tampered = f"{head}.{body}.{'A' * len(sig)}"
        with pytest.raises(AuthError):
            verify_token(tampered)

    def test_payload_swap_rejected(self):
        token_a = issue_token("alice", role="viewer")
        token_b = issue_token("bob", role="clinician")
        head_a, body_a, sig_a = token_a.split(".")
        _head_b, body_b, _sig_b = token_b.split(".")
        # Splice bob's payload onto alice's signature - must not verify.
        with pytest.raises(AuthError):
            verify_token(f"{head_a}.{body_b}.{sig_a}")

    def test_unsigned_token_rejected(self):
        token = issue_token("alice", role="clinician")
        with pytest.raises(AuthError):
            verify_token(token.rsplit(".", 1)[0])
        with pytest.raises(AuthError):
            verify_token("not-a-token")

    def test_expired_token_rejected(self):
        token = issue_token("alice", role="clinician", ttl_seconds=1)
        with pytest.raises(AuthError):
            verify_token(token, now=10**10)
