"""Recommendations API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.recommendation import (
    RecommendationListResponse,
    RecommendationItem,
)
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationListResponse)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> RecommendationListResponse:
    """
    Get top business recommendations.
    Aggregates from scored opportunities, uses cache when available.
    """
    service = RecommendationService(db)
    items = await service.get_recommendations(limit=limit)
    return RecommendationListResponse(
        success=True,
        total=len(items),
        items=[RecommendationItem.model_validate(i) for i in items],
        limit=limit,
    )
