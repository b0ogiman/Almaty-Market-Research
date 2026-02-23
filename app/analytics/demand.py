"""Demand score calculation."""

from typing import Any

from app.logging_config import get_logger

logger = get_logger("analytics.demand")


class DemandScorer:
    """
    Calculate demand score from aggregated metrics.
    Higher score = stronger demand signal.
    """

    def __init__(
        self,
        rating_weight: float = 0.3,
        review_weight: float = 0.3,
        density_weight: float = 0.2,
        sentiment_weight: float = 0.2,
    ) -> None:
        self.rating_weight = rating_weight
        self.review_weight = review_weight
        self.density_weight = density_weight
        self.sentiment_weight = sentiment_weight

    def score(
        self,
        avg_rating: float | None = None,
        total_reviews: int | None = None,
        listing_count: int | None = None,
        avg_sentiment: float | None = None,
        max_listings: int = 1000,
    ) -> float:
        """
        Compute demand score in [0, 1].
        Normalizes inputs and applies weighted sum.
        """
        parts = []
        if avg_rating is not None:
            r = max(0, min(5, avg_rating)) / 5.0
            parts.append((r, self.rating_weight))
        if total_reviews is not None and total_reviews > 0:
            rev = min(1.0, total_reviews / 500)
            parts.append((rev, self.review_weight))
        if listing_count is not None and max_listings > 0:
            den = min(1.0, listing_count / max_listings)
            parts.append((den, self.density_weight))
        if avg_sentiment is not None:
            sent = (avg_sentiment + 1) / 2
            parts.append((sent, self.sentiment_weight))
        if not parts:
            return 0.5
        total_w = sum(w for _, w in parts)
        if total_w <= 0:
            return 0.5
        return sum(v * w for v, w in parts) / total_w

    def score_from_listings(self, listings: list[dict[str, Any]]) -> float:
        """Compute demand score from a list of listing dicts."""
        if not listings:
            return 0.5
        ratings = [l.get("rating") for l in listings if l.get("rating") is not None]
        reviews = [l.get("review_count") or 0 for l in listings]
        sentiments = [l.get("sentiment_score") for l in listings if l.get("sentiment_score") is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        total_reviews = sum(reviews)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None
        return self.score(
            avg_rating=avg_rating,
            total_reviews=total_reviews,
            listing_count=len(listings),
            avg_sentiment=avg_sentiment,
        )
