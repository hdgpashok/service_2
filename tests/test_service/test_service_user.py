from unittest.mock import patch, AsyncMock

import pytest

from src.services.user import UserService
from src.services.call_api import Client


@pytest.mark.asyncio
async def test_create_user_success(mock_id, mock_create_user, mock_session):
    mock_client = AsyncMock(spec=Client)
    mock_client.user_post_request = AsyncMock(return_value=None)
    mock_client.user_delete_request = AsyncMock(return_value=None)

    with patch('src.models.user.uuid.uuid4', return_value=mock_id):

        result = await UserService.create_user(
            mock_create_user,
            mock_session,
            mock_client
        )

    assert result.id == mock_id
    assert result.first_name == mock_create_user.first_name
    assert result.last_name == mock_create_user.last_name
    assert result.title == mock_create_user.title

    assert result.profile.id == mock_id
    assert result.profile.title == mock_create_user.profile.title
    assert result.profile.bio == mock_create_user.profile.bio


@pytest.mark.asyncio
async def test_get_user_success(mock_id, mock_session):
    mock_client = AsyncMock(spec=Client)
    mock_client.user_get_request = AsyncMock(return_value={
        "id": mock_id,
        "first_name": "external_name",
        "last_name": "external_last",
        "title": "test",
        "profile": {
            "id": mock_id,
            "title": "test",
            "bio": "test"
        }
    })

    mock_select = AsyncMock(return_value={
        "id": mock_id,
        "first_name": "internal_name",
        "last_name": "internal_last",
        "profile": {
            "id": mock_id,
            "nickname": "internal_nick"
        }
    })

    with patch("src.repository.user.UserRepository.select", mock_select):

        result = await UserService.get_user(
            mock_id,
            mock_session,
            mock_client
        )

    assert result.id == mock_id
    assert result.first_name == "external_name"
    assert result.last_name == "external_last"
    assert result.title == "test"

    assert result.profile.id == mock_id
    assert result.profile.title == "test"
    assert result.profile.bio == "test"
    assert result.profile.nickname == "internal_nick"