"""Custom exceptions and global error handlers."""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.logging_config import get_logger

logger = get_logger("exceptions")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        detail = {"resource": resource}
        if identifier:
            detail["identifier"] = str(identifier)
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationAppError(AppException):
    """Validation error (business logic)."""

    def __init__(self, message: str, detail: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail or {},
        )


class ExternalServiceError(AppException):
    """External service (DB, Redis, AI) failure."""

    def __init__(self, service: str, message: str | None = None) -> None:
        super().__init__(
            message=message or f"External service error: {service}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"service": service},
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions."""
    logger.warning(
        "Application exception: %s",
        exc.message,
        extra={"status_code": exc.status_code, "detail": exc.detail},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "detail": exc.detail,
        },
    )


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    logger.debug("Validation error: %s", errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "detail": {"errors": errors},
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.exception("Unhandled exception: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": {"message": str(exc)} if __debug__ else {},
        },
    )
