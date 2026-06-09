import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.saga_error import SagaError
from src.models.user import UserModel
from src.repository.user import UserRepository
from src.client.call_api import ClientUserService
from src.core.logger import get_logger
from src.schemas.user import UserExternal


logger = get_logger('saga_logger')


class SagaCoordinator:
    def __init__(self, client: ClientUserService):
        self.client = client

    async def create_user_saga(self, external_user: UserExternal, new_user: UserModel, session: AsyncSession):
        try:

            await self.client.user_post_request(external_user)

            await UserRepository.create(new_user, session)

        except Exception as e:
            await self.rollback(external_user.id)
            raise SagaError()

    async def rollback(self, user_id: uuid.UUID):
        try:
            await self.client.user_delete_request(user_id)

        except Exception as e:
            logger.error(f"Error while deleting the record {user_id}")
