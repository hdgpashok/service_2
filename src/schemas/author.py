from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.book import BookCreate, BookOut


class AuthorBase(BaseModel):
    first_name: str
    last_name: str


class AuthorCreate(AuthorBase):
    books: list[BookCreate]


class AuthorOut(AuthorBase):
    id: UUID
    books: list[BookOut]

    model_config = ConfigDict(from_attributes=True)