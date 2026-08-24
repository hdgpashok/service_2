import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.config import settings
from src.models.outbox import OutboxEvent, OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: OutboxEvent) -> None:
        self.session.add(payload)

    async def get_pending(self, limit: int = 20) -> list[OutboxEvent]:
        now = datetime.now(timezone.utc)

        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status.in_([OutboxStatus.PENDING, OutboxStatus.PROCESSING]),
                or_(
                    OutboxEvent.next_attempt_at.is_(None),
                    OutboxEvent.next_attempt_at <= now,
                    ),
            )
            .order_by(OutboxEvent.created_ad)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_processing(self, event_ids: list[uuid.UUID]) -> dict[uuid.UUID, uuid.UUID]:
        if not event_ids:
            return {}

        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(event_ids))
            .values(
                status=OutboxStatus.PROCESSING,
                next_attempt_at=now + timedelta(minutes=settings.PROCESSING_TIMEOUT),
                processing_token=func.gen_random_uuid(),
            )
            .returning(OutboxEvent.id, OutboxEvent.processing_token)
        )
        return {row.id: row.processing_token for row in result}

    async def mark_sent(self, event_id: uuid.UUID, processing_token: uuid.UUID) -> None:
        result = await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id,
                   OutboxEvent.processing_token == processing_token
                   )
            .values(
                status=OutboxStatus.SENT,
                processing_token=None
            )
        )
        return result.rowcount > 0

    async def mark_failed(self, event_id: uuid.UUID, processing_token: uuid.UUID) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id,
                   OutboxEvent.processing_token == processing_token
                   )
            .values(status=OutboxStatus.FAILED)
        )

    async def reschedule(self, event_id: uuid.UUID, next_attempt_at: datetime, processing_token: uuid.UUID):
        await self.session.execute(
            update(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.processing_token == processing_token,
                )
            .values(status=OutboxStatus.PENDING, next_attempt_at=next_attempt_at)
        )

    async def increment_attempts(self, event_id: uuid.UUID, error: str, processing_token: uuid.UUID) -> int | None:
        result = await self.session.execute(
            update(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.processing_token == processing_token,
                )
            .values(attempts=OutboxEvent.attempts + 1, last_error=error[:500])
            .returning(OutboxEvent.attempts)
        )
        return result.scalar_one_or_none()