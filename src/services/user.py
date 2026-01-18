import asyncio
import random
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.profile import ProfileRepository
from src.schemas.profile import ProfileExternal, ProfileOut, ProfileJoined
from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserExternal, UserJoined, UserOut, UserOutput

from src.core.logger import get_logger

from src.core.config import Settings

settings = Settings()


user_service_loger = get_logger('user_service')


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
            for attempt in range(4):
                try:
                    responce = await client.post(
                        f"{settings.base_url}/external_user",
                        json=external_user.model_dump(mode='json')
                    )
                    responce.raise_for_status()
                    break

                except Exception as e:
                    if attempt == 3:
                        raise e

                    delay = 0.1 * (2 ** attempt)
                    jitter = random.uniform(0, delay * 0.3)

                    user_service_loger.info(f'attempt №{attempt + 1} delay {delay + jitter}')
                    await asyncio.sleep(delay + jitter)

        await UserRepository.create(
            user,
            external_user.id,
            external_user.profile.id,
            session
        )
        user_data = user.model_dump()
        user_data['id'] = external_user.id
        user_data['profile']['id'] = external_user.profile.id
        return UserOutput.model_validate(user_data)

    @staticmethod
    async def get_user(user_id: uuid.UUID, session: AsyncSession):
        async with httpx.AsyncClient() as client:
            for attempt in range(4):
                try:
                    resp = await client.get(f'{settings.base_url}/users/{user_id}')
                    external_user_data = resp.json()
                    break

                except Exception as e:
                    if attempt == 3:
                        raise e

                    delay = 0.1 * (2 ** attempt)
                    jitter = random.uniform(0, delay * 0.3)
                    user_service_loger.info(f'attempt №{attempt + 1} delay {delay + jitter}')
                    await asyncio.sleep(delay + jitter)

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
