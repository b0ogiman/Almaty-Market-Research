"""Competition index - business density per district/sector."""

from collections import defaultdict
from typing import Any

from app.logging_config import get_logger

logger = get_logger("analytics.competition")


class CompetitionIndex:
    """
    Compute competition index as business density per district/category.
    Higher index = more competitors.
    """

    def __init__(self, listings: list[dict[str, Any]]) -> None:
        self._by_district: dict[str, int] = defaultdict(int)
        self._by_category: dict[str, int] = defaultdict(int)
        self._by_district_category: dict[tuple[str, str], int] = defaultdict(int)
        for item in listings:
            d = (item.get("district") or item.get("district_mapped")) or "unknown"
            c = (item.get("category_normalized") or item.get("category")) or "unknown"
            self._by_district[d] += 1
            self._by_category[c] += 1
            self._by_district_category[(d, c)] += 1

    def district_index(self, district: str) -> float:
        """
        Normalized density for district. Returns value in [0, 1].
        1 = highest density among all districts.
        """
        if not self._by_district:
            return 0.0
        counts = list(self._by_district.values())
        mx = max(counts)
        if mx <= 0:
            return 0.0
        count = self._by_district.get(district, 0)
        return count / mx

    def category_index(self, category: str) -> float:
        """Normalized density for category."""
        if not self._by_category:
            return 0.0
        counts = list(self._by_category.values())
        mx = max(counts)
        if mx <= 0:
            return 0.0
        count = self._by_category.get(category, 0)
        return count / mx

    def combined_index(self, district: str, category: str) -> float:
        """Combined district+category density. Higher = more competition."""
        d_idx = self.district_index(district)
        c_idx = self.category_index(category)
        pair_count = self._by_district_category.get((district, category), 0)
        pair_mx = max(self._by_district_category.values()) if self._by_district_category else 1
        pair_idx = pair_count / pair_mx if pair_mx > 0 else 0
        return (d_idx + c_idx + pair_idx) / 3
