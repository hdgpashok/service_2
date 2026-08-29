from typing import Annotated

from fastapi import Depends

from src.session import SessionDep
from src.services.author import AuthorService


def get_author_service(session: SessionDep) -> AuthorService:
    return AuthorService(session=session)


ServiceDep = Annotated[AuthorService, Depends(get_author_service)]