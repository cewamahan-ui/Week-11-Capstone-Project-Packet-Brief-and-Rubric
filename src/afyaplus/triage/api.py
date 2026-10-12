"""HTTP API for the triage service (Week 6 reuse).

Endpoints:
- ``GET  /health``  liveness + version + pin summary (no auth)
- ``POST /token``   issue an HMAC-signed bearer token for a demo role
- ``POST /triage``  authenticated assessment (clinician role only)

Free-text notes are redacted before they are echoed or logged, so a
request carrying PII never has that PII leave the process.
"""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from src.afyaplus import __version__
from src.afyaplus.pins import manager as pins_manager
from src.afyaplus.router.deterministic import Router
from src.afyaplus.security.redaction import redact
from src.afyaplus.triage.auth import AuthError, issue_token, require_role, verify_token
from src.afyaplus.triage.domain_twin import DomainTwin
from src.afyaplus.triage.models import TriageRequest, TriageResponse

SERVICE_NAME = "afyaplus-triage"
MODE = "stub"
START_TIME = time.time()

app = FastAPI(
    title="AfyaPlus Triage API",
    version=__version__,
    description="Deterministic triage assessment with stub-mode LLM and MCP layers.",
)

_router = Router()
_twin = DomainTwin()


class TokenBody(BaseModel):
    client_id: str = Field(min_length=1, examples=["demo-clinician"])
    role: str = Field(default="clinician", examples=["clinician"])


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise HTTPException(
            status_code=401,
            detail="malformed authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return value.strip()


def _verified_payload(authorization: str | None) -> dict:
    token = _bearer_token(authorization)
    try:
        return verify_token(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@app.get("/health")
def health() -> dict:
    """Liveness probe with version and pin summary."""
    pins = pins_manager.summary()
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": __version__,
        "mode": MODE,
        "build_sha": pins.get("generated_at", "unpinned"),
        "pins_ok": pins.get("ok", False),
        "uptime_seconds": round(time.time() - START_TIME, 3),
    }


@app.post("/token")
def token(body: TokenBody) -> dict:
    """Issue a bearer token for a demo client id and role."""
    if body.role not in ("clinician", "viewer", "analyst"):
        raise HTTPException(status_code=422, detail="unknown role")
    access_token = issue_token(client_id=body.client_id, role=body.role)
    return {"access_token": access_token, "token_type": "bearer", "role": body.role}


@app.post("/triage", response_model=TriageResponse)
def triage(
    case: TriageRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> TriageResponse:
    """Assess a case; requires a clinician-role bearer token."""
    payload = _verified_payload(authorization)
    try:
        require_role(payload, ("clinician",))
    except AuthError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
    route = _router.route(case)
    assessment = _twin.assess(case)
    redacted_note = redact(case.note) if case.note else ""

    # Log line: identifiers and the redacted note only.
    print(
        f"triage request_id={request_id} sub={payload.get('sub')} "
        f"endpoint={route['endpoint']} acuity={assessment.acuity} "
        f"note={redacted_note!r}",
        flush=True,
    )

    return TriageResponse(
        acuity=assessment.acuity,
        recommendation=assessment.recommendation,
        priority=assessment.priority,
        confidence_score=assessment.confidence_score,
        reasons=assessment.reasons + [f"endpoint={route['endpoint']}"],
        request_id=request_id,
        redacted_note=redacted_note,
    )
