import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.not_found import ObjectNotFound
from src.services.call_api import CallApi
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

        await CallApi.user_post_request(external_user)

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
        internal_user_orm = await UserRepository.select(user_id, session)

        if not internal_user_orm:
            raise ObjectNotFound(object_id=user_id)

        external_user_data = await CallApi.user_get_request(user_id)

        internal_user = UserOut.model_validate(internal_user_orm)

        external_profile = external_user_data['profile']
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
