#!/bin/sh
set -e

flask db upgrade

if [ "${SEED_DATA:-0}" = "1" ]; then
  python -m app.seed
fi

exec flask run --host=0.0.0.0 --port=8000
