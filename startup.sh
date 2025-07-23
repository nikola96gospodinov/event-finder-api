#!/bin/bash

PORT=${PORT:-8080}

echo "Starting Event Finder API on port $PORT"

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.celery_app worker --loglevel=info --detach

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1