import uuid

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class BookModel(Base):
    __tablename__ = 'books'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(sa.String())

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["AuthorModel"] = relationship("AuthorModel", back_populates="books")
