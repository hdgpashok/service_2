from typing import Annotated

from fastapi import Depends

from src.services.user import UserService
from src.dependencies.cache_service import CacheDep


async def get_service(cache: CacheDep) -> UserService:
    return UserService(cache=cache)


ServiceDep = Annotated[UserService, Depends(get_service)]