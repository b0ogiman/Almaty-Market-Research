"""Data ingestion and listing API."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security import require_write_api_key
from app.schemas.data import (
    DataIngestRequest,
    DataIngestResponse,
    DataListResponse,
    DataItemResponse,
)
from app.services.data_ingestion import DataIngestionService

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/ingest", response_model=DataIngestResponse)
async def ingest_data(
    request: DataIngestRequest,
    _: None = Depends(require_write_api_key),
    db: AsyncSession = Depends(get_db),
) -> DataIngestResponse:
    """
    Ingest market data in bulk.
    Accepts up to 1000 items per request.
    """
    try:
        service = DataIngestionService(db)
        ingested, failed, ids = await service.ingest(request)
        return DataIngestResponse(
            success=True,
            ingested=ingested,
            failed=failed,
            ids=ids,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )


@router.get("", response_model=DataListResponse)
async def list_data(
    sector: str | None = Query(None, max_length=255),
    district: str | None = Query(None, max_length=255),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> DataListResponse:
    """List ingested market data with optional filters and pagination."""
    try:
        service = DataIngestionService(db)
        items, total = await service.list_data(
            sector=sector,
            district=district,
            page=page,
            size=size,
        )
        return DataListResponse(
            success=True,
            total=total,
            items=[DataItemResponse.model_validate(i) for i in items],
            page=page,
            size=size,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
