import pytest

from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_user_route_post(mock_id, mock_create_user, mock_client):
    with patch("src.services.call_api.ClientMainService.user_post_request", new_callable=AsyncMock) as mock_post, \
            patch("src.repository.user.UserRepository.create", new_callable=AsyncMock) as mock_create, \
            patch("src.services.user.uuid.uuid4", return_value=mock_id):

        mock_post.return_value = None
        mock_create.return_value = None

        response = await mock_client.post(
            "/users",
            json=mock_create_user.model_dump()
        )

        assert response.status_code == 201

        data = response.json()
        assert data['id'] == str(mock_id)
        assert data['first_name'] == mock_create_user.first_name
        assert data['last_name'] == mock_create_user.last_name
        assert data['profile']['id'] == str(mock_id)
        assert data['profile']['nickname'] == mock_create_user.profile.nickname


@pytest.mark.asyncio
async def test_user_route_get(mock_id, mock_client, mock_client_get):
    internal_user = {
        "first_name": "string",
        "last_name": "string",
        "id": mock_id,
        "profile": {
            "nickname": "string",
            "id": str(mock_id)
        }
    }

    with patch(
            "src.repository.user.UserRepository.select",
            new_callable=AsyncMock
    ) as mock_select, patch(
        "src.services.call_api.ClientMainService.user_get_request",
        new_callable=AsyncMock
    ) as mock_external:

        mock_select.return_value = internal_user
        mock_external.return_value = mock_client_get

        response = await mock_client.get(f"/users/{mock_id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(mock_id)
        assert data["first_name"] == "string"
        assert data["last_name"] == "string"

        profile = data["profile"]
        assert profile["id"] == str(mock_id)
        assert profile["nickname"] == "string"
        assert profile["title"] == "string"
        assert profile["bio"] == "string"
