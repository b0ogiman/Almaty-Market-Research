"""Security dependencies for protected write endpoints."""

import secrets

from fastapi import Depends, HTTPException, Request, status

from app.config import Settings, get_settings


async def require_write_api_key(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """
    Require API key on mutating endpoints.

    Uses a configurable header (`auth_header_name`) and constant-time comparison.
    """
    if not settings.write_auth_enabled:
        return

    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Write authentication is enabled but API key is not configured.",
        )

    provided_key = request.headers.get(settings.auth_header_name)
    if not provided_key or not secrets.compare_digest(provided_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
