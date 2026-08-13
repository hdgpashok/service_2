import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.not_found import ObjectNotFound

from src.models.books import BookModel
from src.models.authors import AuthorModel

from src.schemas.author import AuthorOut, AuthorCreate
from src.repository.author import AuthorRepository


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

        return await repo.create(new_author)
