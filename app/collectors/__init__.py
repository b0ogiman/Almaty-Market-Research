"""Data collection module."""

from app.collectors.base import BaseCollector, CollectResult
from app.collectors.google_maps import GoogleMapsCollector
from app.collectors.avito_mock import AvitoMockCollector
from app.collectors.pipeline import CollectionPipeline

__all__ = [
    "BaseCollector",
    "CollectResult",
    "GoogleMapsCollector",
    "AvitoMockCollector",
    "CollectionPipeline",
]
