from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.db import async_session_maker
from src.core.redis_cache import CacheService
from src.services.call_api import Client


settings = Settings()


# ====================== Database ======================
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


# ====================== Redis ======================
async def get_redis_client() -> Redis:
    return Redis(
        host=str(settings.REDIS_HOST),
        port=int(settings.REDIS_PORT),
        db=int(settings.REDIS_DB),
        decode_responses=False,
    )


# ====================== Cache ======================
async def get_cache(redis_client: Redis = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client=redis_client)


# ====================== External Client ======================
async def get_client(cache: CacheService = Depends(get_cache)) -> Client:
    return Client(cache=cache)


# ====================== Type Aliases ======================
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CacheDep   = Annotated[CacheService, Depends(get_cache)]
ClientDep  = Annotated[Client, Depends(get_client)]