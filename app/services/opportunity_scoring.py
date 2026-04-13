"""Opportunity scoring service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.opportunity_scorer import OpportunityScorer
from app.analytics.demand import DemandScorer
from app.analytics.competition import CompetitionIndex
from app.analytics.market_gap import MarketGapScorer
from app.config import get_settings
from app.core.redis_client import cache_delete_prefix, cache_get, cache_set
from app.exceptions import NotFoundError
from app.logging_config import get_logger
from app.models.business_listing import BusinessListing
from app.models.market_data import MarketData
from app.models.opportunity import Opportunity

logger = get_logger("services.opportunity_scoring")


class OpportunityScoringService:
    """Orchestrates opportunity scoring: analytics-backed engine, persistence, cache."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        # Keep stub engine as a fallback when no enriched data is available.
        self.scorer = OpportunityScorer()
        self.settings = get_settings()
        self._demand = DemandScorer()
        self._gap = MarketGapScorer()

    def _cache_key(self, sector: str | None, district: str | None, limit: int) -> str:
        return f"opportunities:sector={sector or 'all'}:district={district or 'all'}:limit={limit}"

    async def _load_listings(
        self,
        sector: str | None,
        district: str | None,
        limit: int = 2000,
    ) -> list[dict]:
        """Load enriched business listings used for opportunity scoring."""
        q = select(BusinessListing).where(BusinessListing.is_active == True)
        if sector:
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
                "rating": r.rating,
                "review_count": r.review_count,
                "sentiment_score": r.sentiment_score,
            }
            for r in rows
        ]

    async def _score_from_analytics(
        self,
        listings: list[dict],
        limit: int,
    ) -> list[Opportunity]:
        """Create opportunities using analytics: demand, competition, gap."""
        if not listings:
            return []

        comp_index = CompetitionIndex(listings)
        # Group listings by (district, category) using enriched fields when available.
        groups: dict[tuple[str, str], list[dict]] = {}
        for item in listings:
            d = (item.get("district") or item.get("district_mapped")) or "unknown"
            c = (item.get("category_normalized") or item.get("category")) or "unknown"
            groups.setdefault((d, c), []).append(item)

        segment_scores: list[tuple[tuple[str, str], float, float]] = []
        for (district, category), segment in groups.items():
            demand = self._demand.score_from_listings(segment)
            competition = comp_index.combined_index(district, category)
            gap_score = self._gap.score(demand, competition)
            segment_scores.append(((district, category), gap_score, demand))

        # Sort segments by gap score (desc), then demand as tie-breaker.
        segment_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_segments = segment_scores[:limit]

        opportunities: list[Opportunity] = []
        for district, category in [s[0] for s in top_segments]:
            gap_score = next(s[1] for s in segment_scores if s[0] == (district, category))
            demand = next(s[2] for s in segment_scores if s[0] == (district, category))
            title = f"{category.title()} expansion in {district} district"
            description = (
                f"High-demand, relatively under-served segment for {category} in {district}."
            )
            opp = Opportunity(
                sector=category,
                district=district,
                title=title,
                description=description,
                score=gap_score,
                score_breakdown={
                    "demand_score": demand,
                    "gap_score": gap_score,
                },
                metadata_={
                    "category": category,
                    "district": district,
                },
            )
            self.db.add(opp)
            await self.db.flush()
            opportunities.append(opp)
        return opportunities

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

        listings = await self._load_listings(sector=sector, district=district)

        # Primary path: analytics-backed scoring from enriched listings.
        opportunities = await self._score_from_analytics(listings, limit=limit)

        # Fallback path: legacy stub based on MarketData, if no opportunities produced.
        if not opportunities:
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
            # New opportunities change downstream recommendation state.
            await cache_delete_prefix("analysis:")
            await cache_delete_prefix("opportunities:")
            await cache_delete_prefix("recommendations:")
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
