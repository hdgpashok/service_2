from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.dependencies.author_service import get_author_service, ServiceDep
from src.session import get_session, SessionDep
from src.schemas.author import AuthorCreate


router = APIRouter(
    prefix="/api/v1/authors",
    tags=["Авторы"],
    dependencies=[
        Depends(get_author_service),
    ]
)


@router.post("", status_code=HTTP_201_CREATED)
async def create_author(
        author: AuthorCreate,
        service: ServiceDep
):
    return await service.create_author(author)


@router.get("/{author_id}", status_code=HTTP_200_OK)
async def get_author(
        author_id: UUID,
        service: ServiceDep
):
    return await service.get_author(author_id)