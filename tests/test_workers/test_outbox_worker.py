import asyncio
import json

import pytest
from sqlalchemy import select, update

from src.models.outbox import OutboxEvent, OutboxStatus
from src.repository.outbox import OutboxRepository
from src.config.config import settings


async def make_pending_event(
        session,
        topic: str,
        payload: dict | None = None,
        attempts: int = 0,
) -> OutboxEvent:
    event = OutboxEvent(
        topic=topic,
        payload=payload or {"hello": "world"},
        status=OutboxStatus.PENDING,
        attempts=attempts,
    )
    repo = OutboxRepository(session)
    await repo.create(event)
    await session.commit()
    await session.refresh(event)
    return event


@pytest.mark.asyncio
async def test_process_batch_sends_message_and_marks_sent(
        outbox_worker, kafka_topic, kafka_consumer, session
):
    event = await make_pending_event(
        session, topic=kafka_topic, payload={"user_id": "123"}
    )

    processed = await outbox_worker.process_batch()
    assert processed == 1

    # событие реально долетело до брокера
    msg = await asyncio.wait_for(kafka_consumer.getone(), timeout=10)
    assert json.loads(msg.value) == {"user_id": "123"}
    assert msg.key == str(event.id).encode()

    # и статус в БД обновлён
    result = await session.execute(
        select(OutboxEvent).where(OutboxEvent.id == event.id)
    )
    updated = result.scalar_one()
    assert updated.status == OutboxStatus.SENT


@pytest.mark.asyncio
async def test_process_batch_returns_zero_when_no_pending_events(outbox_worker):
    processed = await outbox_worker.process_batch()
    assert processed == 0


@pytest.mark.asyncio
async def test_get_pending_skips_events_scheduled_in_future(session, kafka_topic):
    import datetime

    future_event = await make_pending_event(session, topic=kafka_topic)
    await session.execute(
        update(OutboxEvent)
        .where(OutboxEvent.id == future_event.id)
        .values(
            next_attempt_at=datetime.datetime.now(datetime.timezone.utc)
                            + datetime.timedelta(minutes=5)
        )
    )
    await session.commit()

    repo = OutboxRepository(session)
    pending = await repo.get_pending()

    assert future_event.id not in [e.id for e in pending]


@pytest.mark.asyncio
async def test_process_batch_reschedules_on_send_failure(
        outbox_worker, kafka_topic, session, monkeypatch
):
    event = await make_pending_event(session, topic=kafka_topic)

    async def failing_send(*args, **kwargs):
        raise RuntimeError("broker unreachable")

    monkeypatch.setattr(outbox_worker.publisher, "send", failing_send)

    processed = await outbox_worker.process_batch()
    assert processed == 1

    result = await session.execute(
        select(OutboxEvent).where(OutboxEvent.id == event.id)
    )
    updated = result.scalar_one()

    assert updated.status == OutboxStatus.PENDING
    assert updated.attempts == 1
    assert updated.next_attempt_at is not None
    assert updated.last_error is not None


@pytest.mark.asyncio
async def test_process_batch_marks_failed_after_max_retries(
        outbox_worker, kafka_topic, session, monkeypatch
):
    event = await make_pending_event(
        session, topic=kafka_topic, attempts=settings.MAX_RETRIES - 1
    )

    async def failing_send(*args, **kwargs):
        raise RuntimeError("broker unreachable")

    monkeypatch.setattr(outbox_worker.publisher, "send", failing_send)

    processed = await outbox_worker.process_batch()
    assert processed == 1

    result = await session.execute(
        select(OutboxEvent).where(OutboxEvent.id == event.id)
    )
    updated = result.scalar_one()

    assert updated.status == OutboxStatus.FAILED
    assert updated.attempts == settings.MAX_RETRIES
    assert updated.next_attempt_at is None