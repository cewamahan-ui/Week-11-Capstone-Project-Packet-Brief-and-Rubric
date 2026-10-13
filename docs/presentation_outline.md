# Presentation outline

Working outline for the Week 12 Monday slot (7 min talk + 3 min live
demo + 3 min questions; adjust to cohort size). Prepared in Thursday
Lab 2 from this outline; exported deck: `docs/presentation.pdf`
(10 slides).

| # | Slide | Key points | Time |
|---|-------|------------|------|
| 1 | Problem and user | Clinic staff routing patients with inconsistent paper rules; ops leads cannot audit decisions or control LLM cost; free-text notes leak PII. | 45s |
| 2 | Path chosen and why | AfyaPlus recommended path; Weeks 1-10 artefacts reused; full skill checklist mapped in `skill_matrix.md` / `integration_map.json`. | 30s |
| 3 | Architecture | Module boundaries: policy at the centre, twin/router, API + auth, RAG, MCP stub, pins, security, catalog; stub mode end to end. | 60s |
| 4 | Skill coverage | Week-by-week: RAG/router (1-5), API/auth (6), MCP/cost (7), pins (8), security smoke (9), catalog (10) - each with the repo path. | 60s |
| 5 | Live demo | Three commands: start service, `/health`, token + `/triage` with a PII note (redaction on screen). Backup: 60-second walk of `docs/demo_transcript.md`. | 90s |
| 6 | Testing evidence | `pytest -q` 55 passed; integration 12 passed; security smoke; `EVAL SCORE: 1.0000` (300 rows); perf p95 numbers; golden-fixture incident 0.6833 -> 1.0000. | 60s |
| 7 | Security and compliance | HMAC tokens (401/403), redaction before echo and logs, repo secret scan, no PII in fixtures, clinical/marketplace split, no production data. | 45s |
| 8 | Cost table with assumptions | All executed steps $0.00; ~$1 live allowance declared but unspent (stub fallback); teaching prices if a live model were wired. | 45s |
| 9 | What works vs deferred | Works (with evidence links) vs deferred (live LLM, Docker, cloud, embeddings, streaming) with reasons; eval caveat: regression guard, not clinical validation. | 45s |
| 10 | Process | Feature branch `feature/module4-capstone`, red -> green fix commit, peer review by Alvin Swalah (5 findings resolved), next steps. | 30s |

## Talking points per slide

1. **Problem and user** - Nurses and clinical officers at small
   clinics make triage calls under time pressure; paper protocols
   differ per site. Ops leads cannot answer "why did the system say
   that?" and copy-paste notes carry phone numbers and IDs around.
2. **Path chosen** - The official AfyaPlus path was the fastest way to
   demonstrate the whole checklist on one coherent product instead of
   six disconnected demos.
3. **Architecture** - One decision policy (`triage/policy.py`) feeds
   assessment, routing and fixture labels; everything else composes
   around it. Stub mode is a first-class path, not a broken live path.
4. **Skill coverage** - Point at `skill_matrix.md` columns: week
   resource reopened, capstone file, evidence.
5. **Demo** - Show the redaction live: raw phone in, `[PHONE]` out,
   and the same redaction visible in the server log.
6. **Testing** - Three tiers; the golden set caught a real drift
   (numbers on slide); incident note linked.
7. **Security** - Fail closed (401/403), redact at the edge, scan the
   repo for secrets in CI.
8. **Cost** - $0.00 actually spent; the ceiling was $1; stub-before-
   live is the reason.
9. **Honesty slide** - Read the deferred list out loud; that is the
   point of the checkpoint.
10. **Process** - Branch, red->green history, named reviewer, next
    steps (push, PR, optional live wiring).

## Backup material

- 60-second recorded/step transcript: `docs/demo_transcript.md`
- Raw captures: `docs/evidence/`
- Incident story: `docs/incidents/2026-10-13-fixture-label-drift.md`
