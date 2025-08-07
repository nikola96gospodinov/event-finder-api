from datetime import date, datetime
from typing import Optional, Union

from supabase import Client

from core.logging_config import get_logger
from core.supabase_client import supabase_base

logger = get_logger(__name__)


class UserRunService:
    """Service for handling user run operations"""

    def __init__(self):
        pass

    async def get_user_subscription_type(self, user_id: str) -> str:
        """
        Get the user's subscription type by checking the subscriptions table
        Returns: 'free', 'premium', or 'unlimited'
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return "free"

        try:
            response = (
                self.client.table("subscriptions")
                .select("subscription_type, is_active")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )

            if response.data and len(response.data) > 0:
                subscription_type = response.data[0].get("subscription_type", "free")
                subscription_type_str = (
                    str(subscription_type) if subscription_type else "free"
                )
                logger.info(
                    f"User {user_id} has active subscription: {subscription_type_str}"
                )
                return subscription_type_str
            else:
                logger.info(f"User {user_id} has no active subscription")
                return "free"

        except Exception as e:
            logger.error(f"Error checking user subscription: {e}")
            return "free"

    async def get_max_runs_per_month(self, user_id: str) -> Union[int, float]:
        """
        Get the maximum number of runs per month based on user's subscription
        """
        subscription_type = await self.get_user_subscription_type(user_id)

        if subscription_type == "unlimited":
            return float("inf")
        elif subscription_type == "premium":
            return 5
        else:
            return 2

    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client from the base class"""
        return supabase_base.client

    async def check_user_run_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded their monthly run limit based on their subscription
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            max_runs = await self.get_max_runs_per_month(user_id)

            if max_runs == float("inf"):
                logger.info(f"User {user_id} has unlimited runs")
                return True

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

                if current_month_runs >= max_runs:
                    logger.info(
                        (
                            f"User {user_id} has already run {current_month_runs} "
                            f"times this month (limit: {max_runs})"
                        )
                    )
                    return False
                else:
                    logger.info(
                        f"User {user_id} has {current_month_runs} runs this month, can "
                        f"run {max_runs - current_month_runs} more times"
                    )
                    return True
            else:
                logger.info(
                    f"User {user_id} has no previous runs, can run up to "
                    f"{max_runs} times this month"
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

    async def revert_user_run(self, user_id: str) -> bool:
        """Revert a user run"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            latest_run = (
                self.client.table("runs")
                .select("id")
                .eq("user_id", user_id)
                .order("run_date", desc=True)
                .limit(1)
                .execute()
            )
            if latest_run.data and len(latest_run.data) > 0:
                run_id = latest_run.data[0]["id"]
                self.client.table("runs").delete().eq("id", run_id).execute()
                return True
            else:
                logger.error(f"No runs found for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error reverting user run: {e}")
            return False


user_run_service = UserRunService()
