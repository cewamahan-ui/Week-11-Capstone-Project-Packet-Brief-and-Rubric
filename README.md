# Module 4 Capstone: AfyaPlus

## Overview

AfyaPlus Module 4 Capstone is an integrated AI health-operations
system: an authenticated triage API (`/health`, `/token`, `/triage`)
backed by a deterministic domain twin and router, a small RAG layer,
MCP tool stubs with cost tracking, pin/version manifest verification
and a redaction-first security layer. I took the **AfyaPlus Module 4
Capstone (recommended)** path, reusing Weeks 1-10 artefacts and running
everything in **stub mode** - no network calls, no API spend, no live
keys. Evidence for every claim below lives in `docs/evidence/`.

## Project path

- [x] AfyaPlus Module 4 Capstone (recommended)
- [ ] Domain / field alternative with skill checklist

## Week reuse (open these)

Programme artefacts live in the course workspace (`week 1` ..
`week 10` folders next to this repo) and are **not shipped** here;
each line names what was carried into this repo.

- Weeks 1-5: LLM/RAG fundamentals from `week 2/course work/lab11_rag.py`
  and `week 3/evaluation/`, routing habits from
  `week 5/AfyaPlus Multimodal Intake Assistant/router.py` ->
  reused as `src/afyaplus/rag/`, `src/afyaplus/router/deterministic.py`,
  `src/afyaplus/evaluation.py`
- Week 6: `week 6/agent/api.py` + `week 6/evidence/curl_*.txt` ->
  `src/afyaplus/triage/api.py`, `tests/test_api.py`,
  `docs/evidence/api_transcript.txt`
- Week 7: `week 7/capstone 7/cost/` -> `src/afyaplus/mcp/tools.py`,
  `src/afyaplus/mcp/cost_tracker.py`, `docs/cost_analysis.md`
- Week 8 pins: `week 8/capstone 8/check_prompt_pin.py` ->
  `src/afyaplus/pins/`, `tests/test_pin_fields.py`,
  `src/afyaplus/pins/manifest.json`
- Week 9 smoke: `week 9/capstone 9/injection_guard.py`,
  `week 9/capstone 9/rbac.py` -> `src/afyaplus/security/`,
  `src/afyaplus/triage/auth.py`, `tests/test_security_smoke.py`
- Week 10 catalog: `week 10/capstone 10/catalog.json` ->
  `src/afyaplus/catalog/`, `fixtures/catalog_listings_sample.jsonl`
  (clinic-poster transfer alternative not taken)

Machine-readable version of the same mapping:
`integration_map.json` (`week_reuse` section) and `skill_matrix.md`.

## Dataset

- `fixtures/triage_messages_sample.jsonl`: **300 rows**, synthetic
  clinical cases + gold labels. No production scrape.
- `fixtures/catalog_listings_sample.jsonl`: **200 rows**, marketplace
  listings, no clinical fields.
- Both files are seeded output of `scripts/make_fixtures.py`
  (offline, `seed=42`). Rules: `fixtures/README.md`.

## Quick start

```bash
pytest -q
```

Then:

```bash
pip install -r requirements.txt
python -m src.afyaplus.main     # full pipeline, prints EVAL SCORE
```

## Docs

- `docs/architecture.md`
- `docs/deployment.md`
- `docs/cost_analysis.md`
- `docs/user_guide.md`
- `docs/build_checkpoint.md`
- `fixtures/README.md` (row counts + no-scrape rule)
- `docs/incidents/2026-10-13-fixture-label-drift.md` (broken-fixture
  diagnosis)
- `docs/demo_transcript.md` (end-to-end transcript)

## Testing

```bash
pytest -q                          # unit default: 55 tests
pytest -m integration              # API integration: 12 tests
pytest tests/test_security_smoke.py   # Week 9 security smoke
```

Evidence: `docs/evidence/pytest_unit.txt` ("55 passed, 12
deselected"), `docs/evidence/pytest_integration.txt` ("12 passed, 55
deselected"). CI (`.github/workflows/ci.yml`) runs the same commands
plus `scripts/eval_score.py`, so the **EVAL SCORE line prints in the
CI logs**; the local capture is `docs/evidence/eval_score.txt`
(`EVAL SCORE: 1.0000` over 300 rows).

## Demo

Three commands (details in `docs/user_guide.md`):

```bash
./start_service.sh
curl -i http://127.0.0.1:8000/health
# token + triage one-liner: see docs/user_guide.md "Demo (three commands)"
```

Captured output: `docs/evidence/api_transcript.txt`
(200 / 401 / 403 / 422 / 200 with redacted note).

## Presentation

`docs/presentation.pdf`, presented Week 12 Monday.
Outline: `docs/presentation_outline.md` (made in Thursday Lab 2).

## Peer review

- `review_log.md` entry: 2026-10-13, reviewer **Alvin Swalah**,
  branch `feature/module4-capstone`, 5 findings recorded and
  re-verified (55 + 12 tests green, eval 1.0000).
- checklist: `docs/peer_review_checklist.md` (12 items)

## Fallbacks declared

- [x] no live OpenAI key (stub agent)
- [x] no Docker (integration manual, marked "[not executed live]")
- [x] no cloud deploy executed (docs only)
- [ ] solo reviewer - instead a peer review was completed:
  **Alvin Swalah**, see `review_log.md`

## Evidence summary

| Claim | Capture |
|-------|---------|
| Unit pytest green | `docs/evidence/pytest_unit.txt` |
| Integration green | `docs/evidence/pytest_integration.txt` |
| Eval score 1.0000 (300 rows) | `docs/evidence/eval_score.txt` |
| Pre-fix eval 0.6833 + failing test | `docs/evidence/eval_pre_fix.txt`, `docs/evidence/gold_fixture_pre_fix_failure.txt` |
| Measured performance | `perf_stub.json`, `docs/evidence/perf_measurement.txt` |
| HTTP demo transcript | `docs/evidence/api_transcript.txt` |
| Redacted server log | `docs/evidence/server_log.txt` |
| One-command pipeline | `docs/evidence/end_to_end_run.txt` |

## Submission checklist

- [x] proposal + skill_matrix + map
- [x] five docs linked
- [x] peer review completed
- [x] slides PDF in docs/ and demo command documented
