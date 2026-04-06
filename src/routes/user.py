from uuid import UUID

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from fastapi import APIRouter, Depends

from src.services.user import UserService
from src.db import get_session, SessionDep

from src.schemas.user import UserOut, UserCreate

router = APIRouter(
    prefix="/api/v1/users_profiles",
    tags=['Пользователи и профили'],
    dependencies=[Depends(get_session)]
)


@router.post('/users', status_code=HTTP_201_CREATED)
async def create_user(user: UserCreate, session: SessionDep) -> UserOut:
    return await UserService.create_user(user, session)


@router.get('/users/{user_id}', status_code=HTTP_200_OK)
async def get_user(user_id: UUID, session: SessionDep) -> UserOut:
    return await UserService.get_user(user_id, session)