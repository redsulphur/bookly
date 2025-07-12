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


async def is_token_blocked(jti: str) -> bool:
    """Check if a jti is in the blocklist."""
    return await jti_blocklist.exists(jti) > 0
