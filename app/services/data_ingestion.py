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
        Ingest market data items. Returns (ingested_count, failed_count, ids).
        Invalidates analysis/opportunity cache on success.
        """
        ingested = 0
        failed = 0
        ids: list[UUID] = []
        source = request.source_override

        for item in request.items:
            try:
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
                self.db.add(record)
                await self.db.flush()
                ids.append(record.id)
                ingested += 1
            except Exception as e:
                logger.warning("Ingest item failed: %s", str(e))
                failed += 1
        # Invalidate caches if we successfully ingested any items.
        if ingested > 0:
            # Market analysis and opportunity scoring both depend on MarketData.
            # It is safe and simple to invalidate all related cache entries.
            try:
                await cache_delete_prefix("analysis:")
                await cache_delete_prefix("opportunities:")
            except Exception as e:
                # Cache invalidation failures should not break ingestion.
                logger.debug("Cache invalidation failed after ingest: %s", str(e))

        return ingested, failed, ids

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
