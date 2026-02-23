"""Google Maps Places API collector."""

import asyncio
from typing import Any

import httpx
from app.collectors.base import BaseCollector, CollectResult, RawListing
from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("collectors.google_maps")


class GoogleMapsCollector(BaseCollector):
    """Collect business listings via Google Maps Places API."""

    source_name = "google_maps"
    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_settings().google_maps_api_key
        if not self.api_key:
            logger.warning("Google Maps API key not configured")

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Async HTTP request to Google API."""
        params["key"] = self.api_key
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self.BASE_URL}/{endpoint}", params=params)
            resp.raise_for_status()
            return resp.json()

    async def _text_search(
        self,
        query: str,
        location: str | None = "43.238949,76.945465",
        radius: int = 50000,
    ) -> list[dict[str, Any]]:
        """Text search for places in Almaty."""
        results = []
        params: dict[str, Any] = {
            "query": query,
            "location": location,
            "radius": radius,
        }
        data = await self._request("textsearch/json", params)
        results.extend(data.get("results", []))
        next_page = data.get("next_page_token")
        while next_page and len(results) < 60:
            await asyncio.sleep(2)
            page_data = await self._request("textsearch/json", {"pagetoken": next_page})
            results.extend(page_data.get("results", []))
            next_page = page_data.get("next_page_token")
        return results

    def _place_to_raw_listing(self, place: dict[str, Any]) -> RawListing:
        """Convert Google Places result to RawListing."""
        geometry = place.get("geometry", {})
        loc = geometry.get("location", {})
        types = place.get("types", [])
        category = types[0] if types else "establishment"
        return RawListing(
            external_id=place.get("place_id", ""),
            source=self.source_name,
            name=place.get("name", ""),
            category=category,
            address=place.get("formatted_address"),
            district=None,
            latitude=loc.get("lat"),
            longitude=loc.get("lng"),
            rating=place.get("rating"),
            review_count=place.get("user_ratings_total"),
            raw=place,
        )

    async def collect(
        self,
        query: str | None = None,
        district: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> CollectResult:
        """Collect business listings from Google Maps."""
        if not self.api_key:
            return CollectResult(
                source=self.source_name,
                errors=["Google Maps API key not configured"],
            )
        query = query or "restaurant Almaty"
        try:
            places = await self._text_search(query)
            raw_items = []
            for p in places[:limit]:
                try:
                    rl = self._place_to_raw_listing(p)
                    if rl.external_id and rl.name:
                        raw_items.append(rl.__dict__)
                except Exception as e:
                    logger.debug("Skip place: %s", str(e))
            return CollectResult(
                source=self.source_name,
                collected=len(places),
                raw_items=raw_items,
            )
        except Exception as e:
            logger.exception("Google Maps collection failed: %s", str(e))
            return CollectResult(
                source=self.source_name,
                errors=[str(e)],
            )
