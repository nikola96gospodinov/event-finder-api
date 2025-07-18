#!/bin/bash

PORT=${PORT:-8000}

echo "Starting Event Finder API on port $PORT"

exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1