from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from services.outbox import OutboxService
from src.exceptions.not_found import ObjectNotFound

from src.schemas.author import AuthorResponse, AuthorCreate
from src.repository.author import AuthorRepository

from src.mappers.author_mapper import AuthorMapper


class AuthorService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthorRepository(session)
        self.outbox_service = OutboxService(session)

    async def get_author(self, author_id: UUID) -> AuthorResponse:

        author = await self.repo.select(author_id)

        if not author:
            raise ObjectNotFound(object_id=author_id)

        return AuthorResponse.model_validate(author)

    async def create_author(self, author: AuthorCreate) -> AuthorResponse:
        new_author = AuthorMapper.schema_to_model(author)

        res = await self.repo.create(new_author)
        await self.outbox_service.create_event(new_author)

        return AuthorResponse.model_validate(res)
