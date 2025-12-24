import uuid

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ProfileModel(Base):
    __tablename__ = 'profile'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(sa.String(), nullable=False)
    bio: Mapped[str] = mapped_column(sa.String(), nullable=False)
    nickname: Mapped[str] = mapped_column(sa.String(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))

    user: Mapped["UserModel"] = relationship('UserModel', back_populates='profile')
