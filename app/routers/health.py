"""Health check API."""

from sqlalchemy import text

from fastapi import APIRouter

from app.config import get_settings
from app.core.redis_client import redis_ping
from app.database import engine
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Verifies PostgreSQL and Redis connectivity.
    """
    settings = get_settings()
    db_ok = "ok"
    redis_ok = "ok"
    detail = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = "error"
        detail["database_error"] = str(e)

    try:
        if not await redis_ping():
            redis_ok = "unavailable"
    except Exception as e:
        redis_ok = "error"
        detail["redis_error"] = str(e)

    status = "healthy" if db_ok == "ok" else "degraded"
    return HealthResponse(
        status=status,
        version=settings.app_version,
        database=db_ok,
        redis=redis_ok,
        detail=detail if detail else None,
    )
