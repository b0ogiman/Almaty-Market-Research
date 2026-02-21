"""Redis client for caching - minimal integration."""

import json
from typing import Any, Optional

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("redis")

_redis_client: Optional[Any] = None


async def get_redis() -> Optional[Any]:
    """Get Redis connection. Returns None if Redis unavailable or disabled."""
    global _redis_client
    settings = get_settings()
    if not settings.cache_enabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis_client.ping()
        logger.info("Redis connected")
        return _redis_client
    except Exception as e:
        logger.warning("Redis unavailable: %s. Caching disabled.", str(e))
        return None


async def cache_get(key: str) -> Optional[dict[str, Any]]:
    """Get cached value as dict. Returns None if miss or Redis unavailable."""
    client = await get_redis()
    if not client:
        return None
    try:
        val = await client.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        logger.debug("Cache get error for %s: %s", key, str(e))
    return None


async def cache_set(key: str, value: dict[str, Any], ttl: int = 3600) -> bool:
    """Set cache value. Returns True if success."""
    client = await get_redis()
    if not client:
        return False
    try:
        await client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.debug("Cache set error for %s: %s", key, str(e))
    return False


async def cache_delete(key: str) -> bool:
    """Delete cache key."""
    client = await get_redis()
    if not client:
        return False
    try:
        await client.delete(key)
        return True
    except Exception:
        pass
    return False


async def redis_ping() -> bool:
    """Check Redis connectivity."""
    client = await get_redis()
    if not client:
        return False
    try:
        return await client.ping()
    except Exception:
        return False
