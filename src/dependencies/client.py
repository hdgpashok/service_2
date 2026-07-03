from typing import Annotated

from fastapi import Depends

from src.client.client_main_service import ClientUserService


async def get_client() -> ClientUserService:
    return ClientUserService()


ClientDep = Annotated[ClientUserService, Depends(get_client)]