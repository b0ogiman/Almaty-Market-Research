"""Lightweight sentiment scoring using VADER or fallback."""

from typing import Optional

from app.logging_config import get_logger

logger = get_logger("enrichment.sentiment")

_vader: Optional[object] = None


def _get_vader():
    """Lazy load VADER (lightweight, no GPU)."""
    global _vader
    if _vader is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _vader = SentimentIntensityAnalyzer()
        except ImportError:
            logger.warning("vaderSentiment not installed. Using fallback sentiment.")
            _vader = "fallback"
    return _vader


def score_sentiment(text: str | None) -> float:
    """
    Score sentiment from -1 (negative) to 1 (positive).
    Uses VADER if available; otherwise simple keyword fallback.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return 0.0
    v = _get_vader()
    if v == "fallback":
        return _fallback_sentiment(text)
    try:
        scores = v.polarity_scores(text)
        compound = scores.get("compound", 0.0)
        return max(-1.0, min(1.0, float(compound)))
    except Exception as e:
        logger.debug("VADER error: %s", str(e))
        return _fallback_sentiment(text)


def _fallback_sentiment(text: str) -> float:
    """Simple keyword-based fallback when VADER unavailable."""
    t = text.lower()
    pos = sum(1 for w in ("good", "great", "excellent", "best", "love") if w in t)
    neg = sum(1 for w in ("bad", "terrible", "worst", "hate", "poor") if w in t)
    if pos > neg:
        return 0.3
    if neg > pos:
        return -0.3
    return 0.0


class SentimentScorer:
    """Scorer for text sentiment."""

    def score(self, text: str | None) -> float:
        """Return sentiment score in [-1, 1]."""
        return score_sentiment(text)

    def enrich(self, item: dict) -> dict:
        """Add sentiment_score to item from description/name."""
        text = item.get("description") or item.get("name") or ""
        item["sentiment_score"] = self.score(text)
        return item
