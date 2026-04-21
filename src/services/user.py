import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.profile import ProfileModel
from src.models.user import UserModel
from src.exceptions.server_error import ServerError
from src.exceptions.not_found import ObjectNotFound
from src.services.call_api import ClientMainService
from src.schemas.profile import ProfileExternal, ProfileJoined
from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserExternal, UserJoined, UserOutput

from src.core.logger import get_logger


user_service_logger = get_logger('user_service')


class UserService:

    @staticmethod
    async def create_user(
            user: UserCreate,
            session: AsyncSession,
            client: ClientMainService,
    ):
        external_user = UserExternal(
            id=uuid.uuid4(),
            title=user.title,
            profile=ProfileExternal(
                id=uuid.uuid4(),
                title=user.profile.title,
                bio=user.profile.bio
            )
        )

        await client.user_post_request(external_user)
        user_service_logger.info(
            f'[CREATE USER] External user created user_id={external_user.id}'
        )

        try:
            new_profile = ProfileModel(
                **user.profile.model_dump(exclude={'title', 'bio'}),
                id=external_user.profile.id
            )

            new_user = UserModel(id=external_user.id, profile=new_profile)

            for key, value in user.model_dump(exclude={'profile'}).items():
                setattr(new_user, key, value)

            await UserRepository.create(new_user, session)

            user_service_logger.info(
                f'[CREATE USER] User saved to DB user_id={external_user.id}'
            )

        except Exception as exc:
            user_service_logger.error(
                f'[CREATE USER] DB error, rolling back external user '
                f'user_id={external_user.id} error={repr(exc)}'
            )

            await client.user_delete_request(external_user.id)
            user_service_logger.info(
                f'[CREATE USER] Rollback successful user_id={external_user.id}'
            )
            raise ServerError("Failed to save user in local database") from exc

        user_data = user.model_dump()
        user_data['id'] = external_user.id
        user_data['profile']['id'] = external_user.profile.id

        user_service_logger.info(
            f'[CREATE USER] Successfully created user user_id={external_user.id}'
        )

        return UserOutput.model_validate(user_data)

    @staticmethod
    async def get_user(user_id: uuid.UUID, session: AsyncSession, client: ClientMainService):
        internal = await UserRepository.select(user_id, session)
        if not internal:
            raise ObjectNotFound(object_id=user_id)

        external = await client.user_get_request(user_id)

        try:
            int_profile_data = {}

            internal_profile = (
                internal.profile if hasattr(internal, 'profile')
                else internal.get('profile') if isinstance(internal, dict)
                else None
            )

            if internal_profile:
                int_profile_data = {
                    "bio": getattr(internal_profile, "bio", None) or internal_profile.get("bio") if isinstance(internal_profile, dict) else getattr(internal_profile, "bio", None),
                    "nickname": getattr(internal_profile, "nickname", None) or internal_profile.get("nickname") if isinstance(internal_profile, dict) else getattr(internal_profile, "nickname", None)
                }

            ext_profile_data = external.get("profile") or {}
            profile_merge = {**int_profile_data, **ext_profile_data}
            profile = ProfileJoined.model_validate(profile_merge)

            user_data = {
                "id": external.get("id") or (internal.id if hasattr(internal, 'id') else internal.get('id')),
                "first_name": external.get("first_name") or (internal.first_name if hasattr(internal, 'first_name') else internal.get('first_name')),
                "last_name": external.get("last_name") or (internal.last_name if hasattr(internal, 'last_name') else internal.get('last_name')),
                "title": external.get("title") or ext_profile_data.get("title"),
                "profile": profile
            }

            return UserJoined(**user_data)

        except Exception as exc:
            user_service_logger.error(f'[GET USER] Data merge error: {repr(exc)}')
            raise ServerError("Failed to merge user data") from exc
