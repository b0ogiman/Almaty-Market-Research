"""Common schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Generic message response."""

    success: bool = True
    message: str = "OK"
    detail: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    database: str = "ok"
    redis: str = "ok"
    detail: Optional[dict[str, Any]] = Field(default=None, exclude_none=True)
