import asyncio

from sqlalchemy import select

from starlette.status import HTTP_404_NOT_FOUND

from src.db import async_session_maker
from src.models.compensation_task import CompensationTask, CompensationStatus
from src.client.client_main_user_service import ClientUserService
from src.utils.logger import get_logger

logger = get_logger('compensation_worker')


async def process_task(task_id: int):
    client = ClientUserService()

    async with async_session_maker() as session:
        task = await session.get(
            CompensationTask,
            task_id,
            with_for_update=True,
        )

        if not task:
            return

        task.status = CompensationStatus.IN_PROGRESS
        user_id = task.user_id

        await session.commit()

    logger.info(f"Starting compensation for user {user_id}")

    try:
        await client.user_delete_request(user_id)

        async with async_session_maker() as session:
            task = await session.get(CompensationTask, task_id)

            if task:
                task.status = CompensationStatus.COMPLETED
                await session.commit()

        logger.info(f"✓ Compensation SUCCESS for user {user_id}")

    except Exception as exc:
        async with async_session_maker() as session:
            task = await session.get(CompensationTask, task_id)

            if not task:
                return

            if getattr(exc, "status_code", None) == HTTP_404_NOT_FOUND:
                task.status = CompensationStatus.COMPLETED
                logger.info(f"User {user_id} already deleted ({HTTP_404_NOT_FOUND})")
            else:
                task.status = CompensationStatus.FAILED
                task.last_error = str(exc)[:500]
                logger.warning(
                    f"Compensation FAILED for user {user_id}: {exc}"
                )

            await session.commit()


async def run_worker():
    logger.info("Compensation Worker started...")

    while True:
        try:
            async with async_session_maker() as session:
                result = await session.execute(
                    select(CompensationTask.id)
                    .where(
                        CompensationTask.status == CompensationStatus.PENDING
                    )
                    .with_for_update(skip_locked=True)
                    .limit(20)
                )

                task_ids = [row[0] for row in result.all()]

            for task_id in task_ids:
                await process_task(task_id)

        except Exception as exc:
            logger.error(f"Worker loop error: {exc}")

        await asyncio.sleep(15)

if __name__ == '__main__':
    asyncio.run(run_worker())