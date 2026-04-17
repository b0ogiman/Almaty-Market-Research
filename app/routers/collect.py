"""Manual data collection trigger."""

import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.logging_config import get_logger

logger = get_logger("routers.collect")

router = APIRouter(prefix="/collect", tags=["collect"])

COLLECTION_QUERIES = [
    "кафе Алматы",
    "ресторан Алматы",
    "магазин Алматы",
    "салон красоты Алматы",
    "аптека Алматы",
    "фитнес Алматы",
    "стоматология Алматы",
    "супермаркет Алматы",
]


class CollectResponse(BaseModel):
    success: bool
    message: str


async def _do_collect() -> None:
    from app.database import AsyncSessionLocal
    from app.collectors.twogis import TwoGisCollector
    from app.collectors.pipeline import CollectionPipeline
    from app.jobs.scheduler import _save_snapshot
    from app.core.redis_client import cache_delete_prefix

    collector = TwoGisCollector()
    total_ingested = 0

    for query in COLLECTION_QUERIES:
        async with AsyncSessionLocal() as db:
            try:
                pipeline = CollectionPipeline(collector, db)
                result = await pipeline.run(query=query, limit=50)
                await db.commit()
                total_ingested += result.ingested
                logger.info("Collected [%s]: ingested=%d dupes=%d", query, result.ingested, result.duplicates)
            except Exception as e:
                await db.rollback()
                logger.warning("Collection failed for [%s]: %s", query, str(e))
        await asyncio.sleep(0.5)

    async with AsyncSessionLocal() as db:
        try:
            await _save_snapshot(db)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.warning("Snapshot save failed: %s", str(e))

    try:
        await cache_delete_prefix("analysis:")
        await cache_delete_prefix("opportunities:")
        await cache_delete_prefix("recommendations:")
        await cache_delete_prefix("trends:")
    except Exception:
        pass

    logger.info("Manual collection done. Total ingested: %d", total_ingested)


@router.post("", response_model=CollectResponse)
async def trigger_collection(background_tasks: BackgroundTasks) -> CollectResponse:
    """Trigger a full 2GIS data collection in the background."""
    background_tasks.add_task(_do_collect)
    return CollectResponse(success=True, message="Collection started in background. Takes ~1 minute.")
