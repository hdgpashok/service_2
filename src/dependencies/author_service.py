from typing import Annotated

from fastapi import Depends

from src.services.author import AuthorService


def get_service() -> AuthorService:
    return AuthorService()


ServiceDep = Annotated[AuthorService, Depends(get_service)]