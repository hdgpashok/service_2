from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.outbox import OutboxRepository


class OutboxRepositoryFactory:
    def __init__(self, session_maker: Callable[[], AsyncSession]):
        self._session_maker = session_maker

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[OutboxRepository]:
        async with self._session_maker() as session:
            yield OutboxRepository(session)