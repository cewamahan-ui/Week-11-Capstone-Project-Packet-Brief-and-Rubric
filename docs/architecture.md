# Architecture

## What the system is

AfyaPlus Module 4 Capstone is an integrated AI health-operations
service: an authenticated triage API backed by a deterministic domain
twin, a small RAG layer, MCP tool stubs, pin management and a
redaction-first security layer. Everything runs in **stub mode** - no
network calls, no API spend - which is the path declared in the
README and used by the automated tests, the eval and the demo.

## Module boundaries

```
module4-capstone/
├── src/afyaplus/
│   ├── triage/
│   │   ├── policy.py       # single source of truth: acuity + routing rules
│   │   ├── models.py       # TriageRequest / TriageResponse contracts
│   │   ├── domain_twin.py  # deterministic assessment (stub model)
│   │   ├── auth.py         # HMAC-SHA256 bearer tokens, roles
│   │   └── api.py          # FastAPI app: /health /token /triage
│   ├── router/
│   │   └── deterministic.py# endpoint selection (uses triage.policy)
│   ├── rag/
│   │   ├── ingest.py       # JSONL loading + protocol documents
│   │   └── retriever.py    # deterministic token-overlap retrieval
│   ├── mcp/
│   │   ├── tools.py        # MCP client with stub fallback
│   │   └── cost_tracker.py # per-call cost ledger ($0 in stub mode)
│   ├── pins/
│   │   ├── manifest.py     # pin manifest builder (source digest, versions)
│   │   ├── manifest.json   # committed pins
│   │   └── manager.py      # verification used by tests and /health
│   ├── security/
│   │   └── redaction.py    # PII redaction (email/phone/ID/card/DOB)
│   ├── catalog/
│   │   └── service.py      # marketplace search (separate fixture line)
│   ├── evaluation.py       # golden-set scoring
│   └── main.py             # one-command runner + server entry point
├── fixtures/               # 300 triage + 200 catalog synthetic rows
├── scripts/                # make_fixtures, eval_score, measure_perf, ...
├── tests/                  # unit (default) / integration / security tiers
└── docs/                   # this pack + evidence + slides
```

## The policy module (why the design looks like this)

`triage/policy.py` holds every decision rule: symptom severities,
vitals thresholds, age escalation, red-flag / routine / urgent token
sets and the routing order. Three consumers import it:

1. `domain_twin.py` - assessment at request time,
2. `router/deterministic.py` - endpoint selection,
3. `scripts/make_fixtures.py` - gold labels in the fixture.

One copy of the rules means the golden fixture can never drift away
from what the runtime enforces. This structure was adopted *after* the
label-drift incident recorded in
`docs/incidents/2026-10-13-fixture-label-drift.md`; before it, the
generator kept a private copy of the tables and 95 of 300 rows
disagreed with the service.

## Request flow

```
POST /triage  +  Authorization: Bearer <token>
     │
     ├─ auth: verify HMAC signature, expiry, role (401 / 403)
     ├─ validation: pydantic constraints (422 on bad input)
     ├─ router.route(case)         -> endpoint + priority
     │      └─ policy.compute_acuity / policy.decide_endpoint
     ├─ domain_twin.assess(case)   -> acuity, disposition, confidence
     │      └─ policy.symptom/vitals/age rules
     ├─ security.redact(note)      -> PII never echoed or logged raw
     └─ response (acuity, recommendation, priority, reasons, request_id)
```

## Data flow

- `fixtures/triage_messages_sample.jsonl` feeds the RAG ingest, the
  golden tests and the eval. It never leaves the repo.
- `fixtures/catalog_listings_sample.jsonl` feeds `CatalogService`
  only. Clinical and marketplace rows are never combined.
- Retrieval uses a fixed built-in protocol corpus plus fixture-derived
  documents; there is no external index or embedding service.

## Stub vs live

| Layer | Stub path (used) | Live path (not wired) |
|-------|------------------|-----------------------|
| Model | `DomainTwin` rules | hosted LLM behind the same interface |
| MCP | `MCPTools.execute` fallback | server reachable at `AFYA_MCP_URL` |
| Retrieval | token overlap | vector index |
| Auth secret | `AFYA_TOKEN_SECRET` env / dev placeholder | managed secret store |

The fallbacks are declared in the README; automated tests force the
stub path (`AFYA_MCP_URL` unset), so CI can never spend money.
