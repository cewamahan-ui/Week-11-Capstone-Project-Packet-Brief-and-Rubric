#!/usr/bin/env python3
"""Golden-set evaluation CLI - prints the EVAL SCORE line for CI logs.

    python scripts/eval_score.py

Reads fixtures/triage_messages_sample.jsonl (the committed golden set)
and scores the deterministic pipeline against the gold labels. Stub
mode: zero API calls, zero cost.

What the score means: the gold labels are produced by the same shared
policy module the runtime executes (src/afyaplus.triage.policy), so
this is a regression guard for contract drift between fixture and
runtime - not an independent clinical validation. The pre-fix run
scored 0.6833 on the same 300 rows (see
docs/incidents/2026-10-13-fixture-label-drift.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.afyaplus.evaluation import evaluate  # noqa: E402

FIXTURE = REPO_ROOT / "fixtures" / "triage_messages_sample.jsonl"
PASS_THRESHOLD = 0.90


def main() -> int:
    with open(FIXTURE, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

    metrics = evaluate(rows)

    print(f"EVAL SCORE: {metrics['score']:.4f}")
    print(f"rows={metrics['rows']} exact={metrics['exact_matches']} mismatches={metrics['mismatch_count']}")
    print(f"acuity_accuracy={metrics['acuity_accuracy']}")
    print(f"recommendation_accuracy={metrics['recommendation_accuracy']}")
    print(f"endpoint_accuracy={metrics['endpoint_accuracy']}")
    if metrics["mismatches"]:
        print("sample mismatches:")
        for item in metrics["mismatches"][:5]:
            print(f"  {item}")

    if metrics["score"] < PASS_THRESHOLD:
        print(f"FAIL: score {metrics['score']} below threshold {PASS_THRESHOLD}")
        return 1
    print(f"PASS: score {metrics['score']} >= threshold {PASS_THRESHOLD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
