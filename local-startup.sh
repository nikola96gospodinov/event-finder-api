#!/bin/bash

PORT=${PORT:-8080}

echo "Starting Event Finder API on port $PORT"

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null
    fi
    if [ ! -z "$UVICORN_PID" ]; then
        kill $UVICORN_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.celery_app worker --loglevel=info --concurrency=1 &
CELERY_PID=$!

# Start FastAPI in the background
echo "Starting FastAPI application..."
uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1 &
UVICORN_PID=$!

# Wait for both processes
wait $CELERY_PID $UVICORN_PID