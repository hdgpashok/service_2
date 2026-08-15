from src.schemas.author import AuthorOut
from src.models.authors import AuthorModel
from src.models.outbox import OutboxEvent, OutboxStatus
from src.utils.config import settings


def author_create_to_outbox(author_data: AuthorModel) -> OutboxEvent:
    author_schema = AuthorOut.model_validate(author_data)

    return OutboxEvent(
        topic=settings.KAFKA_TOPIC,
        payload=author_schema.model_dump(mode='json'),
        status=OutboxStatus.PENDING
    )