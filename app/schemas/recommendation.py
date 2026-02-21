"""Recommendation schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    """Single recommendation item."""

    id: UUID
    sector: str
    district: str
    title: str
    rationale: Optional[str] = None
    score: float
    rank: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationListResponse(BaseModel):
    """Recommendation list response."""

    success: bool = True
    total: int
    items: list[RecommendationItem]
    limit: int = 10
