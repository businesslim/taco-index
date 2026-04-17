#!/bin/sh
set -e
echo "Running database migrations..."
python -m alembic upgrade head
echo "Seeding influencer data..."
python -m app.influencer.seed
echo "Populating X user IDs (skips already-filled)..."
python -m app.influencer.populate_user_ids
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level warning
