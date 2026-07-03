import asyncio

from sqlalchemy import select

from src.db import async_session_maker
from src.models.compensation_task import CompensationTask, CompensationStatus
from src.client.client_main_service import ClientUserService
from src.utils.logger import get_logger

logger = get_logger('compensation_worker')


async def process_task(task_id: int):
    client = ClientUserService()

    async with async_session_maker() as session:
        task = await session.get(CompensationTask, task_id)
        if not task:
            return

        try:
            task.status = CompensationStatus.IN_PROGRESS
            await session.commit()

            logger.info(f"Starting compensation for user {task.user_id}")

            await client.user_delete_request(task.user_id)

            # Успех
            task.status = CompensationStatus.COMPLETED
            logger.info(f"✓ Compensation SUCCESS for user {task.user_id}")

        except Exception as exc:
            if "404" in str(exc) or getattr(exc, "status_code", 0) == 404:
                task.status = CompensationStatus.COMPLETED
                logger.info(f"User {task.user_id} already deleted (404)")
            else:
                task.status = CompensationStatus.FAILED
                task.last_error = str(exc)[:500]
                logger.warning(f"Compensation FAILED for user {task.user_id}: {exc}")

        finally:
            await session.commit()


async def run_worker():
    logger.info("Compensation Worker started...")

    while True:
        try:
            async with async_session_maker() as session:
                query = select(CompensationTask.id).where(
                    CompensationTask.status.in_([
                        CompensationStatus.PENDING,
                        CompensationStatus.IN_PROGRESS
                    ])
                ).limit(20)

                result = await session.execute(query)
                task_ids = [row[0] for row in result.all()]

            for task_id in task_ids:
                await process_task(task_id)

        except Exception as exc:
            logger.error(f"Worker loop error: {exc}")

        await asyncio.sleep(15)


if __name__ == '__main__':
    asyncio.run(run_worker())