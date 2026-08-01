import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import TransactionalOutbox, OutboxStatus


class OutboxRepository:

    @staticmethod
    async def create(payload: TransactionalOutbox, session: AsyncSession) -> None:
        session.add(payload)

    @staticmethod
    async def get_pending(session: AsyncSession, limit: int = 20) -> list[TransactionalOutbox]:
        stmt = (
            select(TransactionalOutbox)
            .where(TransactionalOutbox.status == OutboxStatus.PENDING)
            .order_by(TransactionalOutbox.created_ad)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def mark_sent(event_id: uuid.UUID, session: AsyncSession) -> None:
        await session.execute(
            update(TransactionalOutbox)
            .where(TransactionalOutbox.id == event_id)
            .values(status=OutboxStatus.SENT)
        )

    @staticmethod
    async def mark_failed(event_id: uuid.UUID, session: AsyncSession) -> None:
        await session.execute(
            update(TransactionalOutbox)
            .where(TransactionalOutbox.id == event_id)
            .values(status=OutboxStatus.FAILED)
        )