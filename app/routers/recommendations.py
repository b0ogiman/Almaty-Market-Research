"""Recommendations API."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security import require_write_api_key
from app.schemas.recommendation import (
    RecommendationListResponse,
    RecommendationItem,
)
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationListResponse)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    _: None = Depends(require_write_api_key),
    db: AsyncSession = Depends(get_db),
) -> RecommendationListResponse:
    """
    Get top business recommendations.
    Aggregates from scored opportunities, uses cache when available.
    """
    try:
        service = RecommendationService(db)
        items = await service.get_recommendations(limit=limit)
        return RecommendationListResponse(
            success=True,
            total=len(items),
            items=[RecommendationItem.model_validate(i) for i in items],
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
