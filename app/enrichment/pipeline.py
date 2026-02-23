"""Enrichment pipeline: district mapping, category norm, sentiment."""

from typing import Any

from app.enrichment.district_mapping import DistrictMapper
from app.enrichment.category_normalizer import CategoryNormalizer
from app.enrichment.sentiment import SentimentScorer
from app.logging_config import get_logger

logger = get_logger("enrichment.pipeline")


class EnrichmentPipeline:
    """Run full enrichment on listing items."""

    def __init__(self) -> None:
        self.district_mapper = DistrictMapper()
        self.category_normalizer = CategoryNormalizer()
        self.sentiment_scorer = SentimentScorer()

    def enrich(self, item: dict[str, Any]) -> dict[str, Any]:
        """Enrich a single item in place."""
        self.district_mapper.enrich(item)
        self.category_normalizer.enrich(item)
        self.sentiment_scorer.enrich(item)
        return item

    def enrich_batch(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Enrich a batch of items."""
        for item in items:
            self.enrich(item)
        return items
