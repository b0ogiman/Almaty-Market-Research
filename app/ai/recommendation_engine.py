"""Recommendation AI engine - MVP stub."""

from typing import Any, Optional

from app.logging_config import get_logger

logger = get_logger("ai.recommendation")


class RecommendationEngine:
    """Stub for recommendation AI. Aggregates opportunities into ranked recommendations."""

    async def get_recommendations(
        self,
        opportunities: list[dict[str, Any]],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Generate top N recommendations from scored opportunities.
        MVP: Sorts by score and returns top results.
        """
        logger.info("Generating recommendations (stub): %d opportunities, limit=%d", len(opportunities), limit)
        sorted_opps = sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
        results = []
        for rank, opp in enumerate(sorted_opps[:limit], start=1):
            results.append({
                "opportunity_id": opp.get("id"),
                "sector": opp.get("sector", ""),
                "district": opp.get("district", ""),
                "title": opp.get("title", ""),
                "rationale": f"Rank #{rank} by opportunity score. High potential in local market.",
                "score": opp.get("score", 0),
                "rank": rank,
            })
        return results
