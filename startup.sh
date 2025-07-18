#!/bin/bash

PORT=${PORT:-8000}

echo "Checking Playwright browsers..."
if [ ! -d "/opt/render/.cache/ms-playwright" ]; then
    echo "Installing Playwright browsers..."
    playwright install chromium --with-deps
fi

echo "Starting Event Finder API on port $PORT"

exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1