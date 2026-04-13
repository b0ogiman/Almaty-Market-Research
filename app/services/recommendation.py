"""Recommendation service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.recommendation_engine import RecommendationEngine
from app.config import get_settings
from app.core.redis_client import cache_delete_prefix, cache_get, cache_set
from app.llm.recommendation_service import LLMRecommendationService
from app.logging_config import get_logger
from app.models.opportunity import Opportunity
from app.models.recommendation import Recommendation

logger = get_logger("services.recommendation")


class RecommendationService:
    """Generates and returns ranked recommendations from opportunities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.engine = RecommendationEngine()
        self.settings = get_settings()
        # Use LLM-backed recommendations when OpenAI is configured; otherwise fall back to rule-based engine.
        self.llm_service: LLMRecommendationService | None = (
            LLMRecommendationService() if self.settings.openai_api_key else None
        )

    def _cache_key(self, limit: int) -> str:
        return f"recommendations:limit={limit}"

    async def get_recommendations(self, limit: int = 10) -> list[Recommendation]:
        """Get top N recommendations. Uses cache when available."""
        cache_key = self._cache_key(limit)
        if self.settings.cache_enabled:
            cached = await cache_get(cache_key)
            if cached and "ids" in cached:
                from uuid import UUID

                stmt = select(Recommendation).where(
                    Recommendation.id.in_([UUID(i) for i in cached["ids"]])
                ).order_by(Recommendation.rank)
                result = await self.db.execute(stmt)
                items = list(result.scalars().all())
                if len(items) >= min(limit, len(cached["ids"])):
                    return items[:limit]

        q = (
            select(Opportunity)
            .where(Opportunity.is_active == True)
            .order_by(Opportunity.score.desc())
            .limit(limit * 2)
        )
        result = await self.db.execute(q)
        opportunities = list(result.scalars().all())
        if not opportunities:
            return []
        opp_dicts = [
            {
                "id": str(o.id),
                "sector": o.sector,
                "district": o.district,
                "title": o.title,
                "score": o.score,
            }
            for o in opportunities
        ]

        rec_models: list[Recommendation] = []

        # Primary path: LLM-backed recommendations, when configured.
        if self.llm_service:
            try:
                avg_score = (
                    sum(o["score"] for o in opp_dicts) / len(opp_dicts)
                    if opp_dicts
                    else 0.0
                )
                metrics = {
                    "num_opportunities": len(opp_dicts),
                    "avg_score": round(avg_score, 3),
                    "max_score": max((o["score"] for o in opp_dicts), default=0.0),
                }
                llm_recs = await self.llm_service.get_recommendations(
                    sector="general",
                    district="Almaty",
                    metrics=metrics,
                )
                for rank, r in enumerate(llm_recs[:limit], start=1):
                    rec = Recommendation(
                        opportunity_id=None,
                        sector=r["sector"],
                        district=r["district"],
                        title=r["title"],
                        rationale=r.get("rationale"),
                        score=r["score"],
                        rank=rank,
                    )
                    self.db.add(rec)
                    await self.db.flush()
                    rec_models.append(rec)
            except Exception as e:
                logger.exception("LLM recommendations failed, falling back: %s", str(e))

        # Fallback: heuristic engine based on opportunity scores.
        if not rec_models:
            recs = await self.engine.get_recommendations(opp_dicts, limit=limit)
            for r in recs:
                from uuid import UUID

                opp_id = r.get("opportunity_id")
                rec = Recommendation(
                    opportunity_id=UUID(opp_id) if opp_id else None,
                    sector=r["sector"],
                    district=r["district"],
                    title=r["title"],
                    rationale=r.get("rationale"),
                    score=r["score"],
                    rank=r["rank"],
                )
                self.db.add(rec)
                await self.db.flush()
                rec_models.append(rec)

        if self.settings.cache_enabled and rec_models:
            # Keep cache invalidation policy consistent across write operations.
            await cache_delete_prefix("analysis:")
            await cache_delete_prefix("opportunities:")
            await cache_delete_prefix("recommendations:")
            await cache_set(
                cache_key,
                {"ids": [str(r.id) for r in rec_models]},
                ttl=self.settings.cache_ttl_recommendations,
            )
        return rec_models
