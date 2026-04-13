from uuid import UUID

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from fastapi import APIRouter, Depends

from src.services.user import UserService
from src.core.dependencies import SessionDep, ClientDep, get_session, get_client
from src.schemas.user import UserCreate


router = APIRouter(
    prefix="/api/v1/users_profiles",
    tags=['Пользователи и профили'],
    dependencies=[
        Depends(get_session),
        Depends(get_client),
    ]
)


@router.post('/users', status_code=HTTP_201_CREATED)
async def create_user(
        user: UserCreate,
        session: SessionDep,
        client: ClientDep,
):
    return await UserService.create_user(user, session, client)


@router.get('/users/{user_id}', status_code=HTTP_200_OK)
async def get_user(
        user_id: UUID,
        session: SessionDep,
        client: ClientDep,
):
    return await UserService.get_user(user_id, session, client)