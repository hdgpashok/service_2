from src.schemas.user import UserCreate
from src.models.outbox import TransactionalOutbox, OutboxStatus
from src.utils.config import settings


def user_create_to_outbox(user_data: UserCreate) -> TransactionalOutbox:
    return TransactionalOutbox(
        topic=settings.KAFKA_TOPIC,
        payload=user_data.model_dump(mode='json'),
        status=OutboxStatus.PENDING
    )