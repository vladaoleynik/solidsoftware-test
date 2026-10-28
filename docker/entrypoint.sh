#!/bin/sh
set -e

# Use the virtual environment directly
/app/.venv/bin/flask db upgrade

if [ "${SEED_DATA:-0}" = "1" ]; then
  /app/.venv/bin/python -m app.seed
fi

exec /app/.venv/bin/flask run --host=0.0.0.0 --port=8000
