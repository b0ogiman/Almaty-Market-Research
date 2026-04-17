"""Health check API."""

from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import get_settings
from app.core.redis_client import redis_ping
from app.database import engine, get_db
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


class StatsResponse(BaseModel):
    total_listings: int
    by_source: dict[str, int]
    by_category: dict[str, int]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    from app.models.business_listing import BusinessListing
    total = (await db.execute(
        select(func.count()).select_from(BusinessListing).where(BusinessListing.is_active == True)
    )).scalar() or 0
    sources = (await db.execute(
        select(BusinessListing.source, func.count()).where(BusinessListing.is_active == True).group_by(BusinessListing.source)
    )).all()
    cats = (await db.execute(
        select(BusinessListing.category_normalized, func.count()).where(BusinessListing.is_active == True).group_by(BusinessListing.category_normalized)
    )).all()
    return StatsResponse(
        total_listings=total,
        by_source={s: c for s, c in sources},
        by_category={(cat or "other"): c for cat, c in cats},
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Verifies PostgreSQL and Redis connectivity.
    """
    settings = get_settings()
    db_ok = "ok"
    redis_ok = "ok"
    detail = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = "error"
        detail["database_error"] = str(e)

    try:
        if not await redis_ping():
            redis_ok = "unavailable"
    except Exception as e:
        redis_ok = "error"
        detail["redis_error"] = str(e)

    status = "healthy" if db_ok == "ok" else "degraded"
    return HealthResponse(
        status=status,
        version=settings.app_version,
        database=db_ok,
        redis=redis_ok,
        detail=detail if detail else None,
    )
