"""Data validation and cleaning for collected listings."""

import re
from typing import Any

from app.logging_config import get_logger

logger = get_logger("collectors.validation")


def clean_string(value: str | None, max_len: int = 500) -> str | None:
    """Clean and truncate string."""
    if value is None:
        return None
    s = re.sub(r"\s+", " ", str(value).strip())
    return s[:max_len] if s else None


def clean_float(value: Any, lo: float | None = None, hi: float | None = None) -> float | None:
    """Parse and clamp float."""
    if value is None:
        return None
    try:
        f = float(value)
        if lo is not None and f < lo:
            return lo
        if hi is not None and f > hi:
            return hi
        return f
    except (TypeError, ValueError):
        return None


def clean_int(value: Any, lo: int | None = None, hi: int | None = None) -> int | None:
    """Parse and clamp int."""
    if value is None:
        return None
    try:
        i = int(value)
        if lo is not None and i < lo:
            return lo
        if hi is not None and i > hi:
            return hi
        return i
    except (TypeError, ValueError):
        return None


def validate_listing(item: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """
    Validate and clean a raw listing dict.
    Returns (cleaned_dict, error_message). If valid, error_message is None.
    """
    ext_id = item.get("external_id") or item.get("place_id")
    if not ext_id:
        return None, "missing external_id"
    ext_id = str(ext_id).strip()[:255]
    if not ext_id:
        return None, "empty external_id"

    name = clean_string(item.get("name"), 500)
    if not name:
        return None, "missing or empty name"

    category = clean_string(item.get("category"), 255)
    if not category:
        category = "unknown"

    source = clean_string(item.get("source"), 64)
    if not source:
        source = "unknown"

    return {
        "external_id": ext_id,
        "source": source,
        "name": name,
        "category": category,
        "address": clean_string(item.get("address"), 1000),
        "district": clean_string(item.get("district"), 255),
        "latitude": clean_float(item.get("latitude"), -90, 90),
        "longitude": clean_float(item.get("longitude"), -180, 180),
        "rating": clean_float(item.get("rating"), 0, 5),
        "review_count": clean_int(item.get("review_count"), 0, 10_000_000),
        "price_min": clean_float(item.get("price_min"), 0),
        "price_max": clean_float(item.get("price_max"), 0),
        "description": clean_string(item.get("description"), 5000),
        "raw": item.get("raw"),
    }, None


def validate_batch(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate a batch of listings. Returns (valid_items, errors)."""
    valid = []
    errors = []
    for i, item in enumerate(items):
        cleaned, err = validate_listing(item)
        if cleaned:
            valid.append(cleaned)
        else:
            errors.append(f"item[{i}]: {err}")
    return valid, errors
