from uuid import UUID

from fastapi import APIRouter, Depends

from src.db import get_session, SessionDep

from src.schemas.user import UserOut

router = APIRouter(
    prefix="/api/v1/users_profiles",
    tags=['Пользователи и профили'],
    dependencies=[Depends(get_session)]
)


@router.get("/users/{user_id}")
async def get_users(user_id: UUID, session: SessionDep) -> UserOut:
    pass