"""
Cloud Run Jobs service for executing background tasks.
"""

import time
from typing import Optional

from google.cloud import run_v2

from core.config import settings


class CloudRunJobsService:
    """Service for managing Cloud Run Jobs execution."""

    def __init__(self):
        self.jobs_client = run_v2.JobsClient()
        self.executions_client = run_v2.ExecutionsClient()
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.region = settings.GOOGLE_CLOUD_REGION
        self.job_name = settings.CLOUD_RUN_JOB_NAME

    def execute_job(self) -> str:
        """
        Execute the agent job on Cloud Run Jobs asynchronously.

        Returns:
            A unique task ID for tracking the job execution

        Raises:
            Exception: If the job fails to start
        """
        job_path = self.jobs_client.job_path(
            project=self.project_id, location=self.region, job=self.job_name
        )

        try:
            operation = self.jobs_client.run_job(name=job_path)

            if operation is None:
                raise Exception("Failed to create job operation")

            timestamp = int(time.time())
            task_id = f"{self.job_name}_{timestamp}"

            return task_id

        except Exception as e:
            raise Exception(f"Failed to start Cloud Run Job: {str(e)}")

    def get_execution_status(self, execution_name: str) -> Optional[str]:
        """
        Get the status of a job execution.

        Args:
            execution_name: The name of the execution to check

        Returns:
            The status of the execution, or None if not found
        """
        try:
            execution = self.executions_client.get_execution(name=execution_name)
            return execution.conditions[0].type if execution.conditions else None
        except Exception:
            return None


cloud_run_service = CloudRunJobsService()
