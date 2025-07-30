#!/usr/bin/env python3
"""
Simple Test Job for Google Cloud Run Jobs.
This job is for testing purposes only and doesn't perform any actual work.
"""

import argparse
import os
import sys
from datetime import datetime

# from utils.user_profile_utils import convert_from_json_to_user_profile

print("=" * 50)
print("SIMPLE TEST JOB STARTED")
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

print(f"only_highly_relevant: {only_highly_relevant}")
print(f"user_profile: {user_profile_json}")

# if user_profile_json != "Not provided":
#     try:
#         user_profile = convert_from_json_to_user_profile(user_profile_json)
#         print(f"Parsed user_profile: {user_profile}")
#     except json.JSONDecodeError:
#         print("\nCould not parse user_profile as JSON")

print("\nThis is a simple test job that does nothing but print information.")
print("It's used for testing Cloud Run Jobs functionality.")

print("\n" + "=" * 50)
print("SIMPLE TEST JOB COMPLETED SUCCESSFULLY")
print("=" * 50)

sys.exit(0)
