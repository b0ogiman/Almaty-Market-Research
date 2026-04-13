"""Data ingestion service."""

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import cache_delete_prefix
from app.models.market_data import MarketData
from app.schemas.data import DataIngestItem, DataIngestRequest
from app.logging_config import get_logger
logger = get_logger("services.data_ingestion")


class DataIngestionService:
    """Handles market data ingestion into PostgreSQL."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ingest(self, request: DataIngestRequest) -> tuple[int, int, list[UUID]]:
        """
        Ingest market data items atomically. Returns (ingested_count, failed_count, ids).
        Invalidates analysis/opportunity/recommendation caches on success.
        """
        records: list[MarketData] = []
        source = request.source_override

        for item in request.items:
            record = MarketData(
                sector=item.sector,
                district=item.district,
                metric_name=item.metric_name,
                metric_value=item.metric_value,
                unit=item.unit,
                year=item.year,
                quarter=item.quarter,
                source=source or item.source,
                raw_json=json.dumps(item.raw_json) if item.raw_json else None,
            )
            records.append(record)

        self.db.add_all(records)
        await self.db.flush()
        ids = [r.id for r in records]

        try:
            await cache_delete_prefix("analysis:")
            await cache_delete_prefix("opportunities:")
            await cache_delete_prefix("recommendations:")
        except Exception as e:
            # Cache invalidation failures should not break successful writes.
            logger.debug("Cache invalidation failed after ingest: %s", str(e))

        return len(records), 0, ids

    async def list_data(
        self,
        sector: str | None = None,
        district: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[MarketData], int]:
        """List market data with optional filters and pagination."""
        from sqlalchemy import func

        q = select(MarketData).where(MarketData.is_active == True)
        if sector:
            q = q.where(MarketData.sector == sector)
        if district:
            q = q.where(MarketData.district == district)
        count_stmt = select(func.count()).select_from(q.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        offset = (page - 1) * size
        q = q.order_by(MarketData.created_at.desc()).offset(offset).limit(size)
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        return items, int(total)
