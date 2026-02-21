"""Pydantic request/response schemas."""

from app.schemas.common import HealthResponse, MessageResponse
from app.schemas.data import DataIngestRequest, DataIngestResponse, DataListResponse
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse,
)
from app.schemas.opportunity import (
    OpportunityScoreRequest,
    OpportunityResponse,
    OpportunityListResponse,
)
from app.schemas.recommendation import RecommendationListResponse

__all__ = [
    "HealthResponse",
    "MessageResponse",
    "DataIngestRequest",
    "DataIngestResponse",
    "DataListResponse",
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisListResponse",
    "OpportunityScoreRequest",
    "OpportunityResponse",
    "OpportunityListResponse",
    "RecommendationListResponse",
]
