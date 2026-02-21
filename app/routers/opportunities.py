"""Opportunity scoring and listing API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.opportunity import (
    OpportunityScoreRequest,
    OpportunityResponse,
    OpportunityListResponse,
)
from app.services.opportunity_scoring import OpportunityScoringService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("/score", response_model=OpportunityListResponse)
async def score_opportunities(
    request: OpportunityScoreRequest,
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """
    Score and rank business opportunities for given sector/district.
    Creates new opportunity records and returns them.
    """
    service = OpportunityScoringService(db)
    items = await service.score_opportunities(
        sector=request.sector,
        district=request.district,
        limit=request.limit,
    )
    return OpportunityListResponse(
        success=True,
        total=len(items),
        items=[OpportunityResponse.model_validate(i) for i in items],
        page=1,
        size=len(items),
    )


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    sector: str | None = Query(None, max_length=255),
    district: str | None = Query(None, max_length=255),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """List scored opportunities with pagination."""
    service = OpportunityScoringService(db)
    items, total = await service.list_opportunities(
        sector=sector,
        district=district,
        page=page,
        size=size,
    )
    return OpportunityListResponse(
        success=True,
        total=total,
        items=[OpportunityResponse.model_validate(i) for i in items],
        page=page,
        size=size,
    )
