from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.dependencies.author_service import get_service, ServiceDep
from src.session import get_session, SessionDep
from src.dependencies.client import get_client, ClientDep
from src.schemas.author import AuthorCreate


router = APIRouter(
    prefix="/api/v1/authors",
    tags=["Авторы"],
    dependencies=[
        Depends(get_session),
        Depends(get_client),
        Depends(get_service),
    ]
)


@router.post("", status_code=HTTP_201_CREATED)
async def create_author(
        author: AuthorCreate,
        session: SessionDep,
        service: ServiceDep
):
    return await service.create_author(author, session)


@router.get("/{author_id}", status_code=HTTP_200_OK)
async def get_author(
        author_id: UUID,
        session: SessionDep,
        service: ServiceDep
):
    return await service.get_author(author_id, session)