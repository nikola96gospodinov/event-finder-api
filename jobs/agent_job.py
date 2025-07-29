#!/usr/bin/env python3
"""
Simple Test Job for Google Cloud Run Jobs.
This job is for testing purposes only and doesn't perform any actual work.
"""

import os
import sys
from datetime import datetime

print("=" * 50)
print("SIMPLE TEST JOB STARTED")
print("=" * 50)

print(f"Timestamp: {datetime.utcnow().isoformat()}")
print(f"Python version: {sys.version}")
print(f"Job name: {os.environ.get('CLOUD_RUN_JOB', 'Unknown')}")
print(f"Task index: {os.environ.get('CLOUD_RUN_TASK_INDEX', 'Unknown')}")
print(f"Task count: {os.environ.get('CLOUD_RUN_TASK_COUNT', 'Unknown')}")
print(f"Environment: {os.environ.get('ENVIRONMENT', 'Unknown')}")

print("\nThis is a simple test job that does nothing but print information.")
print("It's used for testing Cloud Run Jobs functionality.")

print("\n" + "=" * 50)
print("SIMPLE TEST JOB COMPLETED SUCCESSFULLY")
print("=" * 50)

sys.exit(0)
