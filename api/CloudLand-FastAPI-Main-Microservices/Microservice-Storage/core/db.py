"""Database (PostgreSQL) layer for Microservice-Storage.

Storage keeps its own lightweight async SQLAlchemy engine so it does not
depend on the shared Structure/DatabaseManager (which only supports
SQL Server / mssql+aioodbc). It connects to the same local PostgreSQL
instance used by the rest of CloudLand (see root .env: DB_* variables).

URL format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger("storage.db")

_engine = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def init_db(database_url: str):
    """Create the async engine + session factory.

    Returns the engine (or None when no database_url is configured so the
    service can still boot without database features).
    """
    global _engine, _session_factory

    if _engine is not None:
        return _engine

    if not database_url:
        logger.warning("No database_url configured — Storage database features disabled")
        return None

    if not database_url.startswith(("postgresql+asyncpg", "postgresql")):
        logger.warning(
            "Storage expects a PostgreSQL URL (postgresql+asyncpg://...), got: %r — "
            "connecting anyway, but the asyncpg driver may be required",
            database_url.split("@")[-1] if "@" in database_url else database_url,
        )

    # asyncpg-specific timeouts; keep connect_args minimal for other drivers
    connect_args: dict = {}
    if "asyncpg" in database_url:
        connect_args = {"timeout": 30, "command_timeout": 30}

    _engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,   # re-test stale connections before use
        pool_recycle=300,     # recycle connections every 5 minutes
        connect_args=connect_args,
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    logger.info("Storage database engine initialized (%s)", database_url.split("@")[-1])
    return _engine


def get_session_factory() -> Optional[async_sessionmaker[AsyncSession]]:
    return _session_factory


async def check_db_connection() -> bool:
    """Run a lightweight `SELECT 1` against the database. Never raises."""
    if _engine is None:
        return False
    try:
        async with _engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Storage database connection check failed: %s", exc)
        return False


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Scoped session with automatic commit/rollback.

    Raises RuntimeError when the database was not configured.
    """
    if _session_factory is None:
        raise RuntimeError("Database not configured: set database_url / STORAGE_DATABASE_URL")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_db() -> None:
    """Dispose of the engine pool on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        try:
            await _engine.dispose()
        except Exception as exc:
            logger.warning("Error disposing Storage database engine: %s", exc)
    _engine = None
    _session_factory = None