# Demo transcript

End-to-end demonstration of AfyaPlus Module 4 Capstone in stub mode,
captured 2026-10-13. Every block below is real output; the raw
captures live in `docs/evidence/`.

## 1. Test suite

```bash
$ pytest -q
55 passed, 12 deselected, 1 warning in 2.35s

$ pytest -m integration
12 passed, 55 deselected, 1 warning in 1.80s
```

Raw: `docs/evidence/pytest_unit.txt`, `docs/evidence/pytest_integration.txt`.

## 2. One-command pipeline

```bash
$ python -m src.afyaplus.main
AfyaPlus Module 4 Capstone - end-to-end run (stub mode)
version: 1.0.0

== 1. pins ==
components: 6  ok: True
problems: none

== 2. security / redaction ==
raw    : Callback for Jane Otieno on 0712345678 or jane.otieno@example.com, ID 34817291, DOB 1985-06-21.
redacted: Callback for Jane Otieno on [PHONE] or [EMAIL], ID [ID], DOB [DOB].
contains_pii(raw)=True  contains_pii(redacted)=False

== 3. auth ==
issued for sub=demo-clinician role=clinician
tampered token: rejected (signature mismatch)

== 4. RAG ==
fixture rows ingested: 300  protocol docs built: 5
  guideline-sepsis  score=2  Sepsis red flags
  guideline-cardiology  score=1  Cardiology review pathway
  guideline-cost  score=0  Cost and token discipline

== 5. triage (router + domain twin) ==
  ['chest_pain'] age=58 -> emergency_department acuity=high     immediate_attention p=4 conf=0.85
  ['fever', 'cough'] age=27 -> urgent_care        acuity=moderate within_24_hours p=3 conf=0.95
  ['routine_checkup'] age=40 -> general_practice   acuity=low      routine_follow_up p=2 conf=0.85

== 6. MCP tool (stub fallback) ==
status=stub  reason=fallback to stub: MCP server not configured (AFYA_MCP_URL unset)
clinics: 2

== 7. catalog search (marketplace fixture, no clinical data) ==
catalog rows: 200  'gloves' hits: 5

== 8. cost ledger ==
summary: {'entries': 3, 'total_api_calls': 0, 'total_cost_usd': 0.0, 'mode': 'stub'}

== 9. golden-set evaluation ==
EVAL SCORE: 1.0000  (300/300 rows exact)
acuity_accuracy=1.0  recommendation_accuracy=1.0  endpoint_accuracy=1.0
mismatches: 0

== result ==
RUN COMPLETE
mode=stub  api_calls=0  spend=$0.00
```

Raw: `docs/evidence/end_to_end_run.txt`.

## 3. HTTP demo (three commands)

### Command 1 - start the service

```bash
$ ./start_service.sh
AfyaPlus triage API on http://127.0.0.1:8000  (mode=stub)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Command 2 - health

```bash
$ curl -i http://127.0.0.1:8000/health
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok","service":"afyaplus-triage","version":"1.0.0","mode":"stub",
 "build_sha":"2026-10-12T23:22:38Z","pins_ok":true,"uptime_seconds":286.46}
```

### Command 3 - token + triage

```bash
$ TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
    -H "Content-Type: application/json" \
    -d '{"client_id":"demo-clinician","role":"clinician"}' | ...)
$ curl -i -X POST http://127.0.0.1:8000/triage \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"symptoms":["fever","cough"],"age":68,"urgency_level":"moderate",
         "vitals":{"temperature":38.9,"heart_rate":104},
         "note":"Call 0712345678 or jane.otieno@example.com about the fever"}'

HTTP/1.1 200 OK
{"acuity":"high","recommendation":"immediate_attention","priority":4,
 "confidence_score":0.99,
 "reasons":["patient_reported_urgency=moderate","clinical_severity=high",
            "escalated_from_patient_report=moderate","vitals_considered",
            "age_band_escalation","endpoint=urgent_care"],
 "request_id":"7eac27885dd7",
 "redacted_note":"Call [PHONE] or [EMAIL] about the fever"}
```

The same request **without** a token returns `401`, with a `viewer`
token `403`, and with `age: -3` it returns `422` - all captured with
headers in `docs/evidence/api_transcript.txt`.

The server log line for that request shows the redacted note only:

```
triage request_id=7eac27885dd7 sub=demo-clinician endpoint=urgent_care
acuity=high note='Call [PHONE] or [EMAIL] about the fever'
```

(`docs/evidence/server_log.txt` - raw PII never reaches the log.)

## 4. Eval and performance

```bash
$ python scripts/eval_score.py
EVAL SCORE: 1.0000
rows=300 exact=300 mismatches=0
acuity_accuracy=1.0
recommendation_accuracy=1.0
endpoint_accuracy=1.0
PASS: score 1.0 >= threshold 0.9

$ python scripts/measure_perf.py
case                                p50 ms    p95 ms   mean ms    max ms
router.route                         0.035     0.050     0.044     0.974
domain_twin.assess                   0.054     0.151     0.105    10.845
rag_retriever.search                 0.182     0.870     0.358     9.972
mcp_tool.execute_stub                0.013     0.051     0.025     0.384
security.redact                      0.040     0.141     0.084     5.925
http_post_triage_inprocess           9.774    18.322    11.771    42.398
```

Raw: `docs/evidence/eval_score.txt`, `perf_stub.json`,
`docs/evidence/perf_measurement.txt`.

## 5. What the demo does *not* do

- No live LLM/MCP calls: every result above says `stub` and the cost
  ledger says `$0.00` (declared fallback, see README).
- No cloud deployment is exercised; `docs/deployment.md` marks those
  steps "[not executed live]".

## Reproduce everything

```bash
pytest -q
pytest -m integration
python -m src.afyaplus.main
./start_service.sh &          # then the three commands above
python scripts/eval_score.py
python scripts/measure_perf.py
```
