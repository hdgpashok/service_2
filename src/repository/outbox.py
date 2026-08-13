import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import SessionDep
from src.models.outbox import OutboxEvent, OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: OutboxEvent) -> None:
        self.session.add(payload)

    async def get_pending(self, limit: int = 20) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING)
            .order_by(OutboxEvent.created_ad)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_processing(self, event_ids: list[uuid.UUID]) -> None:
        if not event_ids:
            return
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(event_ids))
            .values(status=OutboxStatus.PROCESSING)
        )

    async def mark_sent(self, event_id: uuid.UUID) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(status=OutboxStatus.SENT)
        )

    async def mark_failed(self, event_id: uuid.UUID) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(status=OutboxStatus.FAILED)
        )