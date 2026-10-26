"""Base repository providing database access primitives."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from .. import db


class BaseRepository:
    """Base repository encapsulating db interaction for dependency injection."""

    def __init__(self):
        self.db = db

    async def fetch(self, query: str, *args: Any) -> list[Any]:
        return await self.db.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[Any]:
        return await self.db.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        return await self.db.fetchval(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        return await self.db.execute(query, *args)
