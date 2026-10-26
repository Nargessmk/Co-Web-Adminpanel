"""
Response caching — mirrors C# ResponseCaching + OutputCache with 10min TTL.

Uses a simple function-level cache instead of ASGI middleware to avoid
conflicts with Starlette's BaseHTTPMiddleware chain.
"""

import time
from typing import Any

from core.logging import get_logger

logger = get_logger("app.cache")

_DEFAULT_TTL = 600  # 10 minutes, matching C# OutputCache


class ResponseCache:
    """In-memory TTL cache for GET responses.

    Mirrors C# OutputCache with 10-minute expiry.
    Only caches successful (2xx) GET responses.
    """

    def __init__(self, ttl: int = _DEFAULT_TTL):
        self._ttl = ttl
        self._store: dict[str, tuple[float, Any]] = {}

    def _make_key(self, method: str, path: str, query: str) -> str:
        return f"{method}:{path}:{query}"

    def get(self, method: str, path: str, query: str = "") -> Any | None:
        key = self._make_key(method, path, query)
        if key in self._store:
            cached_time, cached_value = self._store[key]
            if time.time() - cached_time < self._ttl:
                logger.debug("Cache HIT: %s", key)
                return cached_value
            del self._store[key]
        return None

    def set(self, method: str, path: str, query: str, value: Any) -> None:
        key = self._make_key(method, path, query)
        self._store[key] = (time.time(), value)
        logger.debug("Cache SET: %s", key)

    def clear(self) -> None:
        self._store.clear()

    def cleanup(self) -> int:
        """Remove expired entries. Returns count of removed items."""
        now = time.time()
        expired = [k for k, (t, _) in self._store.items() if now - t >= self._ttl]
        for k in expired:
            del self._store[k]
        return len(expired)


# Global instance — shared across the application
response_cache = ResponseCache()
