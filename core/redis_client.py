from upstash_redis import Redis

from core.config import settings

redis_client = Redis(
    url=settings.UPSTASH_REDIS_REST_URL,
    token=settings.UPSTASH_REDIS_REST_TOKEN,
)
