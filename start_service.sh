#!/usr/bin/env bash
# Start the AfyaPlus triage API in stub mode (demo command).
#   ./start_service.sh          # default 127.0.0.1:8000
#   PORT=8080 ./start_service.sh
set -euo pipefail
cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

exec python -m src.afyaplus.main serve --host "$HOST" --port "$PORT"
