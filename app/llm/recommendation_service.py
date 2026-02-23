"""LLM-powered recommendation service."""

from typing import Any

from app.llm.openai_client import OpenAIClient
from app.llm.prompts import RecommendationPrompt, RECOMMENDATION_SCHEMA
from app.logging_config import get_logger

logger = get_logger("llm.recommendation")


class LLMRecommendationService:
    """Generate structured recommendations via OpenAI."""

    def __init__(self, client: OpenAIClient | None = None) -> None:
        self.client = client or OpenAIClient()

    async def get_recommendations(
        self,
        sector: str = "general",
        district: str = "Almaty",
        metrics: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Call LLM for structured recommendations.
        Returns validated list of recommendation dicts.
        """
        messages = RecommendationPrompt.build(sector=sector, district=district, metrics=metrics)
        try:
            data = await self.client.complete_json(messages, schema=RECOMMENDATION_SCHEMA)
            recs = data.get("recommendations", [])
            return self._validate_recs(recs)
        except Exception as e:
            logger.exception("LLM recommendation failed: %s", str(e))
            return []

    def _validate_recs(self, recs: list[Any]) -> list[dict[str, Any]]:
        """Validate and normalize recommendation items."""
        out = []
        for r in recs:
            if not isinstance(r, dict):
                continue
            title = r.get("title") or "Unnamed"
            sector = r.get("sector") or "general"
            district = r.get("district") or "Almaty"
            rationale = r.get("rationale") or ""
            score = float(r.get("score", 0.5))
            score = max(0.0, min(1.0, score))
            risks = r.get("risks")
            if isinstance(risks, list):
                risks = [str(x) for x in risks]
            else:
                risks = []
            out.append({
                "title": title,
                "sector": sector,
                "district": district,
                "rationale": rationale,
                "score": score,
                "risks": risks,
            })
        return out
