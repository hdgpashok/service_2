import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.saga_error import SagaError
from src.models.user import UserModel
from src.repository.user import UserRepository
from src.client.call_api import ClientUserService
from src.core.logger import get_logger
from src.schemas.user import UserExternal

from src.models.compensation_task import CompensationTask, CompensationStatus

logger = get_logger('saga_logger')


class SagaCoordinator:
    def __init__(self):
        self.client = ClientUserService()

    async def create_user_saga(self, external_user: UserExternal, new_user: UserModel, session: AsyncSession):
        try:
            await self.client.user_post_request(external_user)
            raise Exception('test error')

            await UserRepository.create(new_user, session)

            logger.info('Saga done, user successfully created')
        except Exception as e:
            logger.error(f"Saga failed for external user {getattr(external_user, 'id', 'unknown')}: {e}")

            # Создаём задачу на компенсацию
            await self._create_compensation_task(external_user.id, session)

            raise SagaError("User creation saga failed") from e

    async def _create_compensation_task(self, user_id: uuid.UUID, session: AsyncSession):
        try:
            task = CompensationTask(
                user_id=user_id,
                task_type='delete_external_user',
                status=CompensationStatus.PENDING
            )
            session.add(task)
            await session.commit()
            logger.info(f'Created compensation task for user id={user_id}')

        except Exception as exc:
            logger.critical('error while creating compensation task')

    async def rollback(self, user_id: uuid.UUID):
        try:
            await self.client.user_delete_request(user_id)

        except Exception as e:
            logger.error(f"Error while deleting the record {user_id}")
