"""2GIS Catalog API collector."""

import asyncio
from typing import Any

import httpx
from app.collectors.base import BaseCollector, CollectResult, RawListing
from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("collectors.twogis")

BASE_URL = "https://catalog.api.2gis.com/3.0/items"

# Almaty district bounding boxes for coordinate-based mapping
DISTRICT_BOUNDS: list[dict[str, Any]] = [
    {"name": "Bostandyq", "lat_min": 43.24, "lat_max": 43.32, "lon_min": 76.87, "lon_max": 77.00},
    {"name": "Medeu",     "lat_min": 43.22, "lat_max": 43.30, "lon_min": 76.96, "lon_max": 77.10},
    {"name": "Almaly",    "lat_min": 43.24, "lat_max": 43.28, "lon_min": 76.89, "lon_max": 76.97},
    {"name": "Auezov",    "lat_min": 43.20, "lat_max": 43.27, "lon_min": 76.80, "lon_max": 76.92},
    {"name": "Alatau",    "lat_min": 43.15, "lat_max": 43.24, "lon_min": 76.75, "lon_max": 76.90},
    {"name": "Nauryzbay", "lat_min": 43.10, "lat_max": 43.22, "lon_min": 76.65, "lon_max": 76.85},
    {"name": "Turksib",   "lat_min": 43.28, "lat_max": 43.38, "lon_min": 76.88, "lon_max": 77.05},
    {"name": "Zhetysu",   "lat_min": 43.28, "lat_max": 43.38, "lon_min": 76.98, "lon_max": 77.15},
]


def _coords_to_district(lat: float | None, lon: float | None) -> str | None:
    if lat is None or lon is None:
        return None
    for b in DISTRICT_BOUNDS:
        if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
            return b["name"]
    return None


class TwoGisCollector(BaseCollector):
    """Collect business listings via 2GIS Catalog API."""

    source_name = "2gis"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_settings().twogis_api_key
        if not self.api_key:
            logger.warning("2GIS API key not configured")

    async def _search(
        self,
        query: str,
        lat: float = 43.238949,
        lon: float = 76.945465,
        radius: int = 40000,
        page_size: int = 10,
        pages: int = 10,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(1, pages + 1):
                params: dict[str, Any] = {
                    "q": query,
                    "location": f"{lon},{lat}",
                    "radius": radius,
                    "key": self.api_key,
                    "page_size": page_size,
                    "page": page,
                    "fields": "items.point,items.address,items.rubrics,items.reviews,items.org",
                }
                try:
                    resp = await client.get(BASE_URL, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("result", {}).get("items", [])
                    if not items:
                        break
                    results.extend(items)
                    if len(items) < page_size:
                        break
                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.warning("2GIS page %d failed: %s", page, str(e))
                    break
        return results

    def _item_to_raw_listing(self, item: dict[str, Any]) -> RawListing:
        point = item.get("point", {})
        lat = point.get("lat")
        lon = point.get("lon")
        rubrics = item.get("rubrics", [])
        category = rubrics[0].get("name", "establishment") if rubrics else "establishment"
        reviews = item.get("reviews", {}) or {}
        address_str = item.get("address_name") or item.get("full_name")
        district = _coords_to_district(lat, lon)
        return RawListing(
            external_id=str(item.get("id", "")),
            source=self.source_name,
            name=item.get("name", ""),
            category=category,
            address=address_str,
            district=district,
            latitude=lat,
            longitude=lon,
            rating=reviews.get("general_rating") or reviews.get("org_rating"),
            review_count=reviews.get("general_review_count") or reviews.get("org_review_count"),
            raw=item,
        )

    async def collect(
        self,
        query: str | None = None,
        district: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> CollectResult:
        if not self.api_key:
            return CollectResult(
                source=self.source_name,
                errors=["2GIS API key not configured"],
            )
        query = query or "кафе Алматы"
        pages = max(1, min(limit // 10 + 1, 20))
        try:
            items = await self._search(query, pages=pages)
            raw_items = []
            for item in items[:limit]:
                try:
                    rl = self._item_to_raw_listing(item)
                    if rl.external_id and rl.name:
                        raw_items.append(rl.__dict__)
                except Exception as e:
                    logger.debug("Skip 2GIS item: %s", str(e))
            return CollectResult(
                source=self.source_name,
                collected=len(items),
                raw_items=raw_items,
            )
        except Exception as e:
            logger.exception("2GIS collection failed: %s", str(e))
            return CollectResult(
                source=self.source_name,
                errors=[str(e)],
            )
