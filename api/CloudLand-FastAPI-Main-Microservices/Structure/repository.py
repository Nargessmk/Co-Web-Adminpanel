from typing import Any, TypeVar, Generic, Sequence, cast
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from Models.base import Base

T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T], application_id: UUID | None = None):
        self._session = session
        self._model = model
        self._application_id = application_id
        self._tenant_scoped = getattr(model, "__tenant_scoped__", True)

    def _apply_tenant_filter(self, stmt):
        if self._tenant_scoped and self._application_id is not None:
            model = cast(Any, self._model)
            stmt = stmt.where(model.application_id == self._application_id)
        return stmt

    async def find(self, id: UUID) -> T | None:
        stmt = select(self._model).where(self._model.id == id)
        stmt = self._apply_tenant_filter(stmt)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self) -> Sequence[T]:
        stmt = select(self._model)
        stmt = self._apply_tenant_filter(stmt)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, entity: T) -> T:
        if self._tenant_scoped and self._application_id is not None:
            entity.application_id = self._application_id
        self._session.add(entity)
        return entity

    async def add_range(self, entities: Sequence[T]) -> None:
        for entity in entities:
            if self._tenant_scoped and self._application_id is not None:
                entity.application_id = self._application_id
        self._session.add_all(entities)

    async def update(self, entity: T) -> T:
        return await self._session.merge(entity)

    async def delete(self, id: UUID) -> int:
        model = cast(Any, self._model)
        stmt = delete(model).where(model.id == id)
        stmt = self._apply_tenant_filter(stmt)
        result = await self._session.execute(stmt)
        cursor = cast("CursorResult[Any]", result)
        rowcount = cursor.rowcount
        return int(rowcount if rowcount is not None else 0)

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._model)
        stmt = self._apply_tenant_filter(stmt)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def paginate(self, page: int, size: int) -> tuple[Sequence[T], int]:
        total_stmt = select(func.count()).select_from(self._model)
        total_stmt = self._apply_tenant_filter(total_stmt)
        total_result = await self._session.execute(total_stmt)
        total = int(total_result.scalar_one())

        offset = (page - 1) * size
        stmt = select(self._model)
        stmt = self._apply_tenant_filter(stmt)
        stmt = stmt.offset(offset).limit(size)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def find_by_parent(self, parent_id: UUID) -> Sequence[T]:
        model = cast(Any, self._model)
        stmt = select(self._model).where(model.parent_id == parent_id)
        stmt = self._apply_tenant_filter(stmt)
        result = await self._session.execute(stmt)
        return result.scalars().all()