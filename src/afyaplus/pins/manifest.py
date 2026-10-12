"""Pin manifest builder (Week 8 reuse).

Running this module regenerates ``manifest.json`` with:
- the local package content digest (sha256 over the source tree),
- pinned dependency versions resolved from the installed environment
  (their digest fingerprints the ``name==version`` pin line),
- a model pin fingerprinting the triage rule table.

Usage:  python -m src.afyaplus.pins.manifest
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"

PINNED_DEPENDENCIES = ("fastapi", "pydantic", "uvicorn", "httpx", "pytest")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_src_digest() -> str:
    """Content digest over the local source tree (sorted, .py only)."""
    digest = hashlib.sha256()
    for path in sorted(SRC_ROOT.rglob("*.py")):
        rel = path.relative_to(SRC_ROOT).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def pin_digest(name: str, version: str) -> str:
    """Fingerprint of the pin line ``name==version`` (not an artifact hash)."""
    return f"sha256:{sha256_hex(f'{name}=={version}'.encode('utf-8'))}"


def installed_version(distribution: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(distribution)
    except Exception:
        return None


def rule_table_digest() -> str:
    """Fingerprint of the triage rule table that the stub model runs."""
    from src.afyaplus.triage.domain_twin import SYMPTOM_SEVERITY
    from src.afyaplus.triage.models import RECOMMENDATION_TOKENS

    payload = json.dumps(
        {"symptom_severity": SYMPTOM_SEVERITY, "recommendations": RECOMMENDATION_TOKENS},
        sort_keys=True,
    )
    return f"sha256:{sha256_hex(payload.encode('utf-8'))}"


def build_manifest() -> dict:
    from src.afyaplus import __version__

    components = [
        {
            "name": "afyaplus-api",
            "version": __version__,
            "source": "local",
            "digest": compute_src_digest(),
        }
    ]
    for dependency in PINNED_DEPENDENCIES:
        version = installed_version(dependency) or "0.0.0"
        components.append(
            {
                "name": dependency,
                "version": version,
                "source": "pypi",
                "digest": pin_digest(dependency, version),
            }
        )

    from src.afyaplus.triage.domain_twin import DomainTwin

    return {
        "manifest_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "python -m src.afyaplus.pins.manifest",
        "components": components,
        "model_pin": {
            "name": "triage-stub-model",
            "version": DomainTwin().rules_version,
            "backend": "deterministic-stub",
            "digest": rule_table_digest(),
        },
    }


def write_manifest(path: Path = MANIFEST_PATH) -> dict:
    manifest = build_manifest()
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    sys.path.insert(0, str(REPO_ROOT))
    written = write_manifest()
    print(f"wrote {MANIFEST_PATH} ({len(written['components'])} components)")
