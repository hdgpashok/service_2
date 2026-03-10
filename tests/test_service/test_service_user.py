import uuid
import pytest

from src.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(
        mock_session,
        user_id,
        profile_id,
        user_create_data,
        user_model,
        mock_user_repository,
        mock_api_client,
        mock_client_class
):
    mock_user_repository.select.return_value = user_model

    result = await UserService.create_user(user_create_data, mock_session)

    assert isinstance(result.id, uuid.UUID)
    assert result.first_name == user_create_data.first_name
    assert result.last_name == user_create_data.last_name
    assert result.profile.nickname == user_create_data.profile.nickname
    assert result.profile.title == user_create_data.profile.title
    assert result.profile.bio == user_create_data.profile.bio

    mock_api_client.user_post_request.assert_awaited_once()
    call_args = mock_api_client.user_post_request.call_args[0][0]
    assert isinstance(call_args.id, uuid.UUID)
    assert isinstance(call_args.profile.id, uuid.UUID)

    mock_user_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_success(
        mock_session,
        user_id,
        user_model,
        profile_model,
        external_user_data,
        mock_user_repository,
        mock_profile_repository,
        mock_api_client
):
    mock_user_repository.select.return_value = user_model
    mock_api_client.user_get_request.return_value = external_user_data
    mock_profile_repository.select.return_value = profile_model

    result = await UserService.get_user(user_id, mock_session)

    assert result.id == user_id
    assert result.first_name == user_model.first_name
    assert result.last_name == user_model.last_name
    assert result.profile.id == profile_model.id
    assert result.profile.nickname == profile_model.nickname

    assert result.title == external_user_data['title']
    assert result.profile.title == external_user_data['profile']['title']
    assert result.profile.bio == external_user_data['profile']['bio']

    mock_user_repository.select.assert_awaited_once_with(user_id, mock_session)
    mock_api_client.user_get_request.assert_awaited_once_with(user_id)
    mock_profile_repository.select.assert_awaited_once_with(
        external_user_data['profile']['id'],
        mock_session
    )

