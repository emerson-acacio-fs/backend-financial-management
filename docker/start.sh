#!/usr/bin/env sh
set -e

MAX_RETRIES="${DB_WAIT_MAX_RETRIES:-30}"
SLEEP_SECONDS="${DB_WAIT_SLEEP_SECONDS:-2}"

attempt=1
until alembic upgrade head; do
  if [ "$attempt" -ge "$MAX_RETRIES" ]; then
    echo "[startup] Failed to apply migrations after ${MAX_RETRIES} attempts."
    exit 1
  fi

  echo "[startup] Database not ready yet (attempt ${attempt}/${MAX_RETRIES}). Retrying in ${SLEEP_SECONDS}s..."
  attempt=$((attempt + 1))
  sleep "$SLEEP_SECONDS"
done

echo "[startup] Migrations applied successfully."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
