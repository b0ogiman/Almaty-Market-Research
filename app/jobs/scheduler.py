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
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def _save_snapshot(db) -> None:
    """Aggregate current listings into a daily MarketSnapshot."""
    from datetime import date
    from collections import defaultdict
    from sqlalchemy import select, func
    from app.models.business_listing import BusinessListing
    from app.models.market_snapshot import MarketSnapshot

    today = date.today()
    stmt = (
        select(
            BusinessListing.district_mapped,
            BusinessListing.category_normalized,
            func.count().label("cnt"),
            func.avg(BusinessListing.rating).label("avg_rating"),
            func.avg(BusinessListing.review_count).label("avg_reviews"),
        )
        .where(BusinessListing.is_active == True)
        .where(BusinessListing.district_mapped.isnot(None))
        .group_by(BusinessListing.district_mapped, BusinessListing.category_normalized)
    )
    rows = (await db.execute(stmt)).all()

    # compute max count per district for competition_index
    district_totals: dict[str, int] = defaultdict(int)
    for row in rows:
        district_totals[row.district_mapped] += row.cnt
    max_total = max(district_totals.values(), default=1)

    for row in rows:
        district = row.district_mapped
        category = row.category_normalized or "other"
        competition_index = district_totals[district] / max_total

        existing = (
            await db.execute(
                select(MarketSnapshot).where(
                    MarketSnapshot.snapshot_date == today,
                    MarketSnapshot.district == district,
                    MarketSnapshot.category == category,
                )
            )
        ).scalar_one_or_none()

        if existing:
            existing.business_count = row.cnt
            existing.avg_rating = row.avg_rating
            existing.avg_review_count = row.avg_reviews
            existing.competition_index = competition_index
        else:
            db.add(MarketSnapshot(
                snapshot_date=today,
                district=district,
                category=category,
                business_count=row.cnt,
                avg_rating=row.avg_rating,
                avg_review_count=row.avg_reviews,
                competition_index=competition_index,
            ))

    logger.info("Snapshots saved for %d district/category pairs (date=%s)", len(rows), today)


async def _run_collection_job() -> None:
    """Scheduled collection job: 2GIS data."""
    from app.database import AsyncSessionLocal
    from app.collectors.twogis import TwoGisCollector
    from app.collectors.pipeline import CollectionPipeline

    logger.info("Running scheduled collection job (2GIS)")
    async with AsyncSessionLocal() as db:
        try:
            collector = TwoGisCollector()
            pipeline = CollectionPipeline(collector, db)
            result = await pipeline.run(query="бизнес Алматы", limit=100)
            await _save_snapshot(db)
            await db.commit()
            try:
                await cache_delete_prefix("analysis:")
                await cache_delete_prefix("opportunities:")
                await cache_delete_prefix("recommendations:")
                await cache_delete_prefix("trends:")
            except Exception as cache_err:
                logger.debug("Cache invalidation failed: %s", str(cache_err))
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
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
