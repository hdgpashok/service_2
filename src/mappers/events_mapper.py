from src.models.outbox import OutboxEvent
from src.schemas.claim_event import ClaimEventSchema


def to_claimed_event(event: OutboxEvent, token: str) -> ClaimEventSchema:
    return ClaimEventSchema(
        id=event.id,
        topic=event.topic,
        payload=event.payload,
        processing_token=token,
    )