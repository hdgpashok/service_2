import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.books import BookModel


class AuthorModel(Base):
    __tablename__ = 'authors'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(sa.String())
    last_name: Mapped[str] = mapped_column(sa.String())

    books: Mapped[list['BookModel']] = relationship(
        "BookModel",
        back_populates="author",
        cascade='all, delete-orphan'
    )