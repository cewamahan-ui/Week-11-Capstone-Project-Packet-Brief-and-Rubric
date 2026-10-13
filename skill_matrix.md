# Skill Matrix: Week Resource Mapping

Columns: the programme artefact that was reopened (course workspace,
not shipped in this repo), the capstone file it became, and where the
evidence lives. Every referenced capstone path exists in this repo -
checked by the review (checklist item 1, `docs/peer_review_checklist.md`).

| Skill Area | Required/Optional | Week Resource (reopened) | File/Module Reference (in this repo) | Evidence Location |
|------------|------------------|--------------------------|--------------------------------------|-------------------|
| **Weeks 1-5: LLM/RAG/Multimodal Fundamentals** | | | | |
| LLM prompt / routing fundamentals | Required | Week 1-2 (`week 2/course work/lab11_rag.py`) | `src/afyaplus/router/deterministic.py` | `tests/test_router.py` |
| RAG document processing | Required | Week 3 (`week 3/evaluation/`) | `src/afyaplus/rag/ingest.py` | `tests/test_rag.py` |
| RAG retrieval (deterministic) | Required | Week 3 (`week 2/course work/lab11_rag.py`) | `src/afyaplus/rag/retriever.py` | `tests/test_rag.py`, `tests/test_service_function_stub.py` |
| Multimodal intake habits | Optional | Week 4-5 (`week 5/.../caption_image.py`) | not taken - deferred in `docs/build_checkpoint.md` | build checkpoint |
| **Week 6: Triage API** | | | | |
| Triage endpoint design | Required | Week 6 (`week 6/agent/api.py`) | `src/afyaplus/triage/api.py` | `tests/test_api.py`, `docs/evidence/api_transcript.txt` |
| Symptom assessment logic | Required | Week 6 (`week 6/agent/agent.py`) | `src/afyaplus/triage/domain_twin.py` + `src/afyaplus/triage/policy.py` | `tests/test_domain_twin.py`, `tests/test_gold_fixture.py` |
| API authentication | Required | Week 6 (`week 6/agent/api.py`) | `src/afyaplus/triage/auth.py` | `tests/test_security_smoke.py::TestTokenIntegrity`, `tests/test_api.py::TestTriageAuth` |
| **Week 7: Cost / MCP Logistics Tools** | | | | |
| MCP tool stub implementation | Required | Week 7 (`week 7/capstone 7/exec/`) | `src/afyaplus/mcp/tools.py` | `tests/test_service_function_stub.py` |
| Cost tracking integration | Required | Week 7 (`week 7/capstone 7/cost/`) | `src/afyaplus/mcp/cost_tracker.py` | `docs/cost_analysis.md`, `docs/evidence/end_to_end_run.txt` |
| Logistics tool abstraction | Optional | Week 7 (`week 7/capstone 7/exec/`) | `plan_delivery_route` stub inside `src/afyaplus/mcp/tools.py` | `tests/test_service_function_stub.py` |
| **Week 8: Pins / Versioning** | | | | |
| Component pinning system | Required | Week 8 (`week 8/capstone 8/check_prompt_pin.py`) | `src/afyaplus/pins/manager.py` | `tests/test_pin_fields.py` |
| Version manifest generation | Required | Week 8 (`week 8/capstone 8/CHANGELOG.md`) | `src/afyaplus/pins/manifest.py` -> `src/afyaplus/pins/manifest.json` | `tests/test_pin_fields.py` |
| Pinned dependencies | Required | Week 8 (`week 8/capstone 8/azure-pipelines.yml`) | `requirements.txt` (exact `==` pins) | `test_manifest_and_requirements_agree` |
| Deployment pinning | Optional | Week 8 (`week 8/capstone 8/deploy/`) | docs only - steps marked "[not executed live]" | `docs/deployment.md` |
| **Week 9: Security and Compliance** | | | | |
| PII redaction pipeline | Required | Week 9 (`week 9/capstone 9/injection_guard.py`) | `src/afyaplus/security/redaction.py` | `tests/test_security_smoke.py::TestRedaction` |
| Security smoke tests | Required | Week 9 (`week 9/capstone 9/conftest.py`) | `tests/test_security_smoke.py` | CI (`.github/workflows/ci.yml`), `docs/evidence/pytest_unit.txt` |
| Secrets / env hygiene | Required | Week 9 (`week 9/capstone 9/check_gitignore.py`) | `.gitignore`, no `.env` committed | `test_no_secrets_committed`, `test_no_env_file_committed` |
| Compliance posture docs | Optional | Week 9 (`week 9/capstone 9/dpia_stub.md`) | env-var table + declared fallbacks | `docs/deployment.md`, `README.md` |
| **Week 10: Multimodal Catalog OR Clinic-Poster Transfer** | | | | |
| Catalog CRUD / search | Required | Week 10 (`week 10/capstone 10/catalog.json`) | `src/afyaplus/catalog/service.py` | `tests/test_catalog.py` |
| Marketplace fixture line | Required | Week 10 (`week 10/capstone 10/fixtures/`) | `fixtures/catalog_listings_sample.jsonl` | `tests/test_security_smoke.py::TestRepoHygiene` |
| Clinic-poster transfer | Optional | Week 10 (`week 10/capstone 10/ethics_note.md`) | not taken - catalog path chosen instead | `docs/build_checkpoint.md` |
| **Cross-Cutting Requirements** | | | | |
| Unit test pyramid (default tier) | Required | all weeks | `pytest.ini` (`-m "not integration"`), `tests/` | `docs/evidence/pytest_unit.txt` |
| Integration markers | Required | Week 6 | `pytest.ini` markers, `tests/test_api.py` | `docs/evidence/pytest_integration.txt` |
| Performance measurement | Required | Week 7, 11 | `scripts/measure_perf.py` | `perf_stub.json`, `docs/evidence/perf_measurement.txt` |
| Golden-set eval | Required | Week 3, 5 | `scripts/eval_score.py`, `src/afyaplus/evaluation.py` | `docs/evidence/eval_score.txt` |
| Broken-fixture diagnosis | Required | Week 11 | shared `triage/policy.py` fix (commit `06ec11a`) | `docs/incidents/2026-10-13-fixture-label-drift.md` |
| Documentation pack | Required | all weeks | `docs/*.md` | `README.md` links |
| Git flow / peer review | Required | Week 11 | `review_log.md`, `docs/peer_review_checklist.md` | git history (`feature/module4-capstone`) |
| Presentation | Required | Week 12 | `docs/presentation.pdf` | Demo session, Week 12 Monday |

## Skill Checklist Summary

- **Required skills**: 19/19 covered by a file in this repo
- **Optional skills**: 3/7 taken (logistics tool stub, compliance
  docs, deployment pinning as documentation); 4 explicitly deferred
  with reasons in `docs/build_checkpoint.md`
- **Week reuse evidence**: `integration_map.json` -> `week_reuse`,
  plus this table
- **No PII mixing**: clinical and catalog fixtures are separate files
  with two-way tests in `tests/test_security_smoke.py` and
  `tests/test_catalog.py`
- **Dataset scale**: 300 rows (clinical) + 200 rows (catalog), both
  inside the 200-500 band, generated offline with `seed=42`
