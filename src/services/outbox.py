from sqlalchemy.ext.asyncio import AsyncSession

from src.mappers.author_mapper import AuthorMapper
from src.models.authors import AuthorModel
from src.repository.outbox import OutboxRepository


class OutboxService:
    def __init__(self, session: AsyncSession):
        self.repo = OutboxRepository(session)

    async def create_event(self, author: AuthorModel):
        outbox_author = AuthorMapper.author_create_to_outbox(author)
        await self.repo.create(outbox_author)