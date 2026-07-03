from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from src.utils.config import settings
from src.redis_cache import CacheService


async def get_redis_client() -> Redis:
    return Redis(
        host=str(settings.REDIS_HOST),
        port=int(settings.REDIS_PORT),
        db=int(settings.REDIS_DB),
        decode_responses=False,
    )


async def get_cache(redis_client: Redis = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client=redis_client)


CacheDep = Annotated[CacheService, Depends(get_cache)]