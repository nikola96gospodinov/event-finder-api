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
        self.jobs_client = run_v2.JobsAsyncClient()
        self.executions_client = run_v2.ExecutionsAsyncClient()
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.region = settings.GOOGLE_CLOUD_REGION
        self.job_name = settings.CLOUD_RUN_JOB_NAME

    async def execute_job(self, parameters: Optional[dict] = None) -> str:
        """
        Execute the agent job on Cloud Run Jobs asynchronously.

        Args:
            parameters: Dictionary of parameters to pass to the job

        Returns:
            A unique task ID for tracking the job execution

        Raises:
            Exception: If the job fails to start
        """
        job_path = self.jobs_client.job_path(
            project=self.project_id, location=self.region, job=self.job_name
        )

        try:
            args = []
            if parameters:
                for key, value in parameters.items():
                    args.extend([f"--{key}", str(value)])

            request = run_v2.RunJobRequest(
                name=job_path,
                overrides=run_v2.RunJobRequest.Overrides(
                    container_overrides=[
                        run_v2.RunJobRequest.Overrides.ContainerOverride(args=args)
                    ]
                ),
            )

            operation = await self.jobs_client.run_job(request=request)

            if operation is None:
                raise Exception("Failed to create job operation")

            timestamp = int(time.time())
            task_id = f"{self.job_name}_{timestamp}"

            return task_id

        except Exception as e:
            raise Exception(f"Failed to start Cloud Run Job: {str(e)}")

    async def get_execution_status(self, execution_name: str) -> Optional[str]:
        """
        Get the status of a job execution.

        Args:
            execution_name: The name of the execution to check

        Returns:
            The status of the execution, or None if not found
        """
        try:
            execution = await self.executions_client.get_execution(name=execution_name)
            return execution.conditions[0].type if execution.conditions else None
        except Exception:
            return None


cloud_run_service = CloudRunJobsService()
