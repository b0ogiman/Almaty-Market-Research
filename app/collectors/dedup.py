"""Duplicate detection for business listings."""

from collections.abc import Callable
from typing import Any

from app.logging_config import get_logger

logger = get_logger("collectors.dedup")


def fingerprint(item: dict[str, Any]) -> str:
    """Create fingerprint for duplicate detection."""
    name = (item.get("name") or "").lower().strip()
    cat = (item.get("category") or "").lower().strip()
    district = (item.get("district") or "").lower().strip()
    addr = (item.get("address") or "").lower().strip()[:200]
    return f"{name}|{cat}|{district}|{addr}"


def detect_duplicates(
    items: list[dict[str, Any]],
    key_fn: Callable[[dict[str, Any]], str] = fingerprint,
    seen: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Split items into unique and duplicates.
    Uses external_id as primary; falls back to key_fn for fuzzy dedup.
    """
    seen = seen or set()
    unique = []
    duplicates = []
    for item in items:
        ext_id = item.get("external_id")
        if ext_id and ext_id in seen:
            item["_is_duplicate"] = True
            duplicates.append(item)
            continue
        fp = key_fn(item)
        if fp in seen:
            item["_is_duplicate"] = True
            duplicates.append(item)
            continue
        if ext_id:
            seen.add(ext_id)
        seen.add(fp)
        item["_is_duplicate"] = False
        unique.append(item)
    return unique, duplicates
