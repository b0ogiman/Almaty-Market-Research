"""Market analysis schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Market analysis request."""

    sector: Optional[str] = Field(None, max_length=255)
    district: Optional[str] = Field(None, max_length=255)
    force_refresh: bool = False


class AnalysisResponse(BaseModel):
    """Market analysis response."""

    id: UUID
    sector: str
    district: str
    summary: Optional[str] = None
    score: Optional[float] = None
    insights: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    """Analysis list response."""

    success: bool = True
    total: int
    items: list[AnalysisResponse]
    page: int = 1
    size: int = 20
