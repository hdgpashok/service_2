import pytest
from unittest.mock import patch, AsyncMock

from src.application import get_app
from src.services.user import UserService


app = get_app()


@pytest.mark.asyncio
async def test_create_user_success(client_override, user_create_data, user_out, mock_session):
    with patch.object(UserService, 'create_user', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = user_out

        response = client_override.post("/api/v1/users_profiles/users", json=user_create_data.model_dump())

        assert response.status_code == 201
        data = response.json()
        assert data['id'] == str(user_out.id)
        assert data['first_name'] == user_out.first_name
        assert data['last_name'] == user_out.last_name
        assert data['profile']['id'] == str(user_out.profile.id)
        assert data['profile']['nickname'] == user_out.profile.nickname

        mock_create.assert_awaited_once()
        args, _ = mock_create.await_args
        assert args[0].model_dump() == user_create_data.model_dump()
        assert args[1] == mock_session


@pytest.mark.asyncio
async def test_get_user_success(client_override, user_id, user_out, mock_session):
    with patch.object(UserService, 'get_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user_out

        response = client_override.get(f"/api/v1/users_profiles/users?user_id={user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == str(user_out.id)
        assert data['first_name'] == user_out.first_name
        assert data['last_name'] == user_out.last_name

        mock_get.assert_awaited_once_with(user_id, mock_session)