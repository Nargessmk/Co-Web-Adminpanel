import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import get_settings
from services.reindex_service import ReindexJobService

logger = logging.getLogger("background_task.scheduler")
settings = get_settings()

_scheduler: Optional[AsyncIOScheduler] = None


async def scheduled_weekly_reindex():
    logger.info("Executing scheduled weekly reindex job...")
    try:
        res = await ReindexJobService.execute_reindex_all_job_async()
        logger.info(f"Scheduled weekly reindex job completed. Result: {res}")
    except Exception as e:
        logger.error(f"Scheduled weekly reindex job failed: {e}", exc_info=True)


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def start_scheduler():
    scheduler = get_scheduler()

    # Register weekly reindex cron job (Default: Friday at 16:00 UTC -> matching C# 0 16 * * 5)
    trigger = CronTrigger(
        day_of_week=settings.reindex_cron_day_of_week,
        hour=settings.reindex_cron_hour,
        minute=settings.reindex_cron_minute,
        timezone="UTC",
    )

    scheduler.add_job(
        scheduled_weekly_reindex,
        trigger=trigger,
        id="weekly-reindex-all",
        name="Weekly Reindex All Job",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. Registered 'weekly-reindex-all' cron job ({settings.reindex_cron_day_of_week.upper()} at {settings.reindex_cron_hour:02d}:{settings.reindex_cron_minute:02d} UTC)."
    )


def shutdown_scheduler():
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown successfully.")
        _scheduler = None
