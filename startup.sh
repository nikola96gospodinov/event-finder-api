#!/bin/bash

echo "Starting Event Finder API with supervisor..."

# Start supervisor which will manage both FastAPI and Celery
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf