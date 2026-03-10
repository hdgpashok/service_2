import pytest
from unittest.mock import AsyncMock, Mock

from src.repository.user import UserRepository
from src.models.user import UserModel
from src.models.profile import ProfileModel


@pytest.mark.asyncio
async def test_get_user_success(mock_session, user_id):
    profile = ProfileModel(
        id=user_id,
        nickname="nick"
    )

    expected_user = UserModel(
        id=user_id,
        first_name="Bob",
        last_name="Karl",
        profile=profile
    )

    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = expected_user

    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await UserRepository.select(user_id, mock_session)

    assert result == expected_user
    assert result.first_name == "Bob"
    assert result.last_name == "Karl"
    assert result.profile.nickname == "nick"

    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_not_found(mock_session, user_id):
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = None

    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await UserRepository.select(user_id, mock_session)

    assert result is None
    mock_session.execute.assert_awaited_once()