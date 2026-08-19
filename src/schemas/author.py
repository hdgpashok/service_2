from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.book import BookCreate, BookResponse


class AuthorBase(BaseModel):
    first_name: str
    last_name: str


class AuthorCreate(AuthorBase):
    books: list[BookCreate]


class AuthorResponse(AuthorBase):
    id: UUID
    books: list[BookResponse]

    model_config = ConfigDict(from_attributes=True)