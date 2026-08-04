import pytest
from sqlalchemy import select

from src.models.outbox import TransactionalOutbox, OutboxStatus
from src.exceptions.not_found import ObjectNotFound


@pytest.mark.asyncio
async def test_create_user_success(user_service, user_create_data, session):
    result = await user_service.create_user(user_create_data, session)
    await session.commit()

    assert result.id is not None
    assert result.first_name == "Ivan"
    assert result.last_name == "Ivanov"
    assert result.title == "developer"
    assert result.profile.nickname == "ivan"
    assert result.profile.title == "profile_title"
    assert result.profile.bio == "bio"


@pytest.mark.asyncio
async def test_create_user_writes_outbox(user_service, user_create_data, session):
    result = await user_service.create_user(user_create_data, session)
    await session.commit()

    rows = await session.execute(select(TransactionalOutbox))
    events = list(rows.scalars().all())

    assert len(events) == 1
    event = events[0]

    assert event.status == OutboxStatus.PENDING
    assert event.payload["id"] == str(result.id) or event.payload["id"] == result.id
    assert event.payload["title"] == "developer"
    assert event.payload["profile"]["title"] == "profile_title"
    assert event.payload["profile"]["bio"] == "bio"


@pytest.mark.asyncio
async def test_get_user_success(user_service, user_create_data, session, wiremock_stub, mock_service_url):
    created = await user_service.create_user(user_create_data, session)
    await session.commit()

    await wiremock_stub(
        endpoint=f"/api/v1/users_profiles/users/{created.id}",
        method="GET",
        response_json={
            "id": str(created.id),
            "title": "developer",
            "profile": {
                "id": str(created.profile.id),
                "title": "profile_title",
                "bio": "bio",
            },
        },
        status=200,
    )

    result = await user_service.get_user(created.id, session)

    assert result.id == created.id
    assert result.first_name == "Ivan"
    assert result.last_name == "Ivanov"
    assert result.title == "developer"
    assert result.profile.nickname == "ivan"
    assert result.profile.title == "profile_title"
    assert result.profile.bio == "bio"


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_id, session):
    with pytest.raises(ObjectNotFound):
        await user_service.get_user(mock_id, session)