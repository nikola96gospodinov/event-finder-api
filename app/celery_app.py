from celery import Celery

from core.upstash_connection_link import get_upstash_redis_url

celery_app = Celery(
    "event_finder_worker",
    broker=get_upstash_redis_url(),
    backend=get_upstash_redis_url(),
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
    task_time_limit=60 * 60 * 3,
    task_soft_time_limit=60 * 60 * 2,
    result_expires=60 * 60 * 24,
)

celery_app.autodiscover_tasks(["app.tasks"])
