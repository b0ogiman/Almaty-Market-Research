"""APScheduler setup and job definitions."""

from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.core.redis_client import cache_delete_prefix
from app.logging_config import get_logger

logger = get_logger("jobs.scheduler")

_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def _run_collection_job() -> None:
    """Scheduled collection job: Avito mock (no API key required)."""
    from app.database import AsyncSessionLocal
    from app.collectors.avito_mock import AvitoMockCollector
    from app.collectors.pipeline import CollectionPipeline

    logger.info("Running scheduled collection job")
    async with AsyncSessionLocal() as db:
        try:
            collector = AvitoMockCollector()
            pipeline = CollectionPipeline(collector, db)
            result = await pipeline.run(limit=50)
            await db.commit()
            # New data affects analysis, opportunities, and recommendations.
            # Invalidate related caches so subsequent calls see fresh state.
            try:
                await cache_delete_prefix("analysis:")
                await cache_delete_prefix("opportunities:")
                await cache_delete_prefix("recommendations:")
            except Exception as cache_err:
                logger.debug("Cache invalidation after scheduled collection failed: %s", str(cache_err))
            logger.info(
                "Collection complete: source=%s, ingested=%d, duplicates=%d",
                result.source,
                result.ingested,
                result.duplicates,
            )
        except Exception as e:
            logger.exception("Scheduled collection failed: %s", str(e))
            await db.rollback()


def start_scheduler() -> None:
    """Start the scheduler with configured jobs."""
    settings = get_settings()
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled")
        return
    sched = get_scheduler()
    sched.add_job(
        _run_collection_job,
        trigger=CronTrigger(
            hour=settings.collection_cron_hour,
            minute=settings.collection_cron_minute,
        ),
        id="collection",
        replace_existing=True,
    )
    sched.start()
    logger.info(
        "Scheduler started (collection at %02d:%02d)",
        settings.collection_cron_hour,
        settings.collection_cron_minute,
    )


def stop_scheduler() -> None:
    """Stop the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
