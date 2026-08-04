import pytest
from sqlalchemy import select

from src.models.outbox import TransactionalOutbox, OutboxStatus


@pytest.mark.asyncio
async def test_route_create_user(api_client, user_create_payload, session):
    response = await api_client.post(
        "/api/v1/users_profiles/users",
        json=user_create_payload,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["first_name"] == "Ivan"
    assert data["last_name"] == "Ivanov"
    assert data["title"] == "developer"
    assert data["profile"]["nickname"] == "ivan"
    assert data["profile"]["title"] == "profile_title"


@pytest.mark.asyncio
async def test_route_create_user_writes_outbox(api_client, user_create_payload, session):
    response = await api_client.post(
        "/api/v1/users_profiles/users",
        json=user_create_payload,
    )
    assert response.status_code == 201

    rows = await session.execute(select(TransactionalOutbox))
    events = list(rows.scalars().all())

    assert len(events) == 1
    assert events[0].status == OutboxStatus.PENDING
    assert events[0].payload["title"] == "developer"


@pytest.mark.asyncio
async def test_route_get_user(api_client, user_create_payload, session, wiremock_stub):
    create_resp = await api_client.post(
        "/api/v1/users_profiles/users",
        json=user_create_payload,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]
    profile_id = create_resp.json()["profile"]["id"]

    await wiremock_stub(
        endpoint=f"/api/v1/users_profiles/users/{user_id}",
        method="GET",
        response_json={
            "id": user_id,
            "title": "developer",
            "profile": {
                "id": profile_id,
                "title": "profile_title",
                "bio": "bio",
            },
        },
        status=200,
    )

    response = await api_client.get(f"/api/v1/users_profiles/users/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["first_name"] == "Ivan"
    assert data["title"] == "developer"
    assert data["profile"]["nickname"] == "ivan"
    assert data["profile"]["title"] == "profile_title"


@pytest.mark.asyncio
async def test_route_get_user_not_found(api_client, mock_id):
    response = await api_client.get(f"/api/v1/users_profiles/users/{mock_id}")
    assert response.status_code == 404