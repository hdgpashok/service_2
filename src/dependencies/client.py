from typing import Annotated

from fastapi import Depends

from src.client.call_api import ClientUserService
from src.dependencies.cache_service import CacheDep


async def get_client() -> ClientUserService:
    return ClientUserService()


ClientDep = Annotated[ClientUserService, Depends(get_client)]