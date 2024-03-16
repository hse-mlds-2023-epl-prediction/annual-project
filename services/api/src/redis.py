import redis

from src.config import settings


def cache():
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
