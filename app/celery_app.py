from celery import Celery

from core.logging_config import get_logger
from core.upstash_connection_link import get_upstash_redis_url

logger = get_logger(__name__)

try:
    redis_url = get_upstash_redis_url()
    logger.info(
        f"Connecting to Redis: "
        f"{redis_url.split('@')[1] if '@' in redis_url else redis_url}"
    )

    celery_app = Celery(
        "event_finder_worker",
        broker=redis_url,
        backend=redis_url,
        include=["app.tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
        broker_connection_retry_on_startup=True,
        task_acks_late=True,
        worker_disable_rate_limits=False,
        task_time_limit=60 * 60 * 3,  # 3 hours
        task_soft_time_limit=60 * 60 * 2,  # 2 hours
        result_expires=60 * 60 * 24,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        worker_send_task_events=True,
        task_send_sent_event=True,
        worker_cancel_long_running_tasks_on_connection_loss=True,
    )

    celery_app.autodiscover_tasks(["app.tasks"])

    logger.info("Celery app initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize Celery app: {str(e)}")
    raise
