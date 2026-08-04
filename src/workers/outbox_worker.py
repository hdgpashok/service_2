import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.kafka_producer import Publisher
from src.db import async_session_maker
from src.repository.outbox import OutboxRepository
from src.utils.logger import get_logger

logger = get_logger("outbox_worker")


class OutboxWorker:
    def __init__(self) -> None:
        self.publisher = Publisher()
        self.repo = OutboxRepository()

    async def start(self) -> None:
        await self.publisher.start_producer()
        logger.info("[OutboxWorker] started")

    async def stop(self) -> None:
        await self.publisher.stop_producer()
        logger.info("[OutboxWorker] stopped")

    async def process_batch(self, session: AsyncSession) -> int:
        events = await self.repo.get_pending(session)

        if not events:
            return 0

        for event in events:
            try:
                await self.publisher.send(
                    topic=event.topic,
                    payload=event.payload,
                    key=str(event.id),
                )
                await self.repo.mark_sent(event.id, session)
                logger.info(f"[OutboxWorker] sent id={event.id} topic={event.topic}")

            except Exception as e:
                await self.repo.mark_failed(event.id, session)
                logger.exception(f"[OutboxWorker] failed id={event.id}: {e}")

        await session.commit()
        return len(events)

    async def run_worker(self) -> None:
        await self.start()

        try:
            while True:
                try:
                    async with async_session_maker() as session:
                        processed = await self.process_batch(session)

                    await asyncio.sleep(0.5 if processed else 5)

                except Exception as e:
                    logger.exception(f"[OutboxWorker] loop error: {e}")
                    await asyncio.sleep(2)
        finally:
            await self.stop()


async def main() -> None:
    worker = OutboxWorker()
    await worker.run_worker()


if __name__ == "__main__":
    asyncio.run(main())