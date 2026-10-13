# User guide

AfyaPlus triage service - stub mode. Python 3.12+ (built and tested
on 3.14), no keys, no Docker required.

## Quick start

```bash
pip install -r requirements.txt   # pinned dependencies
pytest -q                          # unit tier (default): 55 tests
python -m src.afyaplus.main        # full pipeline, prints eval score
```

## Demo (three commands)

```bash
# 1. start the service (default 127.0.0.1:8000)
./start_service.sh
#    Windows / alternative:  python -m src.afyaplus.main serve

# 2. health check
curl -i http://127.0.0.1:8000/health

# 3. issue a token and triage a case (one line)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"demo-clinician","role":"clinician"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])") && \
curl -i -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"symptoms":["fever","cough"],"age":68,"urgency_level":"moderate",
       "vitals":{"temperature":38.9,"heart_rate":104},
       "note":"Call 0712345678 about the fever"}'
```

The response carries `redacted_note` - the phone number in the note
comes back as `[PHONE]`, and the server log never sees the raw value.

## API reference

| Method | Path | Auth | Success | Failures |
|--------|------|------|---------|----------|
| GET | `/health` | none | 200 + version, pins, uptime | - |
| POST | `/token` | none | 200 `{access_token, token_type, role}` | 422 unknown role / missing client_id |
| POST | `/triage` | Bearer (role `clinician`) | 200 assessment | 401 no/bad token, 403 wrong role, 422 invalid case |

Request body for `/triage`:

```json
{
  "symptoms": ["fever", "cough"],
  "age": 68,
  "urgency_level": "low | moderate | high",
  "vitals": {"temperature": 38.9, "heart_rate": 104},
  "note": "optional free text - redacted before echo and logs"
}
```

Response fields: `acuity`, `recommendation`
(`immediate_attention | within_24_hours | routine_follow_up`),
`priority` (1-4), `confidence_score`, `reasons`, `request_id`,
`redacted_note`.

## Test commands

```bash
pytest -q                     # default tier: unit + security + golden (55)
pytest -m integration         # API integration tier (12)
pytest tests/test_security_smoke.py   # Week 9 security smoke
```

Evidence of the last run: `docs/evidence/pytest_unit.txt`.

## Stub path

- The domain twin is deterministic; no LLM is called anywhere in the
  default path.
- MCP tools fall back to stub responses when `AFYA_MCP_URL` is unset
  (the default), and the result says `"status": "stub"` with the
  fallback reason.
- Retrieval is token overlap over a fixed corpus - no embedding
  service.

Environment variables (all optional):

| Variable | Default | Purpose |
|----------|---------|---------|
| `AFYA_TOKEN_SECRET` | dev placeholder | token signing secret - **set this for anything non-local** |
| `AFYA_MCP_URL` | unset (stub) | real MCP server endpoint |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | service bind address |

## Dataset and tools

```bash
python scripts/make_fixtures.py   # regenerate 300 + 200 seeded rows
python scripts/eval_score.py      # golden-set eval, prints EVAL SCORE
python scripts/measure_perf.py    # rewrites perf_stub.json
python -m src.afyaplus.pins.manifest   # re-stamp pins after code changes
```

Fixture rules (row counts, no-scrape, no-PII) are in
`fixtures/README.md`.

## Troubleshooting

- **`pin digest does not match the current tree`** - code changed
  after pins were stamped; run
  `python -m src.afyaplus.pins.manifest`.
- **401 on /triage** - fetch a token first (demo command 3).
- **403** - the token's role is not `clinician`; request one with
  `"role": "clinician"`.
- **Port already in use** - `PORT=8080 ./start_service.sh`.
