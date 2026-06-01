from typing import Annotated

from fastapi import Depends

from src.client.call_api import ClientUserService
from src.dependencies.cache_service import CacheDep


async def get_client(cache: CacheDep) -> ClientUserService:
    return ClientUserService(cache=cache)


ClientDep = Annotated[ClientUserService, Depends(get_client)]