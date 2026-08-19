import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.config.kafka_producer import KafkaProducer
from src.config.config import settings
from src.models.outbox import OutboxStatus
from src.db import async_session_maker
from src.repository.outbox import OutboxRepository
from src.utils.logger import get_logger

logger = get_logger("outbox_worker")


class OutboxWorker:
    def __init__(self) -> None:
        self.publisher = KafkaProducer()

    async def start(self) -> None:
        await self.publisher.start_producer()
        logger.info("[OutboxWorker] started")

    async def stop(self) -> None:
        await self.publisher.stop_producer()
        logger.info("[OutboxWorker] stopped")

    def decide_retry_outcome(self, attempts: int) -> tuple[OutboxStatus, datetime | None]:
        if attempts >= settings.MAX_RETRIES:
            return OutboxStatus.FAILED, None

        delay = settings.BASE_KAFKA_DELAY * (2 ** (attempts - 1))
        next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        return OutboxStatus.PENDING, next_attempt_at

    async def claim_events(self, limit: int = 20):
        async with async_session_maker() as session:
            repo = OutboxRepository(session)

            events = await repo.get_pending(limit=limit)

            events_ids = [event.id for event in events]
            await repo.mark_processing(events_ids)
            await session.commit()

            return [
                {
                    "id": event.id,
                    "topic": event.topic,
                    "payload": event.payload,
                    "attempts": event.attempts,
                }
                for event in events
            ]

    async def mark_sent(self, event_id: UUID) -> None:
        async with async_session_maker() as session:
            repo = OutboxRepository(session)
            await repo.mark_sent(event_id)
            await session.commit()

    async def mark_failure(self, event_id: UUID, error: str) -> None:
        async with async_session_maker() as session:
            repo = OutboxRepository(session)
            await repo.register_failure(event_id, error, decide=self.decide_retry_outcome)
            await session.commit()
            logger.info(f"[OutboxWorker] id={event_id} failure registered")

    async def process_batch(self) -> int:
        events = await self.claim_events()
        if not events:
            return 0

        for event in events:
            try:
                await self.publisher.send(
                    topic=event["topic"],
                    payload=event["payload"],
                    key=str(event["id"]),
                )
                await self.mark_sent(event["id"])
                logger.info(f"[OutboxWorker] sent id={event['id']} topic={event['topic']}")
            except Exception as e:
                logger.exception(f"[OutboxWorker] failed id={event['id']}: {e}")
                await self.mark_failure(event["id"], event["attempts"], str(e))

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