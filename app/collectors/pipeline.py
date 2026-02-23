"""Collection pipeline: collect → validate → dedup → persist."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import BaseCollector, CollectResult
from app.collectors.validation import validate_batch
from app.collectors.dedup import detect_duplicates
from app.enrichment.pipeline import EnrichmentPipeline
from app.models.business_listing import BusinessListing
from app.logging_config import get_logger

logger = get_logger("collectors.pipeline")


class CollectionPipeline:
    """Orchestrates collection, validation, dedup, and persistence."""

    def __init__(
        self,
        collector: BaseCollector,
        db: AsyncSession,
    ) -> None:
        self.collector = collector
        self.db = db
        self._enrichment = EnrichmentPipeline()

    async def run(
        self,
        query: str | None = None,
        district: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> CollectResult:
        """Run full pipeline: collect → validate → dedup → save."""
        result = await self.collector.collect(
            query=query,
            district=district,
            limit=limit,
            **kwargs,
        )
        if result.errors:
            return result

        raw_items = result.raw_items
        if not raw_items:
            return result

        valid, val_errors = validate_batch(raw_items)
        result.errors.extend(val_errors)
        if val_errors:
            logger.info("Validation: %d valid, %d errors", len(valid), len(val_errors))

        unique, dups = detect_duplicates(valid)
        result.duplicates = len(dups)

        # Enrich unique listings (idempotent, skip items that already have enriched fields)
        to_enrich: list[dict[str, Any]] = []
        for item in unique:
            if (
                "district_mapped" in item
                or "category_normalized" in item
                or "sentiment_score" in item
            ):
                continue
            to_enrich.append(item)
        if to_enrich:
            self._enrichment.enrich_batch(to_enrich)

        ingested = 0
        for item in unique:
            try:
                listing = BusinessListing(
                    external_id=item["external_id"],
                    source=item["source"],
                    name=item["name"],
                    category=item["category"],
                    category_normalized=item.get("category_normalized"),
                    address=item.get("address"),
                    district=item.get("district"),
                    district_mapped=item.get("district_mapped"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    rating=item.get("rating"),
                    review_count=item.get("review_count"),
                    price_min=item.get("price_min"),
                    price_max=item.get("price_max"),
                    description=item.get("description"),
                    sentiment_score=item.get("sentiment_score"),
                    raw_json=item.get("raw"),
                )
                self.db.add(listing)
                await self.db.flush()
                ingested += 1
            except Exception as e:
                result.errors.append(f"persist {item.get('external_id')}: {str(e)}")

        result.ingested = ingested
        return result
