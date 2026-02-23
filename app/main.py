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
    allow_origins=["*"],
    allow_credentials=True,
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
