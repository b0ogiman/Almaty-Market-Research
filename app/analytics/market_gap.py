"""Market gap scoring formula."""

from typing import Any

from app.analytics.demand import DemandScorer
from app.analytics.competition import CompetitionIndex
from app.logging_config import get_logger

logger = get_logger("analytics.market_gap")


class MarketGapScorer:
    """
    Score market gaps: high demand + low competition = opportunity.
    Formula: gap_score = demand * (1 - competition_index)
    """

    def __init__(
        self,
        demand_weight: float = 0.6,
        competition_weight: float = 0.4,
    ) -> None:
        self.demand_weight = demand_weight
        self.competition_weight = competition_weight

    def score(
        self,
        demand_score: float,
        competition_index: float,
    ) -> float:
        """
        Compute market gap score in [0, 1].
        Higher = better opportunity (high demand, low competition).
        """
        opportunity = demand_score * (1.0 - competition_index)
        return max(0.0, min(1.0, opportunity))

    def score_from_listings(
        self,
        listings: list[dict[str, Any]],
        district: str,
        category: str,
    ) -> float:
        """Compute gap score for district+category from listings."""
        demand_scorer = DemandScorer()
        comp_index = CompetitionIndex(listings)
        segment = [
            l for l in listings
            if (l.get("district") or l.get("district_mapped")) == district
            and (l.get("category_normalized") or l.get("category")) == category
        ]
        demand = demand_scorer.score_from_listings(segment or listings)
        competition = comp_index.combined_index(district, category)
        return self.score(demand, competition)
