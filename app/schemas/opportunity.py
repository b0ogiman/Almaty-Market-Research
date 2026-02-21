"""Opportunity schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OpportunityScoreRequest(BaseModel):
    """Opportunity scoring request."""

    sector: Optional[str] = Field(None, max_length=255)
    district: Optional[str] = Field(None, max_length=255)
    limit: int = Field(10, ge=1, le=100)


class OpportunityResponse(BaseModel):
    """Single opportunity response."""

    id: UUID
    sector: str
    district: str
    title: str
    description: Optional[str] = None
    score: float
    score_breakdown: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    """Opportunity list response."""

    success: bool = True
    total: int
    items: list[OpportunityResponse]
    page: int = 1
    size: int = 20
