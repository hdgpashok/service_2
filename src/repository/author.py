from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.schemas.author import AuthorResponse
from src.models.authors import AuthorModel


class AuthorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def select(self, author_id: UUID) -> AuthorModel | None:
        query = (
            select(AuthorModel)
            .where(AuthorModel.id == author_id)
            .options(selectinload(AuthorModel.books))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create(self, author: AuthorModel):
        self.session.add(author)

        await self.session.flush()
        return author
