"""Data ingestion schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DataIngestItem(BaseModel):
    """Single market data item for ingestion."""

    sector: str = Field(..., min_length=1, max_length=255)
    district: str = Field(..., min_length=1, max_length=255)
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_value: float
    unit: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    quarter: Optional[int] = Field(None, ge=1, le=4)
    source: str = Field(..., min_length=1, max_length=255)
    raw_json: Optional[dict[str, Any]] = None


class DataIngestRequest(BaseModel):
    """Bulk data ingestion request."""

    items: list[DataIngestItem] = Field(..., min_length=1, max_length=1000)
    source_override: Optional[str] = Field(None, max_length=255)


class DataIngestResponse(BaseModel):
    """Data ingestion response."""

    success: bool = True
    ingested: int
    failed: int = 0
    ids: list[UUID] = []


class DataItemResponse(BaseModel):
    """Single market data item response."""

    id: UUID
    sector: str
    district: str
    metric_name: str
    metric_value: float
    unit: Optional[str]
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DataListResponse(BaseModel):
    """Paginated market data list."""

    success: bool = True
    total: int
    items: list[DataItemResponse]
    page: int = 1
    size: int = 20
