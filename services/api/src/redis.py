import redis

from src.config import settings

DEFAULT_CACHE_TTL = 3600

def cache():
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
