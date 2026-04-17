#!/bin/sh
set -e
echo "Running database migrations..."
python -m alembic upgrade head
echo "Seeding influencer data..."
python -m app.influencer.seed
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level warning
