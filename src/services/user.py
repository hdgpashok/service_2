import json
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.profile import ProfileRepository
from src.schemas.profile import ProfileExternal, ProfileOut, ProfileJoined
from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserExternal, UserJoined, UserOut


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

    @staticmethod
    async def get_user(user_id: uuid.UUID, session: AsyncSession):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'http://localhost:8000/api/v1/users_profiles/users/{user_id}')

        external_user_data = resp.json()

        internal_user_orm = await UserRepository.select(user_id, session)
        internal_user = UserOut.model_validate(internal_user_orm)

        external_profile = resp.json()['profile']
        internal_profile_orm = await ProfileRepository.select(external_profile['id'], session)
        internal_profile = ProfileOut.model_validate(internal_profile_orm)

        profile_data = {
            **external_profile,
            **internal_profile.model_dump()
        }

        profile = ProfileJoined.model_validate(profile_data)
        user_data = {
            **external_user_data,
            **internal_user.model_dump()
        }

        user_data.pop('profile')
        joined_user = UserJoined(
            **user_data,
            profile=profile
        )

        return joined_user
