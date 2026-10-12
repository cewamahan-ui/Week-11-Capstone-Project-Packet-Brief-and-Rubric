"""Corpus ingest for the RAG layer (Week 3 reuse).

Reads the synthetic teaching fixture and turns rows into retrieval
documents. No scraping, no network: the only data source is the
committed ``fixtures/`` files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def load_jsonl(path: str | Path) -> list[dict]:
    """Load a JSONL file, skipping blank lines."""
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> int:
    """Write rows as JSONL (UTF-8, one object per line). Returns count."""
    count = 0
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def build_documents(rows: list[dict]) -> list[dict]:
    """Convert fixture rows into retrieval documents (one per acuity band).

    Documents summarise the teaching protocol per acuity level; they
    contain no individual case data, so nothing patient-like leaves the
    fixture file.
    """
    by_acuity: dict[str, int] = {}
    for row in rows:
        acuity = row.get("expected_urgency", "moderate")
        by_acuity[acuity] = by_acuity.get(acuity, 0) + 1

    docs: list[dict] = []
    for acuity in ("high", "moderate", "low"):
        docs.append(
            {
                "doc_id": f"protocol-{acuity}",
                "title": f"Protocol: {acuity} acuity",
                "content": (
                    f"Acuity band {acuity} covering {by_acuity.get(acuity, 0)} "
                    f"teaching cases. Match symptoms and vitals to this band, "
                    f"then apply the disposition token for the band."
                ),
                "tags": [acuity, "triage-protocol"],
            }
        )
    docs.append(
        {
            "doc_id": "protocol-escalation",
            "title": "Escalation rules",
            "content": (
                "Escalate one band for age 65 and over, age 2 and under, "
                "temperature at or above 39.5, heart rate at or above 120. "
                "Never de-escalate below patient-reported urgency."
            ),
            "tags": ["escalation", "vitals", "age"],
        }
    )
    docs.append(
        {
            "doc_id": "protocol-dispositions",
            "title": "Disposition tokens",
            "content": (
                "immediate_attention for high acuity, within_24_hours for "
                "moderate acuity, routine_follow_up for low acuity. "
                "Cardiology cases route to primary_care review."
            ),
            "tokens": ["immediate_attention", "within_24_hours", "routine_follow_up"],
            "tags": ["disposition"],
        }
    )
    return docs
