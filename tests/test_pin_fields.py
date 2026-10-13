"""Pin-fields tests (Week 8 reuse).

Every component in the manifest must carry the required pin fields,
be pinned to exact semver, and - for the local package - match the
digest of the current source tree. The requirements file and the
manifest must agree, so a bumped dependency cannot go unnoticed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.afyaplus import __version__
from src.afyaplus.pins import manager
from src.afyaplus.pins.manifest import MANIFEST_PATH, compute_src_digest

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = REPO_ROOT / "requirements.txt"

pytestmark = pytest.mark.unit


class TestPinFields:
    """Manifest shape, pin format and consistency checks."""

    def test_manifest_file_exists(self):
        assert MANIFEST_PATH.exists(), "pins/manifest.json must be committed"

    def test_every_component_has_required_fields(self):
        manifest = manager.load()
        components = manifest["components"]
        assert components, "manifest must pin at least the local package"
        for component in components:
            for field in manager.REQUIRED_FIELDS:
                assert component.get(field), f"{component.get('name')}: missing {field}"

    def test_versions_are_exact_semver(self):
        from src.afyaplus.pins.manifest import SEMVER_RE

        for component in manager.load()["components"]:
            assert SEMVER_RE.match(component["version"]), (
                f"{component['name']} version {component['version']} is not exact semver"
            )

    def test_digests_are_sha256_fingerprints(self):
        for component in manager.load()["components"]:
            digest = component["digest"]
            assert digest.startswith("sha256:")
            assert len(digest) == len("sha256:") + 64

    def test_local_package_pin_matches_current_source(self):
        local = manager.get("afyaplus-api")
        assert local is not None
        assert local["version"] == __version__
        assert local["digest"] == compute_src_digest(), (
            "source changed after the pin was taken - regenerate with "
            "python -m src.afyaplus.pins.manifest"
        )

    def test_model_pin_present_and_pinned(self):
        manifest = manager.load()
        model_pin = manifest["model_pin"]
        assert model_pin["backend"] == "deterministic-stub"
        assert model_pin["version"].startswith("twin-rules-")
        assert model_pin["digest"].startswith("sha256:")

    def test_manifest_and_requirements_agree(self):
        pinned = {}
        for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "==" in line:
                name, version = line.split("==")
                pinned[name.strip().lower()] = version.strip()

        for component in manager.load()["components"]:
            name = component["name"].lower()
            if name == "afyaplus-api":
                continue
            assert name in pinned, f"{component['name']} missing from requirements.txt"
            assert pinned[name] == component["version"], (
                f"{component['name']}: requirements pins {pinned[name]}, "
                f"manifest pins {component['version']}"
            )

    def test_verify_reports_no_problems(self):
        problems = manager.verify()
        assert problems == []

    def test_verify_detects_a_tampered_manifest(self):
        manifest = manager.load()
        broken = dict(manifest)
        broken["components"] = [
            dict(component) for component in manifest["components"]
        ]
        broken["components"][0]["digest"] = "sha256:deadbeef"
        problems = manager.verify(broken)
        assert any("does not match the current tree" in p for p in problems)
