import asyncio
from uuid import UUID

from src.utils.kafka_producer import Publisher
from src.db import async_session_maker
from src.repository.outbox import OutboxRepository
from src.utils.logger import get_logger

logger = get_logger("outbox_worker")


class OutboxWorker:
    def __init__(self) -> None:
        self.publisher = Publisher()

    async def start(self) -> None:
        await self.publisher.start_producer()
        logger.info("[OutboxWorker] started")

    async def stop(self) -> None:
        await self.publisher.stop_producer()
        logger.info("[OutboxWorker] stopped")

    async def claim_events(self, limit: int = 20):
        async with async_session_maker() as session:
            repo = OutboxRepository(session)

            events = await repo.get_pending(limit=limit)

            await repo.mark_processing([event.id for event in events])
            await session.commit()
            return events

    async def mark_result(self, event_id: UUID, success: bool) -> None:
        async with async_session_maker() as session:
            repo = OutboxRepository(session)
            if success:
                await repo.mark_sent(event_id)
            else:
                await repo.mark_failed(event_id)
            await session.commit()

    async def process_batch(self) -> int:
        events = await self.claim_events()
        if not events:
            return 0

        for event in events:
            try:
                await self.publisher.send(
                    topic=event.topic,
                    payload=event.payload,
                    key=str(event.id),
                )
                await self.mark_result(event.id, success=True)
                logger.info(f"[OutboxWorker] sent id={event.id} topic={event.topic}")
            except Exception as e:
                await self.mark_result(event.id, success=False)
                logger.exception(f"[OutboxWorker] failed id={event.id}: {e}")

        return len(events)

    async def run_worker(self) -> None:
        await self.start()
        try:
            while True:
                try:
                    processed = await self.process_batch()
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