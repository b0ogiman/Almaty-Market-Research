"""Business listing model for collected raw data."""

from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class BusinessListing(Base, UUIDMixin, TimestampMixin):
    """Raw business listing from Google Maps, Avito, etc."""

    __tablename__ = "business_listings"

    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category_normalized: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    district_mapped: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<BusinessListing(id={self.id}, name={self.name}, source={self.source})>"
