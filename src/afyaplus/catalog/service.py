"""Catalog search over the marketplace fixture (Week 10 reuse).

Marketplace listings only: item names, suppliers, counties, prices.
This fixture line is deliberately kept apart from the clinical triage
fixture so marketplace rows never contain patient data and clinical
rows never contain catalogue data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.afyaplus.rag.ingest import load_jsonl

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "catalog_listings_sample.jsonl"


class CatalogService:
    """Read-only search over the committed catalogue fixture."""

    def __init__(self, path: str | Path = DEFAULT_CATALOG_PATH) -> None:
        self.path = Path(path)
        self.rows: list[dict] = load_jsonl(self.path) if self.path.exists() else []

    def __len__(self) -> int:
        return len(self.rows)

    def get(self, item_id: str) -> Optional[dict]:
        for row in self.rows:
            if row.get("item_id") == item_id:
                return row
        return None

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        county: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Filter listings by free text, category, county and price cap."""
        needle = str(query).strip().lower() if query else ""
        results: list[dict] = []
        for row in self.rows:
            if category and str(row.get("category", "")).lower() != str(category).lower():
                continue
            if county and str(row.get("county", "")).lower() != str(county).lower():
                continue
            if max_price is not None and float(row.get("unit_price_usd", 0)) > float(max_price):
                continue
            if needle:
                haystack = f"{row.get('item_name', '')} {row.get('supplier', '')}".lower()
                if needle not in haystack:
                    continue
            results.append(row)
            if len(results) >= limit:
                break
        return results
