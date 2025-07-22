import asyncio
from typing import Any, Dict

from app.celery_app import celery_app
from core.logging_config import get_logger
from models.user_profile_model import UserProfile
from services.agent.agent import agent

logger = get_logger(__name__)


@celery_app.task(name="tasks.run_agent_task")
def run_agent_task(
    user_profile_dict: Dict[str, Any], only_highly_relevant: bool = False
):
    """Run agent task with proper serialization handling"""
    try:
        user_profile = UserProfile(**user_profile_dict)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent(user_profile, only_highly_relevant))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in run_agent_task: {str(e)}")
        raise
