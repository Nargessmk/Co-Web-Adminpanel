from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import DBAPIError, OperationalError

from Models.base import Base
from Models.calendar import Calendar
from Models.constant import Constant
from Models.permission import UserConstantPermission
from Models.entity_file_attachment import EntityFileAttachment
from Structure.repository import GenericRepository
from core.config import get_settings

settings = get_settings()
logger = logging.getLogger("app.db")


class UnitOfWork:
    def __init__(self, session: AsyncSession, application_id: UUID | None = None):
        self._session = session
        self._application_id = application_id
        self.constants = GenericRepository(session, Constant, application_id)
        self.calendars = GenericRepository(session, Calendar, application_id)
        self.permissions = GenericRepository(session, UserConstantPermission, application_id)
        self.entity_file_attachments = GenericRepository(session, EntityFileAttachment, application_id)

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def application_id(self) -> UUID | None:
        return self._application_id

    async def commit(self) -> None:
        await self._session.commit()

    async def flush(self) -> None:
        await self._session.flush()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()


class DatabaseManager:
    def __init__(self, database_url: str):
        if not database_url.startswith("mssql"):
            raise ValueError(
                f"Only SQL Server (mssql+aioodbc) is supported. Got: {database_url!r}"
            )

        # Connection timeout (seconds) to handle VPN latency and avoid hanging
        connect_args: dict = {"timeout": 30}

        self._engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,      # Automatically test connections before use to handle VPN drops
            pool_recycle=300,        # Recycle connections every 5 minutes to avoid idle drops
            connect_args=connect_args,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    @property
    def engine(self):
        return self._engine

    async def create_tables(self) -> None:
        """Create all tables in the database with resilience against VPN/network timeouts."""
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully.")
        except (DBAPIError, OperationalError, Exception) as exc:
            logger.warning("Could not auto-create tables during startup (VPN/network latency): %s", exc)

    async def close(self) -> None:
        """Dispose of database engine pools during shutdown."""
        if self._engine is not None:
            try:
                await self._engine.dispose()
            except Exception as e:
                logger.warning("Error disposing database engine: %s", e)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_uow(self, application_id: UUID | None = None) -> AsyncGenerator[UnitOfWork, None]:
        """Provides a scoped UnitOfWork instance tied to request/operation lifespan."""
        async with self._session_factory() as session:
            uow = UnitOfWork(session, application_id)
            try:
                yield uow
                await uow.commit()
            except Exception:
                await uow.rollback()
                raise
            finally:
                await uow.close()


_db_manager: DatabaseManager | None = None


def init_db(database_url: str) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_db_manager(database_url: str | None = None) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        target_url = database_url or settings.database_url
        _db_manager = DatabaseManager(target_url)
    return _db_manager