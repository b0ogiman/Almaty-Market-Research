"""Daily market snapshot for trend analysis."""

from datetime import date
from typing import Optional

from sqlalchemy import Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MarketSnapshot(Base, UUIDMixin, TimestampMixin):
    """Aggregated daily snapshot: business count per district/category."""

    __tablename__ = "market_snapshots"
    __table_args__ = (
        UniqueConstraint("snapshot_date", "district", "category", name="uq_snapshot_district_category"),
    )

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    business_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_review_count: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    competition_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
