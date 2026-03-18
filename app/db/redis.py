import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger
redis_client: aioredis.Redis | None = None
logger = get_logger(__name__)


async def get_redis() -> aioredis.Redis:
    return redis_client


async def connect_redis() -> None:
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await redis_client.ping()
    logger.info("Redis connected successful")


async def disconnect_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        logger.info("Redis disconnected")
