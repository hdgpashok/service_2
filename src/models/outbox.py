import datetime
import enum
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from src.models.base import Base
from sqlalchemy import Enum as SQLEnum, func


class OutboxStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class TransactionalOutbox(Base):
    __tablename__ = 'transactional_outbox'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(sa.String(), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(
        SQLEnum(OutboxStatus),
        default=OutboxStatus.PENDING,
        nullable=False
    )
    created_ad: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True), server_default=func.now())
