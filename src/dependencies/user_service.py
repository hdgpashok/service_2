from typing import Annotated

from fastapi import Depends

from src.dependencies.coordinator import CoordinatorDep
from src.services.user import UserService
from src.dependencies.cache_service import CacheDep


async def get_service(cache: CacheDep, coordinator: CoordinatorDep) -> UserService:
    return UserService(cache=cache, coordinator=coordinator)


ServiceDep = Annotated[UserService, Depends(get_service)]