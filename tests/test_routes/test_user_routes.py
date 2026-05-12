from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_user_route_post(mock_id, mock_create_user, mock_client, wiremock_setup):
    await wiremock_setup(
        endpoint="/users",
        method="POST",
        response_json={"id": str(mock_id), "status": "success"},
        status=201
    )

    with patch("src.models.user.uuid.uuid4", return_value=mock_id):
        response = await mock_client.post(
            "/users",
            json=mock_create_user.model_dump()
        )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(mock_id)
    assert data["first_name"] == mock_create_user.first_name


@pytest.mark.asyncio
async def test_user_route_get(mock_id, mock_client, wiremock_setup, mock_session):
    # Создаём пользователя в тестовой БД
    from src.models.user import UserModel
    from src.models.profile import ProfileModel

    new_user = UserModel(
        id=mock_id,
        first_name="internal_first",
        last_name="internal_last"
    )
    new_profile = ProfileModel(
        id=mock_id,
        user_id=mock_id,
        nickname="internal_nick"
    )

    mock_session.add(new_user)
    mock_session.add(new_profile)
    await mock_session.commit()

    # Настраиваем WireMock
    await wiremock_setup(
        endpoint=f"/users/{mock_id}",
        method="GET",
        response_json={
            "id": str(mock_id),
            "title": "external_title",
            "profile": {
                "id": str(mock_id),
                "title": "external_title",
                "bio": "external_bio"
            }
        },
        status=200
    )

    response = await mock_client.get(f"/users/{mock_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(mock_id)
    assert data["first_name"] == "internal_first"
    assert data["profile"]["nickname"] == "internal_nick"
    assert data["profile"]["title"] == "external_title"
    assert data["profile"]["bio"] == "external_bio"