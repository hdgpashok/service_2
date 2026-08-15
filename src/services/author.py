import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.not_found import ObjectNotFound

from src.models.books import BookModel
from src.models.authors import AuthorModel

from src.schemas.author import AuthorOut, AuthorCreate
from src.repository.author import AuthorRepository
from src.repository.outbox import OutboxRepository

from src.utils.author_to_outbox import author_create_to_outbox


class AuthorService:

    @staticmethod
    async def get_author(author_id: UUID, session: AsyncSession) -> AuthorOut:
        repo = AuthorRepository(session)

        author = await repo.select(author_id)

        if not author:
            raise ObjectNotFound(object_id=author_id)

        return AuthorOut.model_validate(author)

    @staticmethod
    async def create_author(author: AuthorCreate, session: AsyncSession) -> AuthorOut:
        new_author = AuthorModel(
            id=uuid.uuid4(),
            **author.model_dump(exclude={'books'}),
            books=[BookModel(**book.model_dump()) for book in author.books]
        )

        repo = AuthorRepository(session)
        outbox_repo = OutboxRepository(session)

        res = await repo.create(new_author)
        outbox_author = author_create_to_outbox(new_author)
        await outbox_repo.create(outbox_author)

        return res
