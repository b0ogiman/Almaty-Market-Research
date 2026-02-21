"""Opportunity scoring service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.opportunity_scorer import OpportunityScorer
from app.config import get_settings
from app.core.redis_client import cache_get, cache_set
from app.exceptions import NotFoundError
from app.logging_config import get_logger
from app.models.market_data import MarketData
from app.models.opportunity import Opportunity

logger = get_logger("services.opportunity_scoring")


class OpportunityScoringService:
    """Orchestrates opportunity scoring: AI engine, persistence, cache."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.scorer = OpportunityScorer()
        self.settings = get_settings()

    def _cache_key(self, sector: str | None, district: str | None, limit: int) -> str:
        return f"opportunities:sector={sector or 'all'}:district={district or 'all'}:limit={limit}"

    async def score_opportunities(
        self,
        sector: str | None = None,
        district: str | None = None,
        limit: int = 10,
    ) -> list[Opportunity]:
        """Score and persist opportunities. Returns created opportunities."""
        cache_key = self._cache_key(sector, district, limit)
        if self.settings.cache_enabled:
            cached = await cache_get(cache_key)
            if cached and "ids" in cached:
                ids = cached["ids"]
                if ids:
                    from uuid import UUID

                    stmt = select(Opportunity).where(
                        Opportunity.id.in_([UUID(i) for i in ids])
                    )
                    result = await self.db.execute(stmt)
                    items = list(result.scalars().all())
                    if len(items) == len(ids):
                        return items

        q = select(MarketData).where(MarketData.is_active == True)
        if sector:
            q = q.where(MarketData.sector == sector)
        if district:
            q = q.where(MarketData.district == district)
        q = q.limit(200)
        result = await self.db.execute(q)
        rows = result.scalars().all()
        market_data = [
            {
                "sector": r.sector,
                "district": r.district,
                "metric_name": r.metric_name,
                "metric_value": r.metric_value,
            }
            for r in rows
        ]

        scored = await self.scorer.score_opportunities(
            sector=sector,
            district=district,
            market_data=market_data,
            limit=limit,
        )
        opportunities = []
        for s in scored:
            opp = Opportunity(
                sector=sector or "various",
                district=district or "Almaty",
                title=s["title"],
                description=s.get("description"),
                score=s["score"],
                score_breakdown=s.get("score_breakdown"),
                metadata_=s.get("metadata"),
            )
            self.db.add(opp)
            await self.db.flush()
            opportunities.append(opp)

        if self.settings.cache_enabled and opportunities:
            await cache_set(
                cache_key,
                {"ids": [str(o.id) for o in opportunities]},
                ttl=self.settings.cache_ttl_opportunities,
            )
        return opportunities

    async def list_opportunities(
        self,
        sector: str | None = None,
        district: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Opportunity], int]:
        """List opportunities with pagination."""
        from sqlalchemy import func

        q = select(Opportunity).where(Opportunity.is_active == True)
        if sector:
            q = q.where(Opportunity.sector == sector)
        if district:
            q = q.where(Opportunity.district == district)
        count_stmt = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0
        q = q.order_by(Opportunity.score.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        return items, int(total)

    async def get_by_id(self, opportunity_id: str) -> Opportunity:
        """Get opportunity by ID."""
        from uuid import UUID

        record = await self.db.get(Opportunity, UUID(opportunity_id))
        if not record:
            raise NotFoundError("Opportunity", opportunity_id)
        return record
