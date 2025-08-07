#!/usr/bin/env python3
"""
Agent Job for Google Cloud Run Jobs.
This job executes the event finding agent directly.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

# Import the agent function directly
from core.logging_config import setup_logging
from services.agent.agent import agent
from utils.user_profile_utils import convert_from_json_to_user_profile

# Set up logging configuration
setup_logging(log_level="INFO")

print("=" * 50)
print("AGENT JOB STARTED")
print("=" * 50)

print(f"Timestamp: {datetime.utcnow().isoformat()}")
print(f"Python version: {sys.version}")
print(f"Job name: {os.environ.get('CLOUD_RUN_JOB', 'Unknown')}")
print(f"Task index: {os.environ.get('CLOUD_RUN_TASK_INDEX', 'Unknown')}")
print(f"Task count: {os.environ.get('CLOUD_RUN_TASK_COUNT', 'Unknown')}")
print(f"Environment: {os.environ.get('ENVIRONMENT', 'Unknown')}")

# Parse command line arguments
parser = argparse.ArgumentParser(description="Agent job with parameters")
parser.add_argument(
    "--only_highly_relevant", type=str, help="Only highly relevant events"
)
parser.add_argument("--user_profile", type=str, help="User profile JSON")

args = parser.parse_args()

print("\n" + "=" * 30)
print("PARAMETERS FROM API")
print("=" * 30)

only_highly_relevant = args.only_highly_relevant or "Not provided"
user_profile_json = args.user_profile or "Not provided"
user_id = args.user_id or "Not provided"

print(f"only_highly_relevant: {only_highly_relevant}")
print(f"user_profile: {user_profile_json}")

if user_profile_json == "Not provided":
    print("ERROR: user_profile parameter is required")
    sys.exit(1)

try:
    user_profile = convert_from_json_to_user_profile(user_profile_json)
    if user_profile is None:
        print("ERROR: Could not convert user_profile - returned None")
        sys.exit(1)
    print(f"Parsed user_profile: {user_profile}")
except json.JSONDecodeError as e:
    print(f"ERROR: Could not parse user_profile as JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Could not convert user_profile: {e}")
    sys.exit(1)

# Convert only_highly_relevant to boolean
only_highly_relevant_bool = False
if only_highly_relevant.lower() in ["true", "1", "yes", "on"]:
    only_highly_relevant_bool = True

print(f"only_highly_relevant (boolean): {only_highly_relevant_bool}")
print(f"user_id: {user_id}")

print("\n" + "=" * 30)
print("EXECUTING AGENT")
print("=" * 30)

try:
    # Run the agent function directly
    asyncio.run(agent(user_profile, user_id, only_highly_relevant_bool))
    print("Agent execution completed successfully")
except Exception as e:
    print(f"ERROR: Agent execution failed: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("AGENT JOB COMPLETED SUCCESSFULLY")
print("=" * 50)

sys.exit(0)
