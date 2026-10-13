"""Pin manifest verification (Week 8 reuse).

``verify`` is what ``tests/test_pin_fields.py`` runs: every component
must carry name / version / source / digest, versions must be pinned
semver, digests must be well formed, and the local package digest must
match the current source tree (i.e. the pin was taken after the last
code change).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.afyaplus.pins.manifest import MANIFEST_PATH, SEMVER_RE, compute_src_digest

REQUIRED_FIELDS = ("name", "version", "source", "digest")
LOCAL_COMPONENT = "afyaplus-api"


def load(path: str | Path = MANIFEST_PATH) -> dict:
    """Load the manifest; a missing file yields an empty manifest."""
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get(component_name: str, manifest: Optional[dict] = None) -> Optional[dict]:
    data = manifest if manifest is not None else load()
    for component in data.get("components", []):
        if component.get("name") == component_name:
            return component
    return None


def verify(manifest: Optional[dict] = None) -> list[str]:
    """Return a list of problems; empty list means the manifest is sound."""
    data = manifest if manifest is not None else load()
    problems: list[str] = []

    if not data:
        return ["manifest missing or empty"]

    if not data.get("manifest_version"):
        problems.append("manifest_version missing")

    for component in data.get("components", []):
        name = component.get("name", "<unnamed>")
        for field in REQUIRED_FIELDS:
            if not component.get(field):
                problems.append(f"{name}: missing field '{field}'")
        version = str(component.get("version", ""))
        if version and not SEMVER_RE.match(version):
            problems.append(f"{name}: version '{version}' is not pinned semver")
        digest = str(component.get("digest", ""))
        if digest and not (
            digest.startswith("sha256:") and len(digest) == 7 + 64
        ):
            problems.append(f"{name}: digest '{digest}' is not a sha256 fingerprint")

    local = get(LOCAL_COMPONENT, data)
    if local and local.get("digest") and local["digest"] != compute_src_digest():
        problems.append(
            "afyaplus-api: source digest does not match the current tree "
            "(regenerate with python -m src.afyaplus.pins.manifest)"
        )

    model_pin = data.get("model_pin") or {}
    for field in ("name", "version", "backend", "digest"):
        if not model_pin.get(field):
            problems.append(f"model_pin: missing field '{field}'")

    return problems


def summary() -> dict:
    """Compact pin summary used by /health and the demo pipeline."""
    data = load()
    return {
        "components": len(data.get("components", [])),
        "manifest_version": data.get("manifest_version", "none"),
        "generated_at": data.get("generated_at", "never"),
        "model_pin": (data.get("model_pin") or {}).get("version", "none"),
        "ok": not verify(data),
    }
