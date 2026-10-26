import logging
from typing import Any
from uuid import UUID

from core.config import get_settings

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

_redis: Any = None


def get_redis() -> Any:
    global _redis
    if _redis is None:
        if aioredis is None:
            return None
        settings = get_settings()
        try:
            _redis = aioredis.from_url(
                f"redis{'s' if settings.redis_ssl else ''}://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                password=settings.redis_password,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )
        except Exception:
            logger.warning("Failed to create Redis client, falling back to DB")
            _redis = None
    return _redis


async def cache_get(key: str) -> str | None:
    return None

async def cache_set(key: str, value: str, expiration_seconds: int) -> None:
    pass

async def cache_remove(key: str) -> None:
    pass


async def invalidate_constant_cache(application_id: UUID | None = None) -> None:
    pass

async def invalidate_calendar_cache() -> None:
    pass
