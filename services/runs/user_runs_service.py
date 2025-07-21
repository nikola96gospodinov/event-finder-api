from datetime import date, datetime
from typing import Optional

from supabase import Client

from core.logging_config import get_logger
from core.supabase_client import supabase_base

logger = get_logger(__name__)


class UserRunService:
    """Service for handling user run operations"""

    def __init__(self):
        # TODO: Make this configurable
        self.MAX_RUNS_PER_MONTH = 2

    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client from the base class"""
        return supabase_base.client

    async def check_user_run_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded their monthly
        run limit (max 2 runs per calendar month)
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            current_date = date.today()
            current_month = current_date.month
            current_year = current_date.year

            response = (
                self.client.table("runs").select("*").eq("user_id", user_id).execute()
            )

            if response.data:
                current_month_runs = 0
                for run in response.data:
                    run_date_str = run.get("run_date")
                    if run_date_str:
                        try:
                            run_date = datetime.fromisoformat(
                                run_date_str.replace("Z", "+00:00")
                            ).date()
                            if (
                                run_date.month == current_month
                                and run_date.year == current_year
                            ):
                                current_month_runs += 1
                        except (ValueError, TypeError) as e:
                            logger.error(f"Error parsing run_date: {e}")
                            continue

                if current_month_runs >= self.MAX_RUNS_PER_MONTH:
                    logger.info(
                        (
                            f"User {user_id} has already run {current_month_runs} "
                            f"times this month (limit: {self.MAX_RUNS_PER_MONTH})"
                        )
                    )
                    return False
                else:
                    logger.info(
                        f"User {user_id} has {current_month_runs} runs this month, can "
                        f"run {self.MAX_RUNS_PER_MONTH - current_month_runs} more times"
                    )
                    return True
            else:
                logger.info(
                    f"User {user_id} has no previous runs, can run up to "
                    f"{self.MAX_RUNS_PER_MONTH} times this month"
                )
                return True

        except Exception as e:
            logger.error(f"Error checking user run limit: {e}")
            return False

    async def record_user_run(self, user_id: str) -> bool:
        """Record a new run for the user"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            response = (
                self.client.table("runs")
                .insert({"user_id": user_id, "run_date": datetime.now().isoformat()})
                .execute()
            )

            if response.data:
                logger.info(f"Successfully recorded run for user {user_id}")
                return True
            else:
                logger.error(f"Failed to record run for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error recording user run: {e}")
            return False


user_run_service = UserRunService()
