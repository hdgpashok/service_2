import uuid

from src.utils.mapping import merge_user_data, create_new_user, create_external_schema

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.server_error import ServerError
from src.exceptions.not_found import ObjectNotFound

from src.client.client_main_service import ClientUserService
from redis_cache import CacheService

from src.schemas.user import UserCreate, UserOutput
from src.repository.user import UserRepository

from utils.logger import get_logger

from services.saga_coordinator import SagaCoordinator


user_service_logger = get_logger('user_service')


class UserService:
    def __init__(self, cache: CacheService):
        self.cache = cache
        self.client = ClientUserService()

    @staticmethod
    async def create_user(
            user: UserCreate,
            session: AsyncSession,
            client: ClientUserService,
    ):
        external_user = create_external_schema(user)
        new_user = create_new_user(user, external_user)

        saga_coordinator = SagaCoordinator()
        await saga_coordinator.create_user_saga(external_user, new_user, session)

        user_service_logger.info(
            f'[CREATE USER] User saved to DB user_id={external_user.id}'
        )

        user_data = user.model_dump()
        user_data['id'] = external_user.id
        user_data['profile']['id'] = external_user.profile.id

        user_service_logger.info(
            f'[CREATE USER] Successfully created user user_id={external_user.id}'
        )

        return UserOutput.model_validate(user_data)

    async def get_user(
            self,
            user_id: uuid.UUID,
            session: AsyncSession,
            client: ClientUserService
    ):
        key = f'user:{user_id}'

        if cached := await self.cache.get(str(key)):
            user_service_logger.info(f'[GET USER] Cache hit user_id={user_id}')
            return cached

        internal = await UserRepository.select(user_id, session)

        if not internal:
            raise ObjectNotFound(object_id=user_id)

        external = await client.user_get_request(user_id)

        try:
            result = merge_user_data(internal, external)

            await self.cache.set(key, result.model_dump(), expire=3600)
            user_service_logger.info(f'[GET USER] User merged and cached user_id={user_id}')

            return result

        except Exception as exc:
            user_service_logger.error(
                f'[GET USER] Data merge error user_id={user_id} error={repr(exc)}'
            )
            raise ServerError("Failed to merge user data") from exc