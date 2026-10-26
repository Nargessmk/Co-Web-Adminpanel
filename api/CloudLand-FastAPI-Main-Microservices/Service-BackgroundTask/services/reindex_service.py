import asyncio
import logging
from typing import Any, List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select
from Models.calendar import Calendar
from Models.constant import Constant
from Schema.AppManagement.calendar import CalendarDTO
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.reindex_result import ReindexResult
from Structure.session import get_db_manager
from core.config import get_settings
from core.elastic import bulk_index, clear_index, get_es_client

logger = logging.getLogger("background_task.reindex")
settings = get_settings()

BATCH_SIZE = 100
INDEX_CONSTANT = "constants"
INDEX_CALENDAR = "calendars"
SUPPORTED_VIEWS = ("Constant", "ConstantRecursive", "Calendar")


def _dump(dto_instance: Any) -> dict:
    return dto_instance.model_dump(by_alias=True, mode="json")


def _to_constant_dto(entity: Constant, recursive: bool) -> dict:
    dto = ConstantDTO.model_validate(entity)
    if recursive:
        dto.constant_type = None
    return _dump(dto)


def _to_calendar_dto(entity: Calendar) -> dict:
    return _dump(CalendarDTO.model_validate(entity))


class ReindexJobService:
    """ReindexJobService matches the C# ReindexJobService logic, reading DB views via Structure and indexing into Elasticsearch."""

    @staticmethod
    async def execute_reindex_all_job_async(application_id: Optional[UUID] = None) -> ReindexResult:
        logger.info("Starting scheduled reindex job for all views...")
        total_processed = 0
        total_errors = 0
        details: List[str] = []

        for view_name in SUPPORTED_VIEWS:
            logger.info(f"Processing view: {view_name}")
            res = await ReindexJobService.execute_reindex_by_view_job_async(view_name, application_id)
            total_processed += res.processed_count
            total_errors += res.error_count
            details.append(f"{view_name}: {res.processed_count} processed, {res.error_count} errors")
            if not res.is_success:
                logger.error(f"Failed to reindex view {view_name}: {res.message}")

        logger.info(f"Scheduled reindex job completed. Total processed: {total_processed}, Total errors: {total_errors}")
        return ReindexResult.success(total_processed, total_errors, details)

    @staticmethod
    async def execute_reindex_by_view_job_async(view_name: str, application_id: Optional[UUID] = None) -> ReindexResult:
        if view_name not in SUPPORTED_VIEWS:
            return ReindexResult.failure(f"View '{view_name}' is not supported for reindexing")

        client = get_es_client()
        if client is None:
            return ReindexResult.failure("Reindex failed: Elasticsearch client not available")

        db_manager = get_db_manager(settings.database_url)

        try:
            if view_name == "Calendar":
                index_name = INDEX_CALENDAR
                await clear_index(index_name)
                total_processed, total_errors = await ReindexJobService._reindex_calendars(db_manager, index_name)
            else:
                index_name = INDEX_CONSTANT
                recursive = (view_name == "ConstantRecursive")
                await clear_index(index_name)
                total_processed, total_errors = await ReindexJobService._reindex_constants(db_manager, index_name, recursive, application_id)

            return ReindexResult.success(total_processed, total_errors)
        except Exception as e:
            logger.error(f"Error during reindex for view {view_name}: {e}", exc_info=True)
            return ReindexResult.failure(f"Reindex failed: {str(e)}")

    @staticmethod
    async def _reindex_constants(db_manager, index_name: str, recursive: bool, application_id: Optional[UUID]) -> Tuple[int, int]:
        total_processed = 0
        total_errors = 0
        offset = 0

        while True:
            async with db_manager.get_uow() as uow:
                stmt = select(Constant).order_by(Constant.id).offset(offset).limit(BATCH_SIZE)
                if application_id is not None:
                    stmt = stmt.where(Constant.application_id == application_id)
                exec_res = await uow.session.execute(stmt)
                rows = list(exec_res.scalars().all())

            if not rows:
                break

            docs = [(str(entity.id), _to_constant_dto(entity, recursive)) for entity in rows]
            success = await bulk_index(index_name, docs)
            if success:
                total_processed += len(rows)
            else:
                total_errors += len(rows)

            offset += BATCH_SIZE
            await asyncio.sleep(0.1)

        return total_processed, total_errors

    @staticmethod
    async def _reindex_calendars(db_manager, index_name: str) -> Tuple[int, int]:
        total_processed = 0
        total_errors = 0
        offset = 0

        while True:
            async with db_manager.get_uow() as uow:
                stmt = select(Calendar).order_by(Calendar.id).offset(offset).limit(BATCH_SIZE)
                exec_res = await uow.session.execute(stmt)
                rows = list(exec_res.scalars().all())

            if not rows:
                break

            docs = [(str(entity.id), _to_calendar_dto(entity)) for entity in rows]
            success = await bulk_index(index_name, docs)
            if success:
                total_processed += len(rows)
            else:
                total_errors += len(rows)

            offset += BATCH_SIZE
            await asyncio.sleep(0.1)

        return total_processed, total_errors
