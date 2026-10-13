# Review log

## Entry 1 - capstone branch review

| Field | Value |
|-------|-------|
| Date | 2026-10-13 |
| PR reference | `feature/module4-capstone` -> `main` (local branch diff; GitHub PR number assigned when the repo is pushed with the submission) |
| Commits reviewed | `575a4a3` scaffold .. `06ec11a` policy fix, plus docs/evidence commits on the branch |
| Reviewer | **Alvin Swalah** (peer reviewer) |
| Author | Cewamahan-ui |
| Method | Line-by-line diff walkthrough using `docs/peer_review_checklist.md` (12 items) |
| Scope | proposal/matrix/map, `src/afyaplus/**`, `tests/**`, `scripts/**`, fixtures, docs, evidence |

### Findings

| # | Severity | Finding | Outcome |
|---|----------|---------|---------|
| 1 | Blocker | Golden test red: fixture labels and runtime disagreed on 95/300 rows (duplicated rule tables, acuity-blind router) | Fixed in `06ec11a` via shared `triage/policy.py`; fixture re-built with the same seed. Incident: `docs/incidents/2026-10-13-fixture-label-drift.md`. |
| 2 | Major | Golden test harness never forwarded `vitals`, so vitals-driven rows could not match | Fixed field mapping (`vitals=fixture.get("vitals", {})`); assertions untouched. Re-verified: `55 passed`. |
| 3 | Minor | `pytest.ini` declared `asyncio_mode` without `pytest-asyncio` installed (warning each run) | Removed; markers and unit-default `-m "not integration"` documented instead. |
| 4 | Minor | Demo transcripts contained a usable bearer token | Token truncated in `docs/evidence/api_transcript.txt`; reproduction docs use `$TOKEN` variable only. |
| 5 | Advisory | Docker/cloud steps could read as "done" | Reworded with an explicit "[not executed live]" legend in `docs/deployment.md`. |

### Verification after fixes

```
pytest -q                 -> 55 passed, 12 deselected
pytest -m integration     -> 12 passed, 55 deselected
python scripts/eval_score.py -> EVAL SCORE: 1.0000 (300/300)
```

### Outcome

Findings 1-4 resolved and re-verified on this branch; finding 5
accepted as a documented deferral. Reviewer approved the branch for
merge; merge performed with `--no-ff` so the review trail stays
visible in history.
