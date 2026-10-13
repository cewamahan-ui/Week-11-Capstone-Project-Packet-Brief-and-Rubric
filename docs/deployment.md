# Deployment

Status legend: **[executed]** - ran on this machine and captured;
**[not executed live]** - documented only, by declared fallback.

## 1. Local run - [executed]

No Docker, no cloud, no keys needed.

```bash
# 1. install pinned dependencies
pip install -r requirements.txt

# 2. run the test suite (unit tier is the default)
pytest -q

# 3. start the service
./start_service.sh            # or: python -m src.afyaplus.main serve
```

Verify:

```bash
curl -i http://127.0.0.1:8000/health
```

Captured output: `docs/evidence/api_transcript.txt`
(health 200, token 200, triage 401 / 403 / 422 / 200).

## 2. One-command pipeline - [executed]

```bash
python -m src.afyaplus.main
```

Runs pins -> redaction -> auth -> RAG -> triage -> MCP stub ->
catalog -> cost ledger -> eval, and prints the eval score.
Captured output: `docs/evidence/end_to_end_run.txt`.

## 3. Docker - [not executed live]

Docker is not installed on this machine, so no image build was run.
The steps below are provided for whoever runs them later; they have
**not** been verified here.

```dockerfile
# suggested Dockerfile sketch (not executed)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["python", "-m", "src.afyaplus.main", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t afyaplus-triage:local .
docker run --rm -p 8000:8000 afyaplus-triage:local
```

## 4. Kubernetes / cloud - [not executed live]

Documentation only. Nothing was deployed to a cluster or cloud
account for this capstone (declared fallback: no cloud credentials).

Suggested shape if executed later:

- Deployment: 2 replicas of the API container, readiness probe on
  `/health`, requests 128Mi/250m.
- Secret: `AFYA_TOKEN_SECRET` from a Kubernetes Secret, never from a
  committed `.env`.
- HPA on CPU 70%; the service is stateless (no DB in stub mode).

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `AFYA_TOKEN_SECRET` | no | `local-demo-secret-change-me` (dev placeholder) | HMAC signing secret for bearer tokens |
| `AFYA_MCP_URL` | no | unset (forces stub MCP path) | Real MCP server, if ever wired |
| `HOST` / `PORT` | no | `127.0.0.1` / `8000` | Bind address for `start_service.sh` |

## Rollback / versioning

- Dependency versions are pinned in `requirements.txt` and mirrored in
  `src/afyaplus/pins/manifest.json`; `tests/test_pin_fields.py` fails
  if the two disagree.
- The source digest in the manifest must match the committed tree -
  regenerate pins after any code change with
  `python -m src.afyaplus.pins.manifest`.
