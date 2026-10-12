"""Deterministic retriever (Weeks 1-5 reuse, stub backend).

Scoring is token overlap over a fixed corpus, sorted stably so the
same query always returns the same documents. With no query matches
the retriever still returns the corpus head - callers (and the tests)
always get at least one document with a ``content`` field.
"""

from __future__ import annotations

import re
from typing import Optional

_TOKEN_RE = re.compile(r"[a-z0-9_]+")

DEFAULT_CORPUS: list[dict] = [
    {
        "doc_id": "guideline-sepsis",
        "title": "Sepsis red flags",
        "content": (
            "Fever with confusion or low heart-rate variability requires "
            "immediate_attention. Escalate to emergency_department."
        ),
        "tags": ["fever", "confusion", "emergency"],
    },
    {
        "doc_id": "guideline-cardiology",
        "title": "Cardiology review pathway",
        "content": (
            "Chest discomfort in adults over 45 routes to cardiology review "
            "within 24 hours after ECG. Cardiology cases need primary_care "
            "follow-up booking."
        ),
        "tags": ["cardiology", "chest_pain", "review"],
    },
    {
        "doc_id": "guideline-minor-injuries",
        "title": "Minor injury routing",
        "content": (
            "Cuts and abrasions without bleeding risk route to "
            "emergency_department for wound assessment, then discharge."
        ),
        "tags": ["minor_cut", "wound", "emergency"],
    },
    {
        "doc_id": "guideline-routine",
        "title": "Routine and preventive visits",
        "content": (
            "Routine_checkup, prescription_refill and follow_up cases route "
            "to general_practice and are low acuity unless vitals escalate."
        ),
        "tags": ["routine", "general_practice"],
    },
    {
        "doc_id": "guideline-cost",
        "title": "Cost and token discipline",
        "content": (
            "Automated tests and golden-set evaluation run in stub mode with "
            "zero API spend. Live calls are reserved for the Thursday demo "
            "and must stay within the declared one dollar budget."
        ),
        "tags": ["cost", "stub", "budget"],
    },
]


def _tokenise(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class RAGRetriever:
    """Small in-memory retriever over an explicit corpus."""

    def __init__(self, corpus: Optional[list[dict]] = None) -> None:
        self.corpus = list(DEFAULT_CORPUS if corpus is None else corpus)

    def search(self, query: str, context: Optional[dict] = None, top_k: int = 3) -> list[dict]:
        """Return up to ``top_k`` documents ranked by token overlap."""
        query_tokens = set(_tokenise(str(query)))
        ranked: list[tuple[int, str, dict]] = []
        for idx, doc in enumerate(self.corpus):
            doc_tokens = set(_tokenise(str(doc.get("content", ""))))
            doc_tokens.update(str(tag).lower() for tag in doc.get("tags", []))
            score = len(query_tokens & doc_tokens)
            ranked.append((score, doc.get("doc_id", f"doc-{idx:03d}"), doc))

        ranked.sort(key=lambda item: (-item[0], item[1]))
        results: list[dict] = []
        for score, _doc_id, doc in ranked[: max(top_k, 1)]:
            entry = dict(doc)
            entry["score"] = score
            entry["context"] = dict(context) if context else {}
            results.append(entry)
        return results
