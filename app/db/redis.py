import redis.asyncio as redis

from app.config import config

jti_blocklist = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True,
)


async def add_jti_to_blocklist(jti: str) -> None:
    """Add a jti to the blocklist."""
    await jti_blocklist.set(
        name=jti, value="blocked", ex=config.JWT_ACCESS_TOKEN_EXPIRE_SECONDS
    )


async def is_token_revoked(jti: str) -> bool:
    """Check if a jti is in the blocklist."""
    if not config.ENABLE_REDIS_BLOCKLIST:
        return False  # Skip Redis check if disabled

    try:
        return await jti_blocklist.exists(jti) > 0
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False  # Allow access if Redis is down (development only)
