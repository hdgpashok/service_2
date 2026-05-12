from unittest.mock import AsyncMock, patch
import pytest

from src.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(mock_id, mock_create_user, mock_session):
    mock_client = AsyncMock()
    mock_client.user_post_request = AsyncMock(return_value=None)

    with patch("src.models.user.uuid.uuid4", return_value=mock_id):
        result = await UserService.create_user(
            mock_create_user, mock_session, mock_client
        )

    assert result.id == mock_id
    assert result.first_name == mock_create_user.first_name


@pytest.mark.asyncio
async def test_get_user_success(mock_id, mock_session):
    mock_client = AsyncMock()
    mock_client.user_get_request = AsyncMock(return_value={
        "id": str(mock_id),
        "title": "external_title",
        "profile": {
            "id": str(mock_id),
            "title": "external_title",
            "bio": "external_bio"
        }
    })

    # Мокаем репозиторий
    with patch("src.repository.user.UserRepository.select") as mock_select:
        mock_select.return_value = {
            "id": mock_id,
            "first_name": "internal_first",
            "last_name": "internal_last",
            "profile": {
                "id": mock_id,
                "nickname": "internal_nick"
            }
        }

        result = await UserService.get_user(mock_id, mock_session, mock_client)

    assert result.id == mock_id
    assert result.first_name == "internal_first"
    assert result.last_name == "internal_last"
    assert result.title == "external_title"
    assert result.profile.nickname == "internal_nick"
    assert result.profile.title == "external_title"