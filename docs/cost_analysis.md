# Cost analysis

Week 11 stays at zero. Everything the tests, eval, perf harness and
demo actually run is local and deterministic; the ~$1 live-call
allowance for Thursday was **declared but not spent** (fallback taken:
no live LLM key, stub mode).

## What was actually executed (measured)

| Step | How it ran | API calls | Cost |
|------|-----------|-----------|------|
| Unit + security + golden tests (55 tests) | `pytest -q` | 0 | $0.00 |
| Integration tests (12 tests) | `pytest -m integration` | 0 | $0.00 |
| Golden-set eval, 300 rows | `python scripts/eval_score.py` | 0 | $0.00 |
| Perf measurement, ~1,400 iterations | `python scripts/measure_perf.py` | 0 | $0.00 |
| End-to-end pipeline run | `python -m src.afyaplus.main` | 0 | $0.00 |
| Demo API calls (health/token/triage over loopback) | `curl` transcript | 0 | $0.00 |
| Fixture regeneration (seeded, offline) | `python scripts/make_fixtures.py` | 0 | $0.00 |
| **Total actually spent** | | **0** | **$0.00** |

Evidence: `docs/evidence/perf_measurement.txt`,
`docs/evidence/eval_score.txt`, `docs/evidence/api_transcript.txt`,
and the cost ledger printed by the pipeline run
(`docs/evidence/end_to_end_run.txt`).

## Budget declared for the packet

| Step | Approx. API calls | Approx. cost | Status |
|------|-------------------|--------------|--------|
| Unit pytest and stubs | 0 | $0 | executed |
| Golden-set eval (stub) | 0 | $0 | executed |
| Thursday live demo | ~10 | ~$1 | **not taken - stub demo** |
| Typical capstone total | 0 | **$0.00** | under the $1 ceiling |

## Teaching table: what live calls would cost if wired later

Illustrative only - these are the unit prices used in the Week 7 cost
exercises, not invoices. The live path is not wired in this build.

| Model class (teaching figures) | Input / 1M tokens | Output / 1M tokens | Demo run (~10 calls, ~4k in / ~1k out) |
|--------------------------------|-------------------|--------------------|-----------------------------------------|
| Small chat (stub substitute) | $0.15 | $0.60 | ~$0.001 |
| Mid chat | $1.00 | $4.00 | ~$0.008 |
| Large chat | $5.00 | $15.00 | ~$0.035 |

So even the largest class stays far below the $1 Thursday ceiling;
the reason this run spent nothing is simpler - every automated and
demo path runs the deterministic stub.

## Assumptions

- Costs assume pay-per-token billing, no subscription, no caching.
- Local HTTP (uvicorn on 127.0.0.1) is free; "API calls" in the table
  means model/provider calls, not localhost curls.
- Token prices change; treat the teaching table as order-of-magnitude
  planning numbers and re-check before any live demo.
- Cost ledger: `src/afyaplus/mcp/cost_tracker.py` records every call;
  in stub mode it reports `total_cost_usd: 0.0`.

## Levers used to keep cost at zero

1. Stub before live LLM - tests and eval never touch a provider.
2. Fixtures in the hundreds (300 + 200 rows), not millions.
3. Pin before reviewing - pinned deps mean no surprise upgrades that
   would force re-runs.
4. Loopback HTTP for the demo instead of a hosted endpoint.
