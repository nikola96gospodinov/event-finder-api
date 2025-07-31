#!/bin/bash

# Test Cloud Run Job locally
# This script builds and runs the job locally to verify it works

set -e

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "Loaded GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."  # Show first 10 chars for verification
else
    echo "Warning: .env file not found"
fi

# Create a test user profile JSON
TEST_USER_PROFILE='{
    "birth_date": "1996-06-14T00:00:00",
    "gender": "male",
    "sexual_orientation": "straight",
    "relationship_status": "in a relationship",
    "willingness_to_pay": true,
    "budget": 50,
    "willingness_for_online": false,
    "acceptable_times": {
        "weekdays": {
            "start": "17:00",
            "end": "22:00"
        },
        "weekends": {
            "start": "8:00",
            "end": "23:00"
        }
    },
    "location": {
        "latitude": 51.5253263,
        "longitude": -0.1015115,
        "country": "United Kingdom",
        "city": "London",
        "country_code": "gb"
    },
    "distance_threshold": {
        "distance_threshold": 20,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 240,
    "interests": ["technology", "coding", "JavaScript", "Python", "AI", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "biohacking", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "phone free", "architecture", "interior design"],
    "goals": ["make new friends", "find a business partner"],
    "occupation": "software engineer",
    "email": "nikola96gospodinov@gmail.com"
}'

echo "Testing Cloud Run Job locally..."

echo "Building Docker image..."
docker build -f Dockerfile.job -t event-finder-job-test . --no-cache=false

echo "Running job locally..."
docker run --rm \
    -e CLOUD_RUN_JOB="test-agent-job" \
    -e CLOUD_RUN_TASK_INDEX="0" \
    -e CLOUD_RUN_TASK_COUNT="1" \
    -e ENVIRONMENT="local" \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e SUPABASE_URL="$SUPABASE_URL" \
    -e SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
    -e SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    -e MAILGUN_API_KEY="$MAILGUN_API_KEY" \
    -e MAILGUN_DOMAIN="$MAILGUN_DOMAIN" \
    -e UPSTASH_REDIS_REST_URL="$UPSTASH_REDIS_REST_URL" \
    -e UPSTASH_REDIS_REST_TOKEN="$UPSTASH_REDIS_REST_TOKEN" \
    -e SCRAPPEY_API_KEY="$SCRAPPEY_API_KEY" \
    -e GOOGLE_CLOUD_PROJECT="$GOOGLE_CLOUD_PROJECT" \
    -e GOOGLE_CLOUD_REGION="$GOOGLE_CLOUD_REGION" \
    -e CLOUD_RUN_JOB_NAME="$CLOUD_RUN_JOB_NAME" \
    event-finder-job-test \
    --user_profile "$TEST_USER_PROFILE" \
    --only_highly_relevant false

echo "Local test completed!"