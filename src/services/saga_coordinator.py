import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.exceptions.server_error import ServerError
from src.exceptions.saga_error import SagaError
from src.models.user import UserModel
from src.repository.user import UserRepository
from src.client.client_main_service import ClientUserService
from src.utils.logger import get_logger
from src.schemas.user import UserExternal

from src.models.compensation_task import CompensationTask, CompensationStatus

logger = get_logger('saga_logger')


class SagaCoordinator:
    def __init__(self):
        self.client = ClientUserService()
        self.user_repo = UserRepository()

    async def create_user_saga(self, external_user: UserExternal, new_user: UserModel, session: AsyncSession):
        try:
            await self.client.user_post_request(external_user)

            await self.user_repo.create(new_user, session)

            logger.info('Saga done, user successfully created')

        except (ServerError, SQLAlchemyError) as e:
            logger.error(f"Saga failed for external user {getattr(external_user, 'id', 'unknown')}: {e}")

            await self._create_compensation_task(external_user.id, session)

            raise SagaError("User creation saga failed") from e

    async def _create_compensation_task(self, user_id: uuid.UUID, session: AsyncSession):
        task = CompensationTask(
            user_id=user_id,
            task_type='delete_external_user',
            status=CompensationStatus.PENDING
        )
        session.add(task)
        logger.info(f'Created compensation task for user id={user_id}')
