"""Market analysis service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.market_analysis_engine import MarketAnalysisEngine
from app.config import get_settings
from app.core.redis_client import cache_get, cache_set
from app.exceptions import NotFoundError
from app.logging_config import get_logger
from app.models.analysis_result import AnalysisResult
from app.models.business_listing import BusinessListing

logger = get_logger("services.market_analysis")


class MarketAnalysisService:
    """Orchestrates market analysis: DB → analytics engine → cache → persistence."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.engine = MarketAnalysisEngine()
        self.settings = get_settings()

    def _cache_key(self, sector: str | None, district: str | None) -> str:
        return f"analysis:sector={sector or 'all'}:district={district or 'all'}"

    async def _load_listings(
        self,
        sector: str | None,
        district: str | None,
        limit: int = 1000,
    ) -> list[dict]:
        """Load enriched business listings for analysis."""
        q = select(BusinessListing).where(BusinessListing.is_active == True)
        if sector:
            # Sector approximated via normalized category when available.
            q = q.where(BusinessListing.category_normalized == sector)
        if district:
            q = q.where(
                (BusinessListing.district == district)
                | (BusinessListing.district_mapped == district)
            )
        q = q.order_by(BusinessListing.created_at.desc()).limit(limit)
        result = await self.db.execute(q)
        rows = result.scalars().all()
        return [
            {
                "id": str(r.id),
                "name": r.name,
                "category": r.category,
                "category_normalized": r.category_normalized,
                "district": r.district,
                "district_mapped": r.district_mapped,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "rating": r.rating,
                "review_count": r.review_count,
                "sentiment_score": r.sentiment_score,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    async def analyze(
        self,
        sector: str | None = None,
        district: str | None = None,
        force_refresh: bool = False,
    ) -> AnalysisResult:
        """Run market analysis. Uses cached AnalysisResult when available."""
        cache_key = self._cache_key(sector, district)
        if not force_refresh and self.settings.cache_enabled:
            cached = await cache_get(cache_key)
            if cached and "id" in cached:
                from uuid import UUID

                existing = await self.db.get(AnalysisResult, UUID(cached["id"]))
                if existing:
                    return existing

        listings = await self._load_listings(sector=sector, district=district)

        output = await self.engine.analyze(
            sector=sector,
            district=district,
            listings=listings,
        )
        record = AnalysisResult(
            sector=sector or "all",
            district=district or "all",
            summary=output.get("summary"),
            score=output.get("score"),
            insights=output.get("insights"),
            raw_output=output.get("raw_output"),
        )
        self.db.add(record)
        await self.db.flush()

        if self.settings.cache_enabled:
            await cache_set(
                cache_key,
                {"id": str(record.id)},
                ttl=self.settings.cache_ttl_analysis,
            )
        return record

    async def get_by_id(self, analysis_id: str) -> AnalysisResult:
        """Get analysis result by ID."""
        from uuid import UUID

        record = await self.db.get(AnalysisResult, UUID(analysis_id))
        if not record:
            raise NotFoundError("AnalysisResult", analysis_id)
        return record

    async def list_analyses(
        self,
        sector: str | None = None,
        district: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AnalysisResult], int]:
        """List analysis results with pagination."""
        from sqlalchemy import func

        q = select(AnalysisResult)
        if sector:
            q = q.where(AnalysisResult.sector == sector)
        if district:
            q = q.where(AnalysisResult.district == district)
        count_stmt = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0
        q = q.order_by(AnalysisResult.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        return items, int(total)
