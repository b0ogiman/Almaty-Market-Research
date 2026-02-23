"""Category normalization for business listings."""

import re
from typing import Optional

from app.logging_config import get_logger

logger = get_logger("enrichment.category")

# Normalize to standard categories
CATEGORY_MAP: dict[str, str] = {
    "restaurant": "food_service",
    "cafe": "food_service",
    "bar": "food_service",
    "food": "food_service",
    "meal_delivery": "food_service",
    "meal_takeaway": "food_service",
    "real_estate": "real_estate",
    "real_estate_agency": "real_estate",
    "car_dealer": "vehicles",
    "car_rental": "vehicles",
    "car_repair": "vehicles",
    "electronics_store": "electronics",
    "hardware_store": "retail",
    "clothing_store": "clothing",
    "shoe_store": "clothing",
    "supermarket": "retail",
    "grocery": "retail",
    "store": "retail",
    "pharmacy": "health",
    "hospital": "health",
    "dentist": "health",
    "doctor": "health",
    "beauty_salon": "beauty",
    "hair_care": "beauty",
    "spa": "beauty",
    "gym": "fitness",
    "school": "education",
    "university": "education",
    "establishment": "general",
    "point_of_interest": "general",
    "food_delivery": "food_service",
    "services": "services",
    "education": "education",
    "vehicles": "vehicles",
    "electronics": "electronics",
    "clothing": "clothing",
    "retail": "retail",
    "health": "health",
    "beauty": "beauty",
    "fitness": "fitness",
    "general": "general",
}


class CategoryNormalizer:
    """Normalizes category strings to canonical taxonomy."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._map = mapping or CATEGORY_MAP
        self._normalized = {k.lower().replace(" ", "_"): v for k, v in self._map.items()}

    def normalize(self, raw: str | None) -> Optional[str]:
        """Normalize category to canonical value."""
        if not raw or not isinstance(raw, str):
            return None
        key = re.sub(r"\s+", "_", raw.lower().strip())
        if not key:
            return None
        if key in self._normalized:
            return self._normalized[key]
        for map_key, canonical in self._normalized.items():
            if map_key in key or key in map_key:
                return canonical
        return "other"

    def enrich(self, item: dict) -> dict:
        """Add category_normalized to item. Mutates in place."""
        raw = item.get("category")
        norm = self.normalize(raw)
        if norm:
            item["category_normalized"] = norm
        return item
