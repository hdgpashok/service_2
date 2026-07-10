import enum
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base
from sqlalchemy import Enum as SQLEnum


class CompensationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CompensationTask(Base):
    __tablename__ = 'compensation_task'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_type: Mapped[str] = mapped_column(sa.String(50), default='delete_external_user', nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False)
    status: Mapped[CompensationStatus] = mapped_column(
        SQLEnum(CompensationStatus),
        default=CompensationStatus.PENDING,
        nullable=False
    )
