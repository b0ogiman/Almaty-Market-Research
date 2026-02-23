"""End-to-end integration test for core pipeline.

Pipeline: collect → enrich → analyze → score → recommend.
"""

import pytest

from app.collectors.avito_mock import AvitoMockCollector
from app.collectors.pipeline import CollectionPipeline
from app.config import get_settings
from app.core.redis_client import cache_get, redis_ping
from app.database import AsyncSessionLocal
from app.jobs.scheduler import _run_collection_job
from app.services.market_analysis import MarketAnalysisService
from app.services.opportunity_scoring import OpportunityScoringService
from app.services.recommendation import RecommendationService


@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    """Full pipeline should run without errors and persist data."""
    settings = get_settings()

    async with AsyncSessionLocal() as db:
        # 1. Collect and enrich listings, then commit.
        collector = AvitoMockCollector()
        pipeline = CollectionPipeline(collector, db)
        result = await pipeline.run(limit=30)
        await db.commit()
        assert result.ingested > 0

        # 2. Run market analysis backed by enriched listings.
        analysis_service = MarketAnalysisService(db)
        analysis = await analysis_service.analyze(
            sector=None,
            district=None,
            force_refresh=True,
        )
        assert analysis.score is not None
        assert analysis.insights is not None

        # 3. Score opportunities using analytics output.
        opp_service = OpportunityScoringService(db)
        opportunities = await opp_service.score_opportunities(
            sector=None,
            district=None,
            limit=5,
        )
        assert len(opportunities) > 0

        # 4. Generate recommendations (LLM-backed when configured, else heuristic).
        rec_service = RecommendationService(db)
        recommendations = await rec_service.get_recommendations(limit=5)
        assert len(recommendations) > 0

        # 5. Cache behavior: verify keys exist when Redis is available.
        if settings.cache_enabled and await redis_ping():
            analysis_key = analysis_service._cache_key(None, None)
            cached_analysis = await cache_get(analysis_key)
            assert cached_analysis and "id" in cached_analysis

            opp_key = opp_service._cache_key(None, None, 5)
            cached_opps = await cache_get(opp_key)
            assert cached_opps and "ids" in cached_opps

        # 6. Scheduled collection job should invalidate caches when Redis is available.
        if settings.cache_enabled and await redis_ping():
            await _run_collection_job()

            analysis_key = analysis_service._cache_key(None, None)
            opp_key = opp_service._cache_key(None, None, 5)

            cached_analysis_after = await cache_get(analysis_key)
            cached_opps_after = await cache_get(opp_key)

            # After scheduled collection, caches for analysis and opportunities
            # should be cleared so new results use fresh data.
            assert cached_analysis_after is None
            assert cached_opps_after is None

