"""End-to-end entry point for the capstone.

    python -m src.afyaplus.main            # full stub pipeline + eval score
    python -m src.afyaplus.main run --rows 3
    python -m src.afyaplus.main serve      # start the HTTP API

Everything runs locally: no network calls, no API spend. The run
prints each layer's evidence (pins, redaction, auth, RAG, triage,
MCP tool, cost ledger, eval score) so the transcript can be captured
as demo evidence.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.afyaplus import __version__
from src.afyaplus.catalog.service import CatalogService
from src.afyaplus.evaluation import evaluate
from src.afyaplus.mcp.cost_tracker import CostTracker
from src.afyaplus.mcp.tools import MCPTools
from src.afyaplus.pins import manager as pins_manager
from src.afyaplus.rag.ingest import build_documents, load_jsonl
from src.afyaplus.rag.retriever import RAGRetriever
from src.afyaplus.router.deterministic import Router
from src.afyaplus.security.redaction import contains_pii, redact
from src.afyaplus.triage.auth import AuthError, issue_token, verify_token
from src.afyaplus.triage.domain_twin import DomainTwin
from src.afyaplus.triage.models import TriageRequest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "fixtures" / "triage_messages_sample.jsonl"

SAMPLE_NOTE = (
    "Callback for Jane Otieno on 0712345678 or jane.otieno@example.com, "
    "ID 34817291, DOB 1985-06-21."
)

SAMPLE_CASES = [
    {"symptoms": ["chest_pain"], "age": 58, "urgency_level": "high", "vitals": {}},
    {"symptoms": ["fever", "cough"], "age": 27, "urgency_level": "moderate",
     "vitals": {"temperature": 38.8, "heart_rate": 98}},
    {"symptoms": ["routine_checkup"], "age": 40, "urgency_level": "low", "vitals": {}},
]


def _step(title: str) -> None:
    print(f"\n== {title} ==")


def run_pipeline(rows_shown: int = 3) -> int:
    """Execute every layer in stub mode; returns a process exit code."""
    print("AfyaPlus Module 4 Capstone - end-to-end run (stub mode)")
    print(f"version: {__version__}")

    _step("1. pins")
    pin_problems = pins_manager.verify()
    pin_summary = pins_manager.summary()
    print(f"components: {pin_summary['components']}  ok: {pin_summary['ok']}")
    print(f"problems: {pin_problems if pin_problems else 'none'}")

    _step("2. security / redaction")
    redacted = redact(SAMPLE_NOTE)
    print(f"raw    : {SAMPLE_NOTE}")
    print(f"redacted: {redacted}")
    print(f"contains_pii(raw)={contains_pii(SAMPLE_NOTE)}  contains_pii(redacted)={contains_pii(redacted)}")

    _step("3. auth")
    token = issue_token("demo-clinician", role="clinician")
    payload = verify_token(token)
    tampered = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    try:
        verify_token(tampered)
        tamper_result = "ACCEPTED (unexpected)"
    except AuthError as exc:
        tamper_result = f"rejected ({exc})"
    print(f"issued for sub={payload['sub']} role={payload['role']}")
    print(f"tampered token: {tamper_result}")

    _step("4. RAG")
    fixture_rows = load_jsonl(FIXTURE_PATH)
    corpus = build_documents(fixture_rows)
    retriever = RAGRetriever()
    results = retriever.search("fever confusion chest pain", top_k=3)
    print(f"fixture rows ingested: {len(fixture_rows)}  protocol docs built: {len(corpus)}")
    for item in results:
        print(f"  {item['doc_id']}  score={item['score']}  {item['title']}")

    _step("5. triage (router + domain twin)")
    router = Router()
    twin = DomainTwin()
    for case_data in SAMPLE_CASES[: max(rows_shown, 1)]:
        case = TriageRequest(**case_data)
        route = router.route(case)
        assessment = twin.assess(case)
        print(
            f"  {case.symptoms} age={case.age} -> {route['endpoint']:<18} "
            f"acuity={assessment.acuity:<8} {assessment.recommendation} "
            f"p={assessment.priority} conf={assessment.confidence_score}"
        )

    _step("6. MCP tool (stub fallback)")
    tools = MCPTools()
    mcp_result = tools.execute("find_clinic_by_county", {"county": "Kisumu"})
    print(f"status={mcp_result['status']}  reason={mcp_result['reason']}")
    print(f"clinics: {len(mcp_result['data'].get('clinics', []))}")

    _step("7. catalog search (marketplace fixture, no clinical data)")
    catalog = CatalogService()
    hits = catalog.search(query="gloves", limit=5)
    print(f"catalog rows: {len(catalog)}  'gloves' hits: {len(hits)}")

    _step("8. cost ledger")
    ledger = CostTracker()
    ledger.record("golden-set eval", api_calls=0, cost_usd=0.0)
    ledger.record("mcp stub call", api_calls=0, cost_usd=0.0)
    ledger.record("http demo calls", api_calls=0, cost_usd=0.0)
    print(f"summary: {ledger.summary()}")

    _step("9. golden-set evaluation")
    metrics = evaluate(fixture_rows)
    print(f"EVAL SCORE: {metrics['score']:.4f}  ({metrics['exact_matches']}/{metrics['rows']} rows exact)")
    print(
        f"acuity_accuracy={metrics['acuity_accuracy']}  "
        f"recommendation_accuracy={metrics['recommendation_accuracy']}  "
        f"endpoint_accuracy={metrics['endpoint_accuracy']}"
    )
    print(f"mismatches: {metrics['mismatch_count']}")

    failed = bool(pin_problems) or metrics["score"] < 0.90
    _step("result")
    print("RUN COMPLETE" + (" (with findings above)" if failed else ""))
    print("mode=stub  api_calls=0  spend=$0.00")
    return 1 if failed else 0


def serve(host: str, port: int) -> int:
    """Start the HTTP API with uvicorn."""
    import uvicorn

    from src.afyaplus.triage.api import app

    print(f"AfyaPlus triage API on http://{host}:{port}  (mode=stub)")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="afyaplus", description="AfyaPlus capstone runner")
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="run the full stub pipeline (default)")
    run_parser.add_argument("--rows", type=int, default=3)

    serve_parser = sub.add_parser("serve", help="start the HTTP API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve(args.host, args.port)
    if args.command == "run":
        return run_pipeline(args.rows)
    return run_pipeline()


if __name__ == "__main__":
    sys.exit(main())
