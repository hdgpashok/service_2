from uuid import UUID

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from fastapi import APIRouter, Depends

from src.dependencies.client import get_client, ClientDep
from src.session import get_session, SessionDep
from src.dependencies.user_service import get_service, ServiceDep
from src.schemas.user import UserCreate


router = APIRouter(
    prefix="/api/v1/users_profiles",
    tags=['Пользователи и профили'],
    dependencies=[
        Depends(get_session),
        Depends(get_client),
        Depends(get_service),
    ]
)


@router.post('/users', status_code=HTTP_201_CREATED)
async def create_user(
        user: UserCreate,
        session: SessionDep,
        service: ServiceDep
):
    return await service.create_user(user, session)


@router.get('/users/{user_id}', status_code=HTTP_200_OK)
async def get_user(
        user_id: UUID,
        session: SessionDep,
        service: ServiceDep
):
    return await service.get_user(user_id, session)