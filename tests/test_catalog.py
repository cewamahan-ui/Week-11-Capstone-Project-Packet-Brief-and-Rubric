"""Catalog tests (Week 10 reuse).

Also enforces the fixture firewall: catalogue rows must never contain
clinical fields, and clinical rows must never contain catalogue rows.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.afyaplus.catalog.service import CatalogService

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def catalog() -> CatalogService:
    return CatalogService()


def test_catalog_fixture_row_count(catalog):
    assert 200 <= len(catalog) <= 500


def test_search_by_category(catalog):
    hits = catalog.search(category="diagnostics")
    assert hits, "diagnostics category must exist"
    for row in hits:
        assert row["category"] == "diagnostics"


def test_search_by_free_text(catalog):
    hits = catalog.search(query="gloves")
    assert hits
    assert all("gloves" in row["item_name"].lower() for row in hits)


def test_search_respects_price_cap(catalog):
    hits = catalog.search(max_price=25.0, limit=50)
    assert hits
    for row in hits:
        assert row["unit_price_usd"] <= 25.0


def test_search_by_county(catalog):
    hits = catalog.search(county="Kisumu")
    assert hits
    for row in hits:
        assert row["county"] == "Kisumu"


def test_get_returns_item_by_id(catalog):
    first = catalog.search(limit=1)[0]
    again = catalog.get(first["item_id"])
    assert again == first
    assert catalog.get("does-not-exist") is None


def test_search_is_deterministic(catalog):
    assert catalog.search(query="test", limit=5) == catalog.search(query="test", limit=5)


def test_catalog_rows_have_no_clinical_fields(catalog):
    clinical = {"symptoms", "age", "vitals", "urgency_level", "expected_urgency"}
    for row in catalog.rows:
        assert not (clinical & set(row)), f"clinical fields leaked: {row['item_id']}"


def test_triage_fixture_has_no_catalog_rows():
    triage = REPO_ROOT / "fixtures" / "triage_messages_sample.jsonl"
    with open(triage, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            assert "item_id" not in row
            assert "unit_price_usd" not in row
