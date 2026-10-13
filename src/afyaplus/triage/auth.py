"""Token auth for the triage API (Week 6 reuse, HMAC-signed, stdlib only).

Tokens are HMAC-SHA256 signed, compact JWT-style strings
(``base64url(header).base64url(payload).signature``). There is no
external identity provider: the demo secret comes from the
``AFYA_TOKEN_SECRET`` environment variable and falls back to a
clearly-labelled local placeholder so the stub path runs anywhere.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

DEFAULT_SECRET = "local-demo-secret-change-me"
TOKEN_TTL_SECONDS = 3600
VALID_ROLES = ("clinician", "viewer", "analyst")


class AuthError(Exception):
    """Raised when a token fails verification."""


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def get_secret() -> str:
    """Resolve the signing secret (env first, dev placeholder second)."""
    return os.environ.get("AFYA_TOKEN_SECRET", DEFAULT_SECRET)


def _sign(signing_input: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256)
    return _b64encode(digest.digest())


def issue_token(
    client_id: str,
    role: str = "clinician",
    secret: Optional[str] = None,
    ttl_seconds: int = TOKEN_TTL_SECONDS,
) -> str:
    """Issue a signed token for a named client and role."""
    if role not in VALID_ROLES:
        raise ValueError(f"unknown role: {role}")
    if not client_id or not client_id.strip():
        raise ValueError("client_id is required")

    header = {"alg": "HS256", "typ": "AFYA"}
    payload = {
        "sub": client_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + int(ttl_seconds),
    }
    signing_input = f"{_b64encode(json.dumps(header, separators=(',', ':')).encode())}." \
                    f"{_b64encode(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = _sign(signing_input, secret or get_secret())
    return f"{signing_input}.{signature}"


def verify_token(token: str, secret: Optional[str] = None, now: Optional[int] = None) -> dict:
    """Verify signature and expiry; return the payload or raise AuthError."""
    if not token or token.count(".") != 2:
        raise AuthError("malformed token")

    header_part, payload_part, signature = token.split(".")
    signing_input = f"{header_part}.{payload_part}"
    expected = _sign(signing_input, secret or get_secret())

    if not hmac.compare_digest(signature, expected):
        raise AuthError("signature mismatch")

    try:
        payload = json.loads(_b64decode(payload_part))
    except Exception as exc:  # pragma: no cover - defensive
        raise AuthError(f"unreadable payload: {exc}") from exc

    current = int(time.time()) if now is None else now
    if int(payload.get("exp", 0)) < current:
        raise AuthError("token expired")
    if payload.get("role") not in VALID_ROLES:
        raise AuthError("unknown role in token")
    return payload


def require_role(payload: dict, allowed: tuple[str, ...]) -> None:
    """Raise AuthError unless the verified payload carries an allowed role."""
    if payload.get("role") not in allowed:
        raise AuthError(f"role '{payload.get('role')}' is not permitted")
