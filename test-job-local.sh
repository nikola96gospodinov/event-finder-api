#!/bin/bash

# Test Cloud Run Job locally
# This script builds and runs the job locally to verify it works

set -e

echo "Testing Cloud Run Job locally..."

echo "Building Docker image..."
docker build -f Dockerfile.job -t event-finder-job-test .

echo "Running job locally..."
docker run --rm \
    -e CLOUD_RUN_JOB="test-agent-job" \
    -e CLOUD_RUN_TASK_INDEX="0" \
    -e CLOUD_RUN_TASK_COUNT="1" \
    -e ENVIRONMENT="local" \
    event-finder-job-test

echo "Local test completed!"