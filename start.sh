#!/usr/bin/env bash
# start.sh

set -euo pipefail

# optionally override via env
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
WORKERS=${WORKERS:-1}

exec uvicorn server.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --log-level info \
  --workers "$WORKERS"