"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app import __version__
from app.config import get_settings
from app.exceptions import AppException, app_exception_handler, validation_exception_handler, generic_exception_handler
from app.logging_config import setup_logging, get_logger
from app.routers import data, analysis, opportunities, recommendations, health

settings = get_settings()
setup_logging(level="DEBUG" if settings.debug else "INFO")
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    if settings.is_production:
        if settings.write_auth_enabled and not settings.api_key:
            raise RuntimeError("API key must be configured in production when write auth is enabled.")
        if not settings.postgres_password:
            raise RuntimeError("PostgreSQL password must be configured in production.")
    logger.info("Starting %s v%s", settings.app_name, __version__)
    if settings.scheduler_enabled:
        from app.jobs.scheduler import start_scheduler, stop_scheduler
        start_scheduler()
    yield
    if settings.scheduler_enabled:
        from app.jobs.scheduler import stop_scheduler
        stop_scheduler()
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Local Market Research and Business Opportunity Identification in Almaty",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(data.router, prefix=settings.api_v1_prefix)
app.include_router(analysis.router, prefix=settings.api_v1_prefix)
app.include_router(opportunities.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
