"""Market analysis API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse,
)
from app.services.market_analysis import MarketAnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/market", response_model=AnalysisResponse)
async def run_market_analysis(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """
    Run market analysis for given sector/district.
    Uses cache unless force_refresh=True.
    """
    service = MarketAnalysisService(db)
    result = await service.analyze(
        sector=request.sector,
        district=request.district,
        force_refresh=request.force_refresh,
    )
    return AnalysisResponse.model_validate(result)


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    sector: str | None = Query(None, max_length=255),
    district: str | None = Query(None, max_length=255),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> AnalysisListResponse:
    """List past analysis results with pagination."""
    service = MarketAnalysisService(db)
    items, total = await service.list_analyses(
        sector=sector,
        district=district,
        page=page,
        size=size,
    )
    return AnalysisListResponse(
        success=True,
        total=total,
        items=[AnalysisResponse.model_validate(i) for i in items],
        page=page,
        size=size,
    )
