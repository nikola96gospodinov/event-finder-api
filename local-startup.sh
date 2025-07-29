#!/bin/bash

echo "Stopping existing processes..."
pkill -f "uvicorn" || true

sleep 2

echo "Starting FastAPI server..."
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080 &
UVICORN_PID=$!

echo "FastAPI server started with PID: $UVICORN_PID"
echo "Server is running at http://localhost:8080"
echo "Health check available at http://localhost:8080/health"

wait $UVICORN_PID