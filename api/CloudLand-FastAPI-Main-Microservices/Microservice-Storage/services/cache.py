"""
Redis caching layer and session management for Storage Microservice.
Mirrors the C# StackExchange.Redis IDistributedCache usage pattern.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class RedisCache:
    """Async Redis client wrapper for caching in Storage microservice."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        ssl: bool = False,
        prefix: str = "cloudland:storage:",
        default_ttl: int = 3600,
    ) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._ssl = ssl
        self._prefix = prefix
        self._default_ttl = default_ttl
        self._client = None

    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                ssl=self._ssl,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            await self._client.ping()
            logger.info("Redis connected successfully at %s:%s", self._host, self._port)
        except ImportError:
            logger.warning("redis package not installed — cache disabled")
            self._client = None
        except Exception as exc:
            logger.warning("Redis connection failed: %s — cache disabled", exc)
            self._client = None

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def _key(self, key: str) -> str:
        """Prefix a key with the namespace."""
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> str | None:
        """Get a cached value."""
        if not self._client:
            return None
        return await self._client.get(self._key(key))

    async def set(
        self, key: str, value: str, ttl_seconds: int | None = None
    ) -> None:
        """Set a cached value with optional TTL."""
        if not self._client:
            return
        full_key = self._key(key)
        if ttl_seconds is None:
            ttl_seconds = self._default_ttl
        await self._client.setex(full_key, ttl_seconds, value)

    async def get_json(self, key: str) -> Any | None:
        """Get a cached JSON value."""
        raw = await self.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def set_json(
        self, key: str, value: Any, ttl_seconds: int | None = None
    ) -> None:
        """Set a JSON value in cache."""
        await self.set(key, json.dumps(value), ttl_seconds)

    async def delete(self, key: str) -> None:
        """Delete a cached key."""
        if not self._client:
            return
        await self._client.delete(self._key(key))


_cache: RedisCache | None = None


def get_cache(
    host: str | None = None,
    port: int | None = None,
    db: int | None = None,
    password: str | None = None,
    ssl: bool | None = None,
) -> RedisCache:
    """Return the shared RedisCache instance (created lazily)."""
    global _cache
    if _cache is None:
        from core.config import get_settings
        settings = get_settings()
        _cache = RedisCache(
            host=host or settings.redis_host,
            port=port or settings.redis_port,
            db=db if db is not None else settings.redis_db,
            password=password if password is not None else settings.redis_password,
            ssl=ssl if ssl is not None else settings.redis_ssl,
        )
    return _cache


async def close_cache() -> None:
    """Close the shared Redis connection."""
    global _cache
    if _cache is not None:
        await _cache.close()
        _cache = None
