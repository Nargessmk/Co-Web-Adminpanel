import asyncio
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select

from middleware.uow_middleware import get_current_uow
from Models.calendar import Calendar
from Models.constant import Constant
from Schema.AppManagement.calendar import CalendarDTO
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.reindex_result import ReindexResult
from services.elastic_client import (
    INDEX_CALENDAR,
    INDEX_CONSTANT,
    _dump,
    bulk_index,
    clear_index,
    get_es_client,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
SUPPORTED_VIEWS = ("Constant", "ConstantRecursive", "Calendar")


async def _fetch_constant_batch(offset: int, batch_size: int, application_id: UUID | None = None) -> list[Constant]:
    uow = get_current_uow()
    stmt = select(Constant).order_by(Constant.id).offset(offset).limit(batch_size)
    if application_id is not None:
        stmt = stmt.where(Constant.application_id == application_id)
    result = await uow.session.execute(stmt)
    return list(result.scalars().all())


async def _fetch_calendar_batch(offset: int, batch_size: int) -> list[Calendar]:
    uow = get_current_uow()
    stmt = select(Calendar).order_by(Calendar.id).offset(offset).limit(batch_size)
    result = await uow.session.execute(stmt)
    return list(result.scalars().all())



def _to_constant_dto(entity: Constant, recursive: bool) -> dict:
    dto = ConstantDTO.model_validate(entity)
    if recursive:
        dto.constant_type = None
    return _dump(dto)


def _to_calendar_dto(entity: Calendar) -> dict:
    return _dump(CalendarDTO.model_validate(entity))


async def reindex_by_view_name(view_name: str, application_id: UUID | None = None) -> ReindexResult:
    if view_name not in SUPPORTED_VIEWS:
        return ReindexResult.failure(f"View '{view_name}' is not supported for reindexing")

    client = get_es_client()
    if client is None:
        return ReindexResult.failure("Reindex failed: Elasticsearch is not configured")

    if view_name == "Calendar":
        index = INDEX_CALENDAR
        total_processed, total_errors = await _reindex_calendars(client)
    else:
        index = INDEX_CONSTANT
        recursive = view_name == "ConstantRecursive"
        total_processed, total_errors = await _reindex_constants(client, recursive, application_id)
    return ReindexResult.success(total_processed, total_errors)


async def _reindex_constants(client: Any, recursive: bool, application_id: UUID | None = None) -> tuple[int, int]:
    total_processed = 0
    total_errors = 0
    offset = 0
    try:
        while True:
            rows = await _fetch_constant_batch(offset, BATCH_SIZE, application_id)
            if not rows:
                break
            docs = [
                (str(entity.id), _to_constant_dto(entity, recursive)) for entity in rows
            ]
            if await bulk_index(INDEX_CONSTANT, docs):
                total_processed += len(rows)
            else:
                total_errors += len(rows)
            offset += BATCH_SIZE
            await asyncio.sleep(0.1)
        return total_processed, total_errors
    except Exception as e:
        raise RuntimeError(f"Reindex failed: {e}") from e


async def _reindex_calendars(client: Any) -> tuple[int, int]:
    total_processed = 0
    total_errors = 0
    offset = 0
    try:
        while True:
            rows = await _fetch_calendar_batch(offset, BATCH_SIZE)
            if not rows:
                break
            docs = [(str(entity.id), _to_calendar_dto(entity)) for entity in rows]
            if await bulk_index(INDEX_CALENDAR, docs):
                total_processed += len(rows)
            else:
                total_errors += len(rows)
            offset += BATCH_SIZE
            await asyncio.sleep(0.1)
        return total_processed, total_errors
    except Exception as e:
        raise RuntimeError(f"Reindex failed: {e}") from e


async def reindex_all(application_id: UUID | None = None) -> ReindexResult:
    client = get_es_client()
    if client is None:
        return ReindexResult.failure("Reindex failed: Elasticsearch is not configured")

    total_processed = 0
    total_errors = 0
    details: list[str] = []
    for view_name in SUPPORTED_VIEWS:
        result = await reindex_by_view_name(view_name, application_id)
        total_processed += result.processed_count
        total_errors += result.error_count
        details.append(
            f"{view_name}: {result.processed_count} processed, {result.error_count} errors"
        )
    return ReindexResult.success(total_processed, total_errors, details)
