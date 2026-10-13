#!/usr/bin/env python3
"""Measure the stub path and write perf_stub.json (Deliverable 2).

    python scripts/measure_perf.py

Everything measured here runs in-process with no network calls, so
the numbers describe the deterministic stub path the tests and the
demo rely on. Each case is warmed up first; percentiles are taken
over the measured iterations only.
"""

from __future__ import annotations

import contextlib
import io
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.afyaplus.mcp.tools import MCPTools  # noqa: E402
from src.afyaplus.rag.retriever import RAGRetriever  # noqa: E402
from src.afyaplus.router.deterministic import Router  # noqa: E402
from src.afyaplus.security.redaction import redact  # noqa: E402
from src.afyaplus.triage.domain_twin import DomainTwin  # noqa: E402
from src.afyaplus.triage.models import TriageRequest  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "perf_stub.json"
ITERATIONS = 300
WARMUP = 20

CASE = TriageRequest(
    symptoms=["fever", "cough"],
    age=68,
    urgency_level="moderate",
    vitals={"temperature": 38.9, "heart_rate": 104},
)
PII_NOTE = (
    "Reach Jane Otieno on 0712345678 or jane.otieno@example.com, ID 34817291."
)


def measure(label: str, func, iterations: int = ITERATIONS) -> dict:
    """Run func with warmup, then collect per-call milliseconds."""
    for _ in range(WARMUP):
        func()

    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        samples.append((time.perf_counter() - start) * 1000.0)

    samples.sort()
    return {
        "case": label,
        "iterations": iterations,
        "mean_ms": round(statistics.fmean(samples), 4),
        "p50_ms": round(statistics.median(samples), 4),
        "p95_ms": round(samples[int(len(samples) * 0.95) - 1], 4),
        "max_ms": round(samples[-1], 4),
    }


def main() -> int:
    router = Router()
    twin = DomainTwin()
    retriever = RAGRetriever()
    tools = MCPTools()

    cases = [
        measure("router.route", lambda: router.route(CASE)),
        measure("domain_twin.assess", lambda: twin.assess(CASE)),
        measure("rag_retriever.search", lambda: retriever.search("fever cardiology review")),
        measure("mcp_tool.execute_stub", lambda: tools.execute("find_clinic_by_county", {"county": "Kisumu"})),
        measure("security.redact", lambda: redact(PII_NOTE)),
    ]

    def http_triage():
        # The API logs one line per request; keep the measurement output clean.
        with contextlib.redirect_stdout(io.StringIO()):
            client.post(
                "/triage",
                json={"symptoms": ["fever", "cough"], "age": 68, "urgency_level": "moderate"},
                headers={"Authorization": f"Bearer {perf_token}"},
            )

    from fastapi.testclient import TestClient

    from src.afyaplus.triage.api import app
    from src.afyaplus.triage.auth import issue_token

    client = TestClient(app)
    perf_token = issue_token("perf", role="clinician")
    cases.append(measure("http_post_triage_inprocess", http_triage, iterations=100))

    result = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/measure_perf.py",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "mode": "stub (no network)",
        },
        "warmup_iterations": WARMUP,
        "cases": cases,
        "notes": (
            "Measured locally on the stub path; no LLM or MCP server involved. "
            "The http case uses FastAPI's in-process TestClient, so it includes "
            "framework overhead but no socket latency."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"{'case':<32}{'p50 ms':>10}{'p95 ms':>10}{'mean ms':>10}{'max ms':>10}")
    for case in cases:
        print(
            f"{case['case']:<32}"
            f"{case['p50_ms']:>10.3f}{case['p95_ms']:>10.3f}"
            f"{case['mean_ms']:>10.3f}{case['max_ms']:>10.3f}"
        )
    print(f"\nwrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
