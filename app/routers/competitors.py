"""Top competitors endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.business_listing import BusinessListing

router = APIRouter(prefix="/competitors", tags=["competitors"])


class CompetitorItem(BaseModel):
    id: str
    name: str
    category: Optional[str]
    category_normalized: Optional[str]
    district: Optional[str]
    address: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]


class CompetitorsResponse(BaseModel):
    success: bool
    items: list[CompetitorItem]
    total: int


@router.get("", response_model=CompetitorsResponse)
async def get_competitors(
    sector: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> CompetitorsResponse:
    """Return top businesses by review count for given sector/district."""
    q = (
        select(BusinessListing)
        .where(
            BusinessListing.is_active == True,
            BusinessListing.source == "2gis",
            BusinessListing.rating.isnot(None),
            BusinessListing.review_count.isnot(None),
        )
    )
    if sector:
        q = q.where(BusinessListing.category_normalized == sector)
    if district:
        q = q.where(
            (BusinessListing.district_mapped == district) |
            (BusinessListing.district == district)
        )
    q = q.order_by(BusinessListing.review_count.desc()).limit(limit)

    rows = (await db.execute(q)).scalars().all()

    # total count for same filters
    count_q = select(func.count()).select_from(BusinessListing).where(
        BusinessListing.is_active == True,
        BusinessListing.source == "2gis",
        BusinessListing.rating.isnot(None),
    )
    if sector:
        count_q = count_q.where(BusinessListing.category_normalized == sector)
    if district:
        count_q = count_q.where(
            (BusinessListing.district_mapped == district) |
            (BusinessListing.district == district)
        )
    total = (await db.execute(count_q)).scalar() or 0

    return CompetitorsResponse(
        success=True,
        total=total,
        items=[
            CompetitorItem(
                id=str(r.id),
                name=r.name,
                category=r.category,
                category_normalized=r.category_normalized,
                district=r.district_mapped or r.district,
                address=r.address,
                rating=r.rating,
                review_count=r.review_count,
            )
            for r in rows
        ],
    )
