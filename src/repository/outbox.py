from sqlalchemy.ext.asyncio import AsyncSession
from src.models.outbox import TransactionalOutbox


class OutboxRepository:
    @staticmethod
    async def create(payload: TransactionalOutbox, session: AsyncSession):
        session.add(payload)
