"""Opportunity scoring AI engine - MVP stub."""

from typing import Any, Optional

from app.logging_config import get_logger

logger = get_logger("ai.opportunity_scorer")


class OpportunityScorer:
    """Stub for opportunity scoring AI. Replace with ML model in production."""

    async def score_opportunities(
        self,
        sector: Optional[str] = None,
        district: Optional[str] = None,
        market_data: Optional[list[dict[str, Any]]] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Score and rank business opportunities.
        MVP: Returns rule-based placeholders. Integrate ML/AI later.
        """
        logger.info(
            "Scoring opportunities (stub): sector=%s, district=%s, limit=%d",
            sector,
            district,
            limit,
        )
        placeholder_titles = [
            "Retail expansion in district center",
            "Food service near transport hubs",
            "Professional services for SMEs",
            "Tech-enabled local delivery",
            "Education and training programs",
            "Health and wellness facilities",
            "Entertainment and leisure venues",
            "Local manufacturing for import substitution",
            "E-commerce fulfillment center",
            "Co-working and business services",
        ]
        results = []
        for i, title in enumerate(placeholder_titles[:limit]):
            base_score = 0.5 + (0.05 * (limit - i)) + (0.02 * (i % 3))
            results.append({
                "title": title,
                "description": f"Opportunity in {sector or 'various'} sector, {district or 'Almaty'} area.",
                "score": min(1.0, round(base_score, 2)),
                "score_breakdown": {
                    "demand": 0.7,
                    "competition": 0.6,
                    "barriers": 0.5,
                    "growth": 0.65,
                },
                "metadata": {"sector": sector, "district": district},
            })
        return results
