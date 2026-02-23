"""Base collector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CollectResult:
    """Result of a collection run."""

    source: str
    collected: int = 0
    ingested: int = 0
    duplicates: int = 0
    errors: list[str] = field(default_factory=list)
    raw_items: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RawListing:
    """Normalized raw listing for validation pipeline."""

    external_id: str
    source: str
    name: str
    category: str
    address: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None
    review_count: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    description: str | None = None
    raw: dict[str, Any] | None = None


class BaseCollector(ABC):
    """Abstract base for data collectors."""

    source_name: str = "base"

    @abstractmethod
    async def collect(
        self,
        query: str | None = None,
        district: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> CollectResult:
        """Collect listings from source."""
        pass
