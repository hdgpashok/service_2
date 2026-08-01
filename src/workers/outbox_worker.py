import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.kafka_producer import Publisher

from src.db import async_session_maker
from src.repository.outbox import OutboxRepository


class OutboxWorker:
    def __init__(self):
        self.publisher = Publisher()
        self.repo = OutboxRepository()

    async def start(self):
        await self.publisher.start_producer()

    async def stop(self):
        await self.publisher.stop_producer()

    async def process_batch(self, session: AsyncSession):
        events = await self.repo.get_pending(session)

        if not events:
            return None

        for event in events:
            try:
                await self.publisher.send(
                    topic=event.topic,
                    payload=event.payload,
                    key=str(event.id)
                )

                await self.repo.mark_sent(event.id, session)

            except Exception as e:
                await self.repo.mark_failed(event.id, session)

        await session.commit()

    async def run_worker(self):
        await self.start()
        try:
            while True:
                try:
                    async with async_session_maker() as session:
                        await self.process_batch(session)

                    await asyncio.sleep(5)

                except Exception as e:
                    print(f"[OutboxWorker] loop error: {e}")
                    await asyncio.sleep(2)

        finally:
            await self.stop()


async def main():
    worker = OutboxWorker()
    await worker.run_worker()


if __name__ == '__main__':
    asyncio.run(main())