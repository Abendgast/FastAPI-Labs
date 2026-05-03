import os
import time
from fastapi import Request, HTTPException, status
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMITS = {
    "anonymous": (2, 60),
    "authenticated": (10, 60),
}

async def rate_limiter(request: Request, user_id: str | None = None):
    host = request.client.host if request.client else "unknown"
    identity = user_id or host
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit_{identity}"
    now = int(time.time())
    window_start = now - period

    await redis_client.zremrangebyscore(key, min=0, max=window_start)
    request_count = await redis_client.zcard(key)

    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )

    await redis_client.zadd(key, {str(now): now})
    await redis_client.expire(key, period)
