#!/bin/sh

set -eu

if [ -z "${DATABASE_URL:-}" ]; then
    echo "DATABASE_URL is required." >&2
    exit 1
fi

if [ -n "${RAILWAY_ENVIRONMENT:-}" ]; then
    case "$DATABASE_URL" in
        *localhost*|*127.0.0.1*)
            echo "DATABASE_URL cannot use localhost on Railway. Add a reference to the Railway PostgreSQL service." >&2
            exit 1
            ;;
    esac
fi

case "$DATABASE_URL" in
    postgresql://*)
        DATABASE_URL="postgresql+psycopg://${DATABASE_URL#postgresql://}"
        ;;
    postgres://*)
        DATABASE_URL="postgresql+psycopg://${DATABASE_URL#postgres://}"
        ;;
esac

export DATABASE_URL

../.venv/bin/pelican up
../.venv/bin/python -m app.seed

exec ../.venv/bin/fastapi run app/main.py \
    --host 0.0.0.0 \
    --port "${PORT:-8000}"
