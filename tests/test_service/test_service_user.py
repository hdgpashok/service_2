from unittest.mock import patch, AsyncMock

import pytest

from src.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(mock_id, mock_create_user, mock_session):
    with patch('src.services.user.api.user_post_request') as mock_post, \
            patch('src.models.user.uuid.uuid4', return_value=mock_id):

        mock_post.return_value = None

        result = await UserService.create_user(mock_create_user, mock_session)

    assert result.id == mock_id
    assert result.first_name == mock_create_user.first_name
    assert result.last_name == mock_create_user.last_name
    assert result.title == mock_create_user.title

    assert result.profile.id == mock_id
    assert result.profile.title == mock_create_user.profile.title
    assert result.profile.bio == mock_create_user.profile.bio


@pytest.mark.asyncio
async def test_get_user_success(mock_id, mock_session):

    with patch(
            "src.services.user.UserRepository.select",
            new_callable=AsyncMock
    ) as mock_select, patch(
        "src.services.user.api.user_get_request",
        new_callable=AsyncMock
    ) as mock_get:

        mock_select.return_value = {
            "id": mock_id,
            "first_name": "internal_name",
            "last_name": "internal_last",
            "profile": {
                "id": mock_id,
                "nickname": "internal_nick"
            }
        }

        mock_get.return_value = {
            "id": mock_id,
            "first_name": "external_name",
            "last_name": "external_last",
            "title": "test",
            "profile": {
                "id": mock_id,
                "title": "test",
                "bio": "test"
            }
        }

        result = await UserService.get_user(mock_id, mock_session)

    assert result.id == mock_id
    assert result.first_name == "external_name"
    assert result.last_name == "external_last"
    assert result.title == "test"

    assert result.profile.id == mock_id
    assert result.profile.title == "test"
    assert result.profile.bio == "test"
    assert result.profile.nickname == "internal_nick"