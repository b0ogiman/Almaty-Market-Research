"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.config import get_settings

settings = get_settings()


def setup_logging(
    level: str | int = "INFO",
    json_format: bool = False,
) -> logging.Logger:
    """Configure application logging."""
    log_level = getattr(logging, level.upper(), logging.INFO) if isinstance(level, str) else level

    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if json_format or settings.environment == "production":
        try:
            import json_log_formatter

            formatter = json_log_formatter.JSONFormatter()
        except ImportError:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Reduce noise from third-party libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )

    return logging.getLogger("app")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module."""
    return logging.getLogger(f"app.{name}")


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter to add extra context to log messages."""

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
