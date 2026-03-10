#!/bin/bash

PORT=${UVICORN_PORT:-3000}
CPU_WORKERS=$(python -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')
WORKERS=${UVICORN_WORKERS:-$CPU_WORKERS}
MAX_REQUESTS=${UVICORN_MAX_REQUESTS:-2000}
TIMEOUT=${UVICORN_TIMEOUT:-90}

echo "Starting Uvicorn with $WORKERS workers on port $PORT"

exec uvicorn app.asgi:application \
  --host 0.0.0.0 \
  --port "$PORT" \
  --workers "$WORKERS" \
  --limit-max-requests "$MAX_REQUESTS" \
  --timeout-keep-alive "$TIMEOUT" \
  --log-level info \
  --no-server-header \
  --lifespan off
