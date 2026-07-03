import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.compensation_task import CompensationTask, CompensationStatus


async def create_compensation_task(user_id: uuid.UUID, session: AsyncSession):
    task = CompensationTask(
        user_id=user_id,
        task_type='delete_external_user',
        status=CompensationStatus.PENDING
    )
    session.add(task)
