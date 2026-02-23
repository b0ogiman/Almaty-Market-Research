"""LLM prompt templates."""

from typing import Any

RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "sector": {"type": "string"},
                    "district": {"type": "string"},
                    "rationale": {"type": "string"},
                    "score": {"type": "number"},
                    "risks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "sector", "district", "rationale", "score"],
            },
        },
    },
    "required": ["recommendations"],
}


RECOMMENDATION_SYSTEM = """You are a market research analyst for Almaty, Kazakhstan.
Generate structured business opportunity recommendations based on the provided market data.
Be concise, data-driven, and specific to Almaty's local market."""

RECOMMENDATION_USER_TEMPLATE = """Based on the following market analysis for Almaty:

{sector_info}
{district_info}
{metrics_summary}

Provide 3-5 business opportunity recommendations. For each:
- title: short descriptive name
- sector: business sector
- district: Almaty district
- rationale: 1-2 sentence justification
- score: 0-1 opportunity score
- risks: optional list of risks

Return valid JSON only."""


class RecommendationPrompt:
    """Structured prompt for business recommendations."""

    @staticmethod
    def build(
        sector: str = "general",
        district: str = "Almaty",
        metrics: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        """Build messages for recommendation request."""
        metrics = metrics or {}
        sector_info = f"Sector focus: {sector}"
        district_info = f"District focus: {district}"
        metrics_summary = "Metrics: " + ", ".join(f"{k}={v}" for k, v in metrics.items()) if metrics else "No metrics"
        user = RECOMMENDATION_USER_TEMPLATE.format(
            sector_info=sector_info,
            district_info=district_info,
            metrics_summary=metrics_summary,
        )
        return [
            {"role": "system", "content": RECOMMENDATION_SYSTEM},
            {"role": "user", "content": user},
        ]


EXECUTIVE_SUMMARY_SYSTEM = """You are a market research analyst. Write a brief executive summary (2-4 sentences) of the market analysis findings for Almaty. Be concise and actionable."""


class ExecutiveSummaryPrompt:
    """Prompt for executive summary generation."""

    @staticmethod
    def build(
        key_findings: list[str],
        top_opportunities: list[str],
    ) -> list[dict[str, str]]:
        """Build messages for summary request."""
        content = f"""Key findings:
{chr(10).join('- ' + f for f in key_findings)}

Top opportunities:
{chr(10).join('- ' + o for o in top_opportunities)}

Generate a brief executive summary."""
        return [
            {"role": "system", "content": EXECUTIVE_SUMMARY_SYSTEM},
            {"role": "user", "content": content},
        ]
