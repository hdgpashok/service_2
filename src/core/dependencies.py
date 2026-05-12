from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.db import async_session_maker
from src.core.redis_cache import CacheService
from src.client.call_api import ServiceClient


settings = Settings()


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis_client() -> Redis:
    return Redis(
        host=str(settings.REDIS_HOST),
        port=int(settings.REDIS_PORT),
        db=int(settings.REDIS_DB),
        decode_responses=False,
    )


async def get_cache(redis_client: Redis = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client=redis_client)


async def get_client(cache: CacheService = Depends(get_cache)) -> ServiceClient:
    return ServiceClient(cache=cache)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CacheDep   = Annotated[CacheService, Depends(get_cache)]
ClientDep  = Annotated[ServiceClient, Depends(get_client)]