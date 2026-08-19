import uuid

from src.config.config import settings
from src.models.outbox import OutboxEvent, OutboxStatus
from src.models.authors import AuthorModel
from src.models.books import BookModel
from src.schemas.author import AuthorCreate, AuthorResponse


class AuthorMapper:
    @staticmethod
    def schema_to_model(data: AuthorCreate):
        return AuthorModel(
            id=uuid.uuid4(),
            **data.model_dump(exclude={'books'}),
            books=[BookModel(**book.model_dump()) for book in data.books]
        )

    @staticmethod
    def author_create_to_outbox(data: AuthorModel) -> OutboxEvent:
        author_schema = AuthorResponse.model_validate(data)

        return OutboxEvent(
            topic=settings.KAFKA_TOPIC,
            payload=author_schema.model_dump(mode='json'),
            status=OutboxStatus.PENDING
        )