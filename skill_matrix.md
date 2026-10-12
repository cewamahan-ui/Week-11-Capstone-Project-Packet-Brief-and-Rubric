# Skill Matrix: Week Resource Mapping

| Skill Area | Required/Optional | Week Resource | File/Module Reference | Evidence Location |
|------------|------------------|---------------|----------------------|-------------------|
| **Weeks 1-5: LLM/RAG/Multimodal Fundamentals** | | | | |
| LLM prompt engineering | Required | Week 1-2 | `src/afyaplus/rag/retriever.py` | Unit tests + integration |
| RAG document processing | Required | Week 3 | `src/afyaplus/rag/ingest.py` | `tests/test_rag.py` |
| Multimodal handling | Optional | Week 4-5 | `src/afyaplus/catalog/multimodal.py` | Feature flag |
| **Week 6: Triage API** | | | | |
| Triage endpoint design | Required | Week 6 | `src/afyaplus/triage/api.py` | `tests/test_triage.py` |
| Symptom assessment logic | Required | Week 6 | `src/afyaplus/triage/assessment.py` | Gold fixture tests |
| API authentication | Required | Week 6 | `src/afyaplus/triage/auth.py` | Security smoke tests |
| **Week 7: Cost / MCP Logistics Tools** | | | | |
| MCP tool stub implementation | Required | Week 7 | `src/afyaplus/mcp/tools.py` | `tests/test_mcp.py` |
| Cost tracking integration | Required | Week 7 | `src/afyaplus/mcp/cost_tracker.py` | `docs/cost_analysis.md` |
| Logistics tool abstraction | Optional | Week 7 | `src/afyaplus/mcp/logistics.py` | Stub mode only |
| **Week 8: Pins / Versioning** | | | | |
| Component pinning system | Required | Week 8 | `src/afyaplus/pins/manager.py` | `tests/test_pins.py` |
| Version manifest generation | Required | Week 8 | `src/afyaplus/pins/manifest.py` | `pins.yaml` |
| Deployment pinning | Optional | Week 8 | `src/afyaplus/pins/deploy.py` | Not executed live |
| **Week 9: Security and Compliance** | | | | |
| PII redaction pipeline | Required | Week 9 | `src/afyaplus/security/redaction.py` | `tests/test_security_smoke.py` |
| Security smoke tests | Required | Week 9 | `tests/test_security_smoke.py` | CI pipeline |
| Compliance metadata | Optional | Week 9 | `src/afyaplus/security/compliance.py` | Architecture docs |
| **Week 10: Multimodal Catalog OR Clinic-Poster Transfer** | | | | |
| Catalog CRUD operations | Required | Week 10 | `src/afyaplus/catalog/service.py` | `tests/test_catalog.py` |
| Search and filter engine | Required | Week 10 | `src/afyaplus/catalog/search.py` | Gold fixture tests |
| Poster transfer habits | Optional | Week 10 | `src/afyaplus/catalog/poster.py` | Feature flag |
| **Cross-Cutting Requirements** | | | | |
| Unit test pyramid | Required | All weeks | `pytest.ini`, `tests/` | CI badge |
| Integration test markers | Required | All weeks | `pytest.ini` | CI logs |
| Performance measurement | Required | Week 7, 11 | `scripts/measure_perf.py` | `perf_stub.json` |
| Documentation pack | Required | All weeks | `docs/*.md` | README links |
| Git flow / peer review | Required | Week 11 | `review_log.md`, `peer_review_checklist.md` | Git history |
| Presentation | Required | Week 12 | `docs/presentation.pdf` | Demo session |

## Skill Checklist Summary
- **Required Skills**: 18/18 covered
- **Optional Skills**: 4/6 covered (multimodal, logistics, deploy pinning, poster transfer)
- **Week Reuse Evidence**: Explicit in `integration_map.json` and test files
- **No PII mixing**: Clinical triage fixtures separate from catalog fixtures
- **Dataset Scale**: ~300 rows in `fixtures/triage_messages_sample.jsonl`