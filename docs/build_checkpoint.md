# Build checkpoint

Honest status of the capstone as of 2026-10-13. Every "works" line
names its evidence; every deferral says why. Nothing below is
inflated: if it is not linked to a captured artefact, it is listed
under deferred, not under works.

## What works (with evidence)

| Capability | Evidence |
|------------|----------|
| 55 unit/security/golden tests green | `docs/evidence/pytest_unit.txt` ("55 passed, 12 deselected") |
| 12 API integration tests green | `docs/evidence/pytest_integration.txt` ("12 passed, 55 deselected") |
| One-command end-to-end pipeline | `python -m src.afyaplus.main` -> `docs/evidence/end_to_end_run.txt` |
| HTTP API: auth, validation, redaction | `docs/evidence/api_transcript.txt` (200 / 401 / 403 / 422 / 200) |
| Redacted server logs | `docs/evidence/server_log.txt` (`note='Call [PHONE] or [EMAIL] ...'`) |
| Golden-set eval score | `docs/evidence/eval_score.txt` (`EVAL SCORE: 1.0000`, 300 rows) |
| Measured performance | `perf_stub.json` + `docs/evidence/perf_measurement.txt` |
| Pins verified in CI-style run | `src/afyaplus/pins/manifest.json`, `tests/test_pin_fields.py` |
| Fixtures: 300 + 200 rows, no PII, no scrape | `fixtures/README.md`, `tests/test_security_smoke.py` |
| Broken-fixture diagnosis and fix | `docs/incidents/2026-10-13-fixture-label-drift.md` |
| Peer review with named reviewer | `review_log.md` (Alvin Swalah), `docs/peer_review_checklist.md` |
| Feature-branch history | `feature/module4-capstone`, merged to `main` with `--no-ff` |

## What is deferred (and why)

| Deferred | Why |
|----------|-----|
| Live LLM backend | Fallback declared: no live key used. Tests mandate stub mode; the ~$1 Thursday allowance was not spent (see `docs/cost_analysis.md`). |
| Real MCP server | `AFYA_MCP_URL` unset by design; `MCPTools` falls back to deterministic stubs with the reason visible on every result. |
| Docker image build | Docker is not installed on this machine - deployment.md marks those steps "[not executed live]". |
| Cloud / Kubernetes deploy | No cloud credentials; docs only, explicitly marked not executed. |
| Vector embeddings for RAG | Retrieval is deterministic token overlap; an index would add a service the tests cannot guarantee. |
| Database persistence | Stateless by design; cases and tokens live for the request only. |
| Streaming responses | Out of scope for the packet's MWP layers. |
| Week 10 clinic-poster transfer | The catalog path of Week 10 was taken instead (`src/afyaplus/catalog/`). |

## Known limitations (be aware before demoing)

- **The eval score is a regression guard, not clinical validation.**
  Gold labels are produced by the same shared policy module the
  runtime executes. Its value is detecting fixture/runtime drift -
  which it did: the pre-fix run scored 0.6833 on the same rows
  (incident note). Treat 1.0000 as "contract consistent", not
  "clinically accurate".
- The default token secret is a development placeholder; anything
  beyond localhost must set `AFYA_TOKEN_SECRET`.
- The dataset is one seeded synthetic sample (seed=42), not a
  population estimate.
- The in-process HTTP perf case includes framework overhead but no
  socket latency, so it is not a network benchmark.

## Explicitly not claimed

- No production data, no scraping, no real patient rows.
- No live provider calls were made while building or demonstrating.
- No deployment is claimed to be running anywhere.
