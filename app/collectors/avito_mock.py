"""Mock Avito-style data adapter for development and testing."""

import random
import uuid
from typing import Any

from app.collectors.base import BaseCollector, CollectResult

# Almaty districts
ALMATY_DISTRICTS = [
    "Alatau",
    "Almaly",
    "Auezov",
    "Bostandyq",
    "Medeu",
    "Nauryzbay",
    "Turksib",
    "Zhetysu",
]

# Avito-style categories
CATEGORIES = [
    "real_estate",
    "vehicles",
    "electronics",
    "clothing",
    "food_delivery",
    "services",
    "beauty",
    "education",
    "restaurants",
    "retail",
    "pharmacy",
    "gym",
]

SAMPLE_NAMES = [
    "Almaty Premium", "City Center", "Green Market", "Family Store",
    "Best Service", "Quick Fix", "Smart Choice", "Local Hub",
    "Express Delivery", "Quality Plus", "Urban Style", "Central Point",
]

DESCRIPTIONS = [
    "Great location, modern facility.",
    "Professional service, competitive prices.",
    "Open daily. Contact for details.",
    "Serving Almaty since 2020.",
]


class AvitoMockCollector(BaseCollector):
    """Mock collector simulating Avito-style listing data."""

    source_name = "avito_mock"

    async def collect(
        self,
        query: str | None = None,
        district: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> CollectResult:
        """Generate mock Avito-style listings."""
        districts = [district] if district else ALMATY_DISTRICTS
        raw_items = []
        for i in range(min(limit, 100)):
            cat = random.choice(CATEGORIES)
            d = random.choice(districts)
            name = f"{random.choice(SAMPLE_NAMES)} {d}"
            ext_id = f"avito_{uuid.uuid4().hex[:12]}"
            price = random.uniform(5000, 500000) if random.random() > 0.3 else None
            raw_items.append({
                "external_id": ext_id,
                "source": self.source_name,
                "name": name,
                "category": cat,
                "address": f"Almaty, {d} district",
                "district": d,
                "latitude": 43.2 + random.uniform(-0.1, 0.1),
                "longitude": 76.8 + random.uniform(-0.2, 0.2),
                "rating": round(random.uniform(3.0, 5.0), 1) if random.random() > 0.4 else None,
                "review_count": random.randint(0, 500) if random.random() > 0.5 else None,
                "price_min": price,
                "price_max": price * 1.2 if price else None,
                "description": random.choice(DESCRIPTIONS),
                "raw": {"mock": True, "seed": i},
            })
        return CollectResult(
            source=self.source_name,
            collected=len(raw_items),
            raw_items=raw_items,
        )
