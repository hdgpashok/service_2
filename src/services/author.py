from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.not_found import ObjectNotFound

from src.schemas.author import AuthorResponse, AuthorCreate
from src.repository.author import AuthorRepository
from src.repository.outbox import OutboxRepository

from src.mappers.author_mapper import AuthorMapper


class AuthorService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_author(self, author_id: UUID) -> AuthorResponse:
        repo = AuthorRepository(self.session)

        author = await repo.select(author_id)

        if not author:
            raise ObjectNotFound(object_id=author_id)

        return AuthorResponse.model_validate(author)

    async def create_author(self, author: AuthorCreate) -> AuthorResponse:
        new_author = AuthorMapper.schema_to_model(author)

        repo = AuthorRepository(self.session)
        outbox_repo = OutboxRepository(self.session)

        res = await repo.create(new_author)
        outbox_author = AuthorMapper.author_create_to_outbox(new_author)
        await outbox_repo.create(outbox_author)

        return AuthorResponse.model_validate(res)
