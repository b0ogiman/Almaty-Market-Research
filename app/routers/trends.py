"""Trends API — historical snapshots per district/category."""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.market_snapshot import MarketSnapshot
from pydantic import BaseModel

router = APIRouter(prefix="/trends", tags=["trends"])


class SnapshotPoint(BaseModel):
    snapshot_date: date
    district: str
    category: Optional[str]
    business_count: int
    avg_rating: Optional[float]
    avg_review_count: Optional[float]
    competition_index: Optional[float]


class TrendsResponse(BaseModel):
    success: bool
    items: list[SnapshotPoint]
    total: int


@router.get("", response_model=TrendsResponse)
async def get_trends(
    district: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> TrendsResponse:
    """Return historical snapshots for the given district/category over the last N days."""
    since = date.today() - timedelta(days=days)
    stmt = select(MarketSnapshot).where(MarketSnapshot.snapshot_date >= since)
    if district:
        stmt = stmt.where(MarketSnapshot.district == district)
    if category:
        stmt = stmt.where(MarketSnapshot.category == category)
    stmt = stmt.order_by(MarketSnapshot.snapshot_date.asc())

    rows = (await db.execute(stmt)).scalars().all()
    items = [
        SnapshotPoint(
            snapshot_date=r.snapshot_date,
            district=r.district,
            category=r.category,
            business_count=r.business_count,
            avg_rating=r.avg_rating,
            avg_review_count=r.avg_review_count,
            competition_index=r.competition_index,
        )
        for r in rows
    ]
    return TrendsResponse(success=True, items=items, total=len(items))
