import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.profile import ProfileModel
from src.models.user import UserModel
from src.exceptions.server_error import ServerError
from src.exceptions.not_found import ObjectNotFound
from src.services.call_api import Client
from src.schemas.profile import ProfileExternal, ProfileOut, ProfileJoined
from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserExternal, UserJoined, UserOut, UserOutput

from src.core.logger import get_logger

from src.core.config import Settings


settings = Settings()

api = Client()
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

        try:
            await api.user_post_request(external_user)
            user_service_loger.info(
                f'[CREATE USER] External user created user_id={external_user.id}'
            )

        except Exception as exc:
            user_service_loger.error(
                f'[CREATE USER] Failed to create external user '
                f'user_id={external_user.id} error={repr(exc)}'
            )
            raise

        new_profile = ProfileModel(
            **user.profile.model_dump(exclude={'title', 'bio'}),
            id=external_user.profile.id
        )

        new_user = UserModel(id=external_user.id, profile=new_profile)

        for key, value in user.model_dump(exclude={'profile'}).items():
            setattr(new_user, key, value)

        try:
            await UserRepository.create(new_user, session)
            user_service_loger.info(
                f'[CREATE USER] User saved to DB user_id={external_user.id}'
            )

        except Exception as exc:
            user_service_loger.error(
                f'[CREATE USER] DB error, rolling back external user '
                f'user_id={external_user.id} error={repr(exc)}'
            )

            try:
                await api.user_delete_request(external_user.id)
                user_service_loger.info(
                    f'[CREATE USER] Rollback user_id={external_user.id}'
                )
            except Exception as delete_exc:
                user_service_loger.critical(
                    f'[CREATE USER] CRITICAL: failed to rollback external user '
                    f'user_id={external_user.id} error={repr(delete_exc)}'
                )

            raise ServerError(status=exc.status_code)

        user_data = user.model_dump()
        user_data['id'] = external_user.id
        user_data['profile']['id'] = external_user.profile.id

        user_service_loger.info(
            f'[CREATE USER] Successfully created user user_id={external_user.id}'
        )

        return UserOutput.model_validate(user_data)

    @staticmethod
    async def get_user(user_id: uuid.UUID, session: AsyncSession):
        try:
            internal = await UserRepository.select(user_id, session)
        except Exception as exc:
            user_service_loger.error(
                f'[GET USER] DB error user_id={user_id} error={repr(exc)}'
            )
            raise

        if not internal:
            user_service_loger.warning(
                f'[GET USER] User not found internally user_id={user_id}'
            )
            raise ObjectNotFound(object_id=user_id)

        user_service_loger.info(
            f'[GET USER] Internal user fetched user_id={user_id}'
        )

        try:
            external = await api.user_get_request(user_id)
        except Exception as exc:
            user_service_loger.error(
                f'[GET USER] External API error user_id={user_id} error={repr(exc)}'
            )
            raise

        user_service_loger.info(
            f'[GET USER] External user fetched user_id={user_id}'
        )

        try:
            # ✅ профиль
            profile = ProfileJoined.model_validate({
                **external.get("profile", {}),
                **internal.get("profile", {})
            })

            # ✅ пользователь
            user_data = {
                "id": external.get("id", internal["id"]),
                "first_name": external.get("first_name", internal["first_name"]),
                "last_name": external.get("last_name", internal["last_name"]),
                "title": external.get("title"),
            }

            user_service_loger.info(
                f'[GET USER] Successfully merged user data user_id={user_id}'
            )

            return UserJoined(**user_data, profile=profile)

        except Exception as exc:
            user_service_loger.error(
                f'[GET USER] Data merge/validation error user_id={user_id} '
                f'error={repr(exc)}'
            )
            raise