"""
Redis client — async connection pool.

Used for:
- WebSocket pub/sub (broadcasting bid events)
- Caching active auction current-bid state
- (Future) Rate limiting counters
"""

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level connection pool (created once at startup)
_redis_pool: Redis | None = None


async def init_redis() -> None:
    """Create the Redis connection pool. Called at application startup."""
    global _redis_pool
    _redis_pool = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    # Verify connectivity
    await _redis_pool.ping()
    logger.info("redis.connected", url=settings.redis_url)


async def close_redis() -> None:
    """Close the Redis connection pool. Called at application shutdown."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("redis.disconnected")


def get_redis_pool() -> Redis:
    """Return the module-level Redis pool (raises if not initialized)."""
    if _redis_pool is None:
        raise RuntimeError("Redis not initialized — call init_redis() first")
    return _redis_pool


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency that yields the Redis connection pool.

    The pool manages individual connections internally.
    Do NOT call .close() on the returned object.

    Usage:
        @router.get("/")
        async def handler(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")
    """
    yield get_redis_pool()
