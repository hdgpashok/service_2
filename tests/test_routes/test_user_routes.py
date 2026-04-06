import pytest

from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_user_route_post(mock_id, mock_create_user, mock_client):
    with patch("src.services.user.api.user_post_request", new_callable=AsyncMock) as mock_post, \
            patch("src.services.user.UserRepository.create", new_callable=AsyncMock) as mock_create, \
            patch("src.services.user.uuid.uuid4", return_value=mock_id):

        mock_post.return_value = None
        mock_create.return_value = None

        response = await mock_client.post(
            "/users",
            json=mock_create_user.model_dump()
        )

        assert response.status_code == 201

        data = response.json()

        print(data)
        assert data['id'] == str(mock_id)
        assert data['first_name'] == mock_create_user.first_name
        assert data['last_name'] == mock_create_user.last_name

        assert data['profile']['id'] == str(mock_id)
        assert data['profile']['nickname'] == mock_create_user.profile.nickname


@pytest.mark.asyncio
async def test_user_route_get(mock_id, mock_client):
    external_response = {
        "id": mock_id,
        "first_name": "external_name",
        "last_name": "external_last",
        "title": "external_title",
        "profile": {
            "id": mock_id,
            "title": "external_profile_title",
            "bio": "external_bio"
        }
    }

    internal_user = {
        "id": mock_id,
        "first_name": "internal_name",
        "last_name": "internal_last",
        "profile": {
            "id": mock_id,
            "nickname": "internal_nick"
        }
    }

    with patch(
            "src.services.user.UserRepository.select",
            new_callable=AsyncMock
    ) as mock_select, patch(
        "src.services.user.api.user_get_request",
        new_callable=AsyncMock
    ) as mock_get:

        mock_select.return_value = internal_user
        mock_get.return_value = external_response

        response = await mock_client.get(f"/users/{mock_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(mock_id)
    assert data["first_name"] == "external_name"
    assert data["last_name"] == "external_last"

    assert data["profile"]["id"] == str(mock_id)
    assert data["profile"]["nickname"] == "internal_nick"