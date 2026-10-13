"""RAG tests (Weeks 1-5 reuse): ingest + deterministic retrieval."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.afyaplus.rag.ingest import build_documents, load_jsonl
from src.afyaplus.rag.retriever import RAGRetriever

REPO_ROOT = Path(__file__).resolve().parents[1]
TRIAGE_FIXTURE = REPO_ROOT / "fixtures" / "triage_messages_sample.jsonl"

pytestmark = pytest.mark.unit


def test_ingest_loads_teaching_fixture():
    rows = load_jsonl(TRIAGE_FIXTURE)
    assert 200 <= len(rows) <= 500
    assert all("id" in row and "symptoms" in row for row in rows)


def test_ingest_builds_protocol_documents():
    rows = load_jsonl(TRIAGE_FIXTURE)
    docs = build_documents(rows)
    assert len(docs) >= 4
    assert all(doc.get("content") for doc in docs)
    acuity_levels = {row["expected_urgency"] for row in rows}
    for acuity in acuity_levels:
        assert any(acuity in doc["title"] for doc in docs), f"missing protocol doc for {acuity}"


def test_retriever_returns_content_for_any_query():
    retriever = RAGRetriever()
    results = retriever.search("completely unrelated query")
    assert results
    assert all("content" in doc for doc in results)


def test_retriever_ranks_relevant_document_first():
    retriever = RAGRetriever()
    results = retriever.search("cardiology chest pain ECG review")
    assert results[0]["doc_id"] == "guideline-cardiology"
    assert results[0]["score"] > 0


def test_retriever_is_deterministic():
    retriever = RAGRetriever()
    first = [doc["doc_id"] for doc in retriever.search("fever sepsis red flags")]
    second = [doc["doc_id"] for doc in retriever.search("fever sepsis red flags")]
    assert first == second


def test_retriever_attaches_context():
    retriever = RAGRetriever()
    results = retriever.search("review pathway", context={"department": "cardiology"})
    assert results
    assert all(doc["context"] == {"department": "cardiology"} for doc in results)
