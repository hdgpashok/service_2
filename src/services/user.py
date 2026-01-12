import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.profile import ProfileExternal
from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserExternal


class UserService:
    @staticmethod
    async def create_user(user: UserCreate, session: AsyncSession):
        external_user = UserExternal(
            id=uuid.uuid4(),
            title=user.title,
            profile=ProfileExternal(
                id=uuid.uuid4(),
                title=user.profile.title,
                bio=user.profile.bio
            )
        )

        async with httpx.AsyncClient() as client:
            responce = await client.post(
                "http://localhost:8000/api/v1/users_profiles/external_user",
                json=external_user.model_dump(mode='json')
            )
            status_code = responce.status_code

        if status_code == 200:
            return await UserRepository.create(
                user,
                external_user.id,
                external_user.profile.id,
                session
            )
        else:
            return {'error': 'error'}
